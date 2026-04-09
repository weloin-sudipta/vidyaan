import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "routine"
	context.page_title = "Routine"
	context.page_subtitle = "Class routines, slots and period timings"

	context.generations = safe_count("Routine Generation")
	context.slots       = safe_count("Routine Slot")
	context.periods     = safe_count("Period Timing")

	context.recent = safe_get_list(
		"Routine Generation",
		fields=["name", "academic_year", "academic_term", "status"],
		order_by="creation desc",
		limit=20,
	)
