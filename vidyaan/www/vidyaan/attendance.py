import frappe
from frappe.utils import today, add_days
from vidyaan.www.vidyaan._helpers import guard, safe_count, safe_get_list


def get_context(context):
	guard(context)
	context.active_page = "attendance"
	context.page_title = "Attendance"
	context.page_subtitle = "Daily student attendance tracking"

	t = today()
	context.today_present = safe_count("Student Attendance", {"status": "Present", "date": t})
	context.today_absent  = safe_count("Student Attendance", {"status": "Absent",  "date": t})
	context.today_total   = context.today_present + context.today_absent
	context.today_percent = round((context.today_present / context.today_total) * 100, 1) if context.today_total else 0

	# Last 7 days
	context.week = []
	for i in range(6, -1, -1):
		d = add_days(t, -i)
		p = safe_count("Student Attendance", {"status": "Present", "date": d})
		a = safe_count("Student Attendance", {"status": "Absent",  "date": d})
		tot = p + a
		context.week.append({
			"date": d,
			"present": p, "absent": a, "total": tot,
			"percent": round((p / tot) * 100, 1) if tot else 0,
		})

	context.recent = safe_get_list(
		"Student Attendance",
		fields=["name", "student", "student_name", "status", "date", "course_schedule"],
		order_by="date desc, creation desc",
		limit=30,
	)
