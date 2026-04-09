import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "assignments"
	context.page_title = "Assignments"
	context.page_subtitle = "Assignments published and submissions received"

	context.total = safe_count("Assignment")
	context.submissions = safe_count("Assignment Submission")

	context.assignments = safe_get_list(
		"Assignment",
		fields=["name", "title", "course", "due_date", "status"],
		order_by="creation desc",
		limit=40,
	)
