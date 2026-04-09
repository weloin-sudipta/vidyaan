import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "students"
	context.page_title = "Students"
	context.page_subtitle = "All students enrolled in your institute"

	context.total = safe_count("Student")
	context.active = safe_count("Student", {"enabled": 1})
	context.inactive = context.total - context.active

	context.students = safe_get_list(
		"Student",
		fields=["name", "student_name", "student_email_id", "student_mobile_number",
				"joining_date", "gender", "enabled"],
		order_by="creation desc",
		limit=50,
	)
