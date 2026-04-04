import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user


@frappe.whitelist()
def get_my_fee():
    """Get all fee records for the logged-in student."""
    student = _get_student_for_user()
    if not student:
        return []

    fees = frappe.get_all(
        "Fees",
        filters={"student": student.name},
        fields=[
            "name", "student", "student_name", "program",
            "academic_year", "academic_term", "due_date",
            "grand_total", "outstanding_amount", "docstatus",
            "posting_date"
        ],
        order_by="posting_date desc"
    )

    for fee in fees:
        fee["status"] = "Paid" if fee.outstanding_amount == 0 and fee.docstatus == 1 else (
            "Submitted" if fee.docstatus == 1 else "Draft"
        )
        # Get fee components
        components = frappe.get_all(
            "Fee Component",
            filters={"parent": fee.name},
            fields=["fees_category", "amount"]
        )
        fee["components"] = components

    return fees
