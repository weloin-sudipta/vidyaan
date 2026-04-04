import frappe
from frappe.model.document import Document

class Publication(Document):

    def validate(self):
        self.validate_by_type()
        self.validate_approval()

    def validate_by_type(self):
        """Invoke type-specific validation based on Publication Type."""
        TYPE_VALIDATORS = {
            "Notice": self.validate_notice,
            "News": self.validate_news,
            "Announcement": self.validate_announcement
        }

        method = TYPE_VALIDATORS.get(self.type)
        if method:
            method()

    def validate_notice(self):
        """Notices require targeting information."""
        if not self.target_type:
            frappe.throw("Target Type is required for Notice")
        if self.target_type == "Student Group" and not self.target_student_group:
            frappe.throw("Target Student Group is required for Student Group target type")

    def validate_news(self):
        """News publications require a featured image."""
        if not self.featured_image:
            frappe.throw("Featured Image is required for News")

    def validate_announcement(self):
        """Announcements are simpler and don't need extra fields."""
        pass

    def validate_approval(self):
        """Ensure approval fields are set based on selection."""
        if self.approval_type == "By Role" and not self.approver_role:
            frappe.throw("Approver Role is required")

        if self.approval_type == "By User" and not self.approver_user:
            frappe.throw("Approver User is required")

    def on_submit(self):
        """Auto-assign to the approver when the publication is submitted."""
        self.db_set("status", "Pending")

        if self.approval_type == "By User" and self.approver_user:
            frappe.assign_to.add({
                "assign_to": [self.approver_user],
                "doctype": self.doctype,
                "name": self.name,
                "description": f"Please approve the publication: {self.title}"
            })
        elif self.approval_type == "By Role" and self.approver_role:
            # For role-based assignment, find users with that role scoped to this company
            users = frappe.get_all("Has Role", filters={"role": self.approver_role}, pluck="parent")
            if users:
                # Filter to users who have permission for this company (multi-tenant isolation)
                company = frappe.db.get_value("Student Group", self.target_student_group, "company") if self.target_student_group else None
                if company:
                    permitted_users = frappe.get_all(
                        "User Permission",
                        filters={"allow": "Company", "for_value": company, "user": ["in", users]},
                        pluck="user"
                    )
                    # Also include System Managers who have no company restriction
                    system_managers = [u for u in users if "System Manager" in frappe.get_roles(u)]
                    users = list(set(permitted_users + system_managers))

                if users:
                    frappe.assign_to.add({
                        "assign_to": users,
                        "doctype": self.doctype,
                        "name": self.name,
                        "description": f"Action Required: Approve {self.type} - {self.title}"
                    })
