import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "instructors"
	context.page_title = "Instructors"
	context.page_subtitle = "Teaching staff and faculty members"

	context.total = safe_count("Instructor")
	context.instructors = safe_get_list(
		"Instructor",
		fields=["name", "instructor_name", "department", "status", "gender"],
		order_by="creation desc",
		limit=50,
	)
