import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "admissions"
	context.page_title = "Admissions"
	context.page_subtitle = "Student applicants and admission status"

	context.applied  = safe_count("Student Applicant", {"application_status": "Applied"})
	context.approved = safe_count("Student Applicant", {"application_status": "Approved"})
	context.rejected = safe_count("Student Applicant", {"application_status": "Rejected"})

	context.applicants = safe_get_list(
		"Student Applicant",
		fields=["name", "first_name", "last_name", "program", "application_status", "application_date"],
		order_by="creation desc",
		limit=50,
	)
