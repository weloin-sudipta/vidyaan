import frappe
from vidyaan.www.vidyaan._helpers import guard, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "settings"
	context.page_title = "Settings"
	context.page_subtitle = "Vidyaan and Education configuration"

	try:
		context.settings = frappe.get_single("Vidyaan Settings")
	except Exception:
		context.settings = None

	try:
		context.edu_settings = frappe.get_single("Education Settings")
	except Exception:
		context.edu_settings = None

	context.academic_years = safe_get_list("Academic Year", fields=["name", "year_start_date", "year_end_date"], order_by="year_start_date desc", limit=10)
	context.academic_terms = safe_get_list("Academic Term", fields=["name", "academic_year", "term_start_date", "term_end_date"], order_by="term_start_date desc", limit=10)
