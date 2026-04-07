import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate, today


class Assignment(Document):

    def validate(self):
        self._auto_set_instructor()
        self._validate_due_date()
        self._validate_target_groups()

    def before_save(self):
        # When transitioning to Published, stamp published_on once
        if self.status == "Published" and not self.published_on:
            self.published_on = now_datetime()

    def on_trash(self):
        # Block deletion if any submission has already been graded (score is set)
        for row in (self.submissions or []):
            if row.score is not None and row.score != 0:
                frappe.throw(
                    _(
                        "Cannot delete Assignment '{0}': one or more submissions have "
                        "already been graded. Close the assignment instead."
                    ).format(self.title)
                )

    # ── Private helpers ────────────────────────────────────────────────────

    def _auto_set_instructor(self):
        """Resolve the instructor field from the logged-in user when it is blank."""
        if self.instructor:
            return
        try:
            from vidyaan.api_folder.profile import _get_instructor_for_user
            instructor = _get_instructor_for_user()
            if instructor:
                self.instructor = instructor.name
            else:
                frappe.throw(_("No Instructor record found for the current user. "
                               "Please set the Instructor field manually."))
        except ImportError:
            frappe.throw(_("Profile module not available. Set the Instructor field manually."))

    def _validate_due_date(self):
        """On insert, prevent past due dates. Allow on amendments of existing docs."""
        if self.is_new() and self.due_date:
            if getdate(self.due_date) < getdate(today()):
                frappe.throw(_("Due Date cannot be in the past when creating an assignment."))

    def _validate_target_groups(self):
        """When assign_to is Specific Groups, at least one target group must be listed."""
        if self.assign_to == "Specific Groups":
            if not self.target_groups:
                frappe.throw(
                    _("At least one Target Group is required when 'Assign To' is set to 'Specific Groups'.")
                )
