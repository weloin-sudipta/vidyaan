import frappe
from frappe.utils import flt, today, add_days

from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)

	context.active_page = "dashboard"
	context.page_title = "Dashboard"
	context.page_subtitle = "Overview of your institute at a glance"

	# --- KPIs (real DB counts) ---
	context.kpis = [
		{"label": "Students",         "value": safe_count("Student", {"enabled": 1}), "icon": "users",       "tone": ""},
		{"label": "Instructors",      "value": safe_count("Instructor"),              "icon": "user-check",  "tone": "success"},
		{"label": "Programs",         "value": safe_count("Program"),                 "icon": "book-open",   "tone": "violet"},
		{"label": "Courses",          "value": safe_count("Course"),                  "icon": "file-text",   "tone": "teal"},
		{"label": "Open Admissions",  "value": safe_count("Student Applicant", {"application_status": "Applied"}), "icon": "user-plus",   "tone": "warning"},
		{"label": "Assignments",      "value": safe_count("Assignment"),              "icon": "file-text",   "tone": "accent"},
		{"label": "Pending Requests", "value": safe_count("Student Request", {"status": "Pending"}), "icon": "inbox",       "tone": "peach"},
		{"label": "Routine Slots",    "value": safe_count("Routine Slot"),            "icon": "clock",       "tone": ""},
	]

	# --- Recent students ---
	context.recent_students = safe_get_list(
		"Student",
		fields=["name", "student_name", "student_email_id", "joining_date", "enabled"],
		order_by="creation desc",
		limit=6,
	)

	# --- Recent admissions ---
	context.recent_applicants = safe_get_list(
		"Student Applicant",
		fields=["name", "first_name", "last_name", "application_status", "program"],
		order_by="creation desc",
		limit=6,
	)

	# --- Attendance today ---
	present = safe_count("Student Attendance", {"status": "Present", "date": today()})
	absent  = safe_count("Student Attendance", {"status": "Absent",  "date": today()})
	total   = present + absent
	context.attendance_today = {
		"present": present,
		"absent":  absent,
		"total":   total,
		"percent": round((present / total) * 100, 1) if total else 0,
	}

	# --- Fees collected (last 30 days, real query, fall back gracefully) ---
	fees_collected = 0
	try:
		row = frappe.db.sql(
			"""select coalesce(sum(grand_total), 0)
			   from `tabFees`
			   where docstatus = 1 and posting_date >= %s""",
			(add_days(today(), -30),),
		)
		fees_collected = flt(row[0][0]) if row else 0
	except Exception:
		fees_collected = 0
	context.fees_collected_30d = fees_collected
	context.currency = frappe.db.get_default("currency") or ""
