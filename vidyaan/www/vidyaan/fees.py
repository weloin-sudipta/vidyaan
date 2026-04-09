import frappe
from frappe.utils import flt, today, add_days
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "fees"
	context.page_title = "Fees"
	context.page_subtitle = "Fee schedules, invoices and collections"

	context.total_fees = safe_count("Fees")
	context.schedules  = safe_count("Fee Schedule")
	context.structures = safe_count("Fee Structure")
	context.currency   = frappe.db.get_default("currency") or ""

	collected = 0
	outstanding = 0
	try:
		row = frappe.db.sql("""select coalesce(sum(grand_total),0), coalesce(sum(outstanding_amount),0)
			from `tabFees` where docstatus = 1 and posting_date >= %s""",
			(add_days(today(), -30),))
		if row:
			collected = flt(row[0][0])
			outstanding = flt(row[0][1])
	except Exception:
		pass
	context.collected_30d = collected
	context.outstanding   = outstanding

	context.fees = safe_get_list(
		"Fees",
		fields=["name", "student", "student_name", "grand_total", "outstanding_amount",
				"posting_date", "docstatus"],
		order_by="posting_date desc",
		limit=40,
	)
