import frappe
from frappe.model.document import Document
from frappe import _


class StudentNOC(Document):
	def validate(self):
		self.validate_duplicate()

	def validate_duplicate(self):
		if self.is_new():
			existing = frappe.db.exists("Student NOC", {
				"student": self.student,
				"noc_type": self.noc_type,
				"status": ["in", ["Pending", "In Progress", "Pending Review", "Library Clearance", "Accounts Clearance", "Lab Clearance", "Hostel Clearance", "Final Approval"]],
				"docstatus": ["<", 2],
			})
			if existing:
				frappe.throw(
					_("Student {0} already has an active {1} application ({2}).").format(
						self.student_name, self.noc_type, existing
					)
				)

	def before_submit(self):
		self.status = "Pending"

	def on_update(self):
		"""Update status based on workflow state."""
		if self.workflow_state:
			status_map = {
				"Draft": "Draft",
				"Pending Review": "Pending",
				"Library Clearance": "In Progress",
				"Accounts Clearance": "In Progress",
				"Lab Clearance": "In Progress",
				"Hostel Clearance": "In Progress",
				"Final Approval": "In Progress",
				"Approved": "Approved",
				"Rejected": "Rejected",
			}
			if self.workflow_state in status_map:
				current_status = status_map[self.workflow_state]
				if self.status != current_status:
					self.db_set("status", current_status)

			# Set approval details when approved
			if self.workflow_state == "Approved" and not self.approved_by:
				self.db_set("approved_by", frappe.session.user)
				self.db_set("approval_date", frappe.utils.now_datetime())

	def on_cancel(self):
		self.db_set("status", "Cancelled")
