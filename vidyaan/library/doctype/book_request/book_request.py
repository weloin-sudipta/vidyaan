import frappe
from frappe.model.document import Document
from frappe import _


class BookRequest(Document):
	def validate(self):
		if self.status in ["Approved", "Issued"]:
			self.validate_librarian()
		if self.status == "Approved" and not self.assigned_copy:
			self.assign_book_copy()

	def validate_librarian(self):
		library_doc = frappe.get_doc("Library", self.library)
		if library_doc.librarian != frappe.session.user and "System Manager" not in frappe.get_roles():
			frappe.throw(_("Only the librarian of {0} can approve or manage requests.").format(self.library))

	def assign_book_copy(self):
		available_copy = frappe.get_all(
			"Book Copy",
			filters={"book": self.book, "status": "Available"},
			limit=1,
		)
		if not available_copy:
			frappe.throw(_("No valid or available copies found for the selected book."))

		self.assigned_copy = available_copy[0].name

		copy_doc = frappe.get_doc("Book Copy", self.assigned_copy)
		copy_doc.status = "Reserved"
		copy_doc.save(ignore_permissions=True)

	@frappe.whitelist()
	def create_book_issue(self):
		self.validate_librarian()
		if self.status != "Approved":
			frappe.throw(_("Book Request must be Approved to issue a book."))

		if not self.assigned_copy:
			frappe.throw(_("No copy is assigned to this request."))

		library_doc = frappe.get_doc("Library", self.library)
		member_doc = frappe.get_doc("Library Member", self.member)

		if member_doc.current_issued_books >= member_doc.max_books_allowed:
			frappe.throw(_("Member has already reached the maximum allowed books limits."))

		due_date = frappe.utils.add_days(frappe.utils.nowdate(), library_doc.issue_duration_days)

		issue_doc = frappe.get_doc(
			{
				"doctype": "Book Issue",
				"library": self.library,
				"member": self.member,
				"book": self.book,
				"book_copy": self.assigned_copy,
				"issue_date": frappe.utils.nowdate(),
				"due_date": due_date,
				"status": "Issued",
				"book_request": self.name,
			}
		)
		issue_doc.insert()

		self.db_set("status", "Issued")

		return issue_doc.name
