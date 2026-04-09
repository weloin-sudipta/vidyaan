import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "requests"
	context.page_title = "Requests & NOC"
	context.page_subtitle = "Student requests and NOC applications"

	context.total_requests = safe_count("Student Request")
	context.pending = safe_count("Student Request", {"status": "Pending"})
	context.total_noc = safe_count("Student NOC")

	context.requests = safe_get_list(
		"Student Request",
		fields=["name", "student", "student_name", "request_type", "status", "creation"],
		order_by="creation desc",
		limit=30,
	)
	context.nocs = safe_get_list(
		"Student NOC",
		fields=["name", "student", "student_name", "status", "creation"],
		order_by="creation desc",
		limit=20,
	)
