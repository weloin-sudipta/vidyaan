import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now


class StudentRequest(Document):
	def before_submit(self):
		self.status = "Open"

	def on_update_after_submit(self):
		if self.status in ("Resolved", "Closed") and not self.resolution_date:
			self.db_set("resolution_date", now())
			self.db_set("resolved_by", frappe.session.user)
		if self.response and not self.response_date:
			self.db_set("response_date", now())

	def on_cancel(self):
		self.db_set("status", "Closed")
