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
				"status": ["in", ["Pending", "In Progress"]],
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

	def on_cancel(self):
		self.db_set("status", "Cancelled")
