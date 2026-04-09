import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "programs"
	context.page_title = "Programs & Courses"
	context.page_subtitle = "Academic programs and the courses inside them"

	context.total_programs = safe_count("Program")
	context.total_courses = safe_count("Course")
	context.total_topics = safe_count("Topic")

	context.programs = safe_get_list(
		"Program",
		fields=["name", "program_name", "program_code", "department"],
		order_by="creation desc",
		limit=30,
	)
	context.courses = safe_get_list(
		"Course",
		fields=["name", "course_name", "course_code", "department"],
		order_by="creation desc",
		limit=30,
	)
