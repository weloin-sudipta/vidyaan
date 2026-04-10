import frappe
from frappe.model.document import Document
from frappe.desk.form.assign_to import add


class Publication(Document):

    def validate(self):
        self.validate_by_type()
        self.validate_approval()

    # -----------------------------
    # TYPE-BASED VALIDATION
    # -----------------------------
    def validate_by_type(self):
        TYPE_VALIDATORS = {
            "Notice": self.validate_notice,
            "News": self.validate_news,
            "Announcement": self.validate_announcement
        }

        method = TYPE_VALIDATORS.get(self.type)
        if method:
            method()

    def validate_notice(self):
        if not self.target_type:
            frappe.throw("Target Type is required for Notice")

        if self.target_type == "Student Group" and not self.target_student_group:
            frappe.throw("Target Student Group is required for Student Group target type")

    def validate_news(self):
        if not self.featured_image:
            frappe.throw("Featured Image is required for News")

    def validate_announcement(self):
        # No extra validation needed
        pass

    # -----------------------------
    # APPROVAL VALIDATION
    # -----------------------------
    def validate_approval(self):
        if self.approval_type == "By Role" and not self.approver_role:
            frappe.throw("Approver Role is required")

        if self.approval_type == "By User" and not self.approver_user:
            frappe.throw("Approver User is required")

    # -----------------------------
    # SUBMIT LOGIC
    # -----------------------------
    def on_submit(self):
        """Auto-assign to approver when submitted"""

        # Set status to Pending
        self.db_set("status", "Pending")

        # -------------------------
        # USER-BASED APPROVAL
        # -------------------------
        if self.approval_type == "By User" and self.approver_user:
            add({
                "assign_to": [self.approver_user],
                "doctype": self.doctype,
                "name": self.name,
                "description": f"Please approve the publication: {self.title}"
            })

        # -------------------------
        # ROLE-BASED APPROVAL
        # -------------------------
        elif self.approval_type == "By Role" and self.approver_role:

            users = frappe.get_all(
                "Has Role",
                filters={"role": self.approver_role},
                pluck="parent"
            )

            if not users:
                return

            # Get company from Student Group (if applicable)
            company = None
            if self.target_student_group:
                company = frappe.db.get_value(
                    "Student Group",
                    self.target_student_group,
                    "company"
                )

            # Filter users by company permission
            if company:
                permitted_users = frappe.get_all(
                    "User Permission",
                    filters={
                        "allow": "Company",
                        "for_value": company,
                        "user": ["in", users]
                    },
                    pluck="user"
                )

                # Include System Managers (no restriction)
                system_managers = [
                    u for u in users if "System Manager" in frappe.get_roles(u)
                ]

                users = list(set(permitted_users + system_managers))

            # Final assignment
            if users:
                add({
                    "assign_to": users,
                    "doctype": self.doctype,
                    "name": self.name,
                    "description": f"Action Required: Approve {self.type} - {self.title}"
                })