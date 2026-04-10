import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import date_diff, today


class BookIssue(Document):
	def validate(self):
		self.validate_librarian()

	def validate_librarian(self):
		library_doc = frappe.get_doc("Library", self.library)
		if library_doc.librarian != frappe.session.user and "System Manager" not in frappe.get_roles():
			frappe.throw(_("Only the librarian of {0} can manage book issues.").format(self.library))

	def before_save(self):
		if self.is_new():
			member_issued = frappe.db.get_value("Library Member", self.member, "current_issued_books") or 0
			frappe.db.set_value("Library Member", self.member, "current_issued_books", member_issued + 1)
			copy_doc = frappe.get_doc("Book Copy", self.book_copy)
			copy_doc.status = "Issued"
			copy_doc.save(ignore_permissions=True)

			# Auto-link and fulfill pending book requests for this member/book if manually issued
			if not self.book_request:
				pending_request = frappe.db.get_value("Book Request", {"member": self.member, "book": self.book, "status": ["in", ["Pending", "Approved"]]}, "name")
				if pending_request:
					self.book_request = pending_request
					frappe.db.set_value("Book Request", pending_request, "status", "Issued")

		elif self.has_value_changed("status") and self.status == "Returned":
			self.process_return()

	def process_return(self):
		if not self.return_date:
			self.return_date = today()

		member_issued = frappe.db.get_value("Library Member", self.member, "current_issued_books") or 0
		frappe.db.set_value("Library Member", self.member, "current_issued_books", max(0, member_issued - 1))

		library_doc = frappe.get_doc("Library", self.library)
		days_overdue = date_diff(self.return_date, self.due_date)
		if days_overdue > 0:
			self.fine_amount = days_overdue * library_doc.fine_per_day
		else:
			self.fine_amount = 0

		# Sync status back to the linked Book Request
		if self.book_request:
			frappe.db.set_value("Book Request", self.book_request, "status", "Returned")

		self.assign_next_request_if_needed(library_doc)

	def assign_next_request_if_needed(self, library_doc):
		if library_doc.auto_assign_on_return:
			next_request = frappe.get_all(
				"Book Request",
				filters={"book": self.book, "status": "Pending", "library": self.library},
				order_by="priority asc, creation asc",
				limit=1,
			)
			if next_request:
				req_doc = frappe.get_doc("Book Request", next_request[0].name)
				req_doc.status = "Approved"
				req_doc.assigned_copy = self.book_copy
				req_doc.save()
				copy_doc = frappe.get_doc("Book Copy", self.book_copy)
				copy_doc.status = "Reserved"
				copy_doc.save(ignore_permissions=True)
				return

		copy_doc = frappe.get_doc("Book Copy", self.book_copy)
		copy_doc.status = "Available"
		copy_doc.save(ignore_permissions=True)
