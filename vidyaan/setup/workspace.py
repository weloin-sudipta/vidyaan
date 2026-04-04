import frappe
import json


def create_vidyaan_workspace():
	workspace_name = "Vidyaan Dashboard"

	if frappe.db.exists("Workspace", workspace_name):
		return

	content = [
		{"id": "sp1", "type": "spacer", "data": {"col": 12}},
		{"id": "hdr_shortcuts", "type": "header", "data": {"text": '<span class="h4"><b>Your Shortcuts</b></span>', "col": 12}},
		{"id": "sc_student", "type": "shortcut", "data": {"shortcut_name": "Student", "col": 3}},
		{"id": "sc_instructor", "type": "shortcut", "data": {"shortcut_name": "Instructor", "col": 3}},
		{"id": "sc_program", "type": "shortcut", "data": {"shortcut_name": "Program", "col": 3}},
		{"id": "sc_course", "type": "shortcut", "data": {"shortcut_name": "Course", "col": 3}},
		{"id": "sc_attendance_sheet", "type": "shortcut", "data": {"shortcut_name": "Student Monthly Attendance Sheet", "col": 3}},
		{"id": "sc_scheduling_tool", "type": "shortcut", "data": {"shortcut_name": "Course Scheduling Tool", "col": 3}},
		{"id": "sc_attendance_tool", "type": "shortcut", "data": {"shortcut_name": "Student Attendance Tool", "col": 3}},
		{"id": "sc_routine", "type": "shortcut", "data": {"shortcut_name": "Routine Generation", "col": 3}},
		{"id": "sp2", "type": "spacer", "data": {"col": 12}},
		{"id": "hdr_masters", "type": "header", "data": {"text": '<span class="h4"><b>Reports & Masters</b></span>', "col": 12}},
		{"id": "cd_student", "type": "card", "data": {"card_name": "Student and Instructor", "col": 4}},
		{"id": "cd_masters", "type": "card", "data": {"card_name": "Masters", "col": 4}},
		{"id": "cd_content", "type": "card", "data": {"card_name": "Content Masters", "col": 4}},
		{"id": "cd_settings", "type": "card", "data": {"card_name": "Settings", "col": 4}},
		{"id": "cd_admission", "type": "card", "data": {"card_name": "Admission", "col": 4}},
		{"id": "cd_fees", "type": "card", "data": {"card_name": "Fees", "col": 4}},
		{"id": "cd_schedule", "type": "card", "data": {"card_name": "Schedule", "col": 4}},
		{"id": "cd_attendance", "type": "card", "data": {"card_name": "Attendance", "col": 4}},
		{"id": "cd_assessment", "type": "card", "data": {"card_name": "Assessment", "col": 4}},
		{"id": "cd_assess_rpt", "type": "card", "data": {"card_name": "Assessment Reports", "col": 4}},
		{"id": "cd_tools", "type": "card", "data": {"card_name": "Tools", "col": 4}},
		{"id": "cd_other", "type": "card", "data": {"card_name": "Other Reports", "col": 4}},
	]

	shortcuts = [
		{"label": "Student", "link_to": "Student", "type": "DocType", "color": "Grey", "format": "{} Active", "stats_filter": '{"enabled": 1}'},
		{"label": "Instructor", "link_to": "Instructor", "type": "DocType", "color": "Grey", "format": "{} Active", "stats_filter": '{"status": "Active"}'},
		{"label": "Program", "link_to": "Program", "type": "DocType"},
		{"label": "Course", "link_to": "Course", "type": "DocType"},
		{"label": "Student Monthly Attendance Sheet", "link_to": "Student Monthly Attendance Sheet", "type": "Report"},
		{"label": "Course Scheduling Tool", "link_to": "Course Scheduling Tool", "type": "DocType"},
		{"label": "Student Attendance Tool", "link_to": "Student Attendance Tool", "type": "DocType"},
		{"label": "Routine Generation", "link_to": "Routine Generation", "type": "DocType"},
	]

	links = [
		# Student and Instructor
		_card_break("Student and Instructor"),
		_link("Student", "Student", onboard=1),
		_link("Instructor", "Instructor", onboard=1),
		_link("Guardian", "Guardian"),
		_link("Student Group", "Student Group"),
		_link("Student Log", "Student Log"),

		# Masters
		_card_break("Masters"),
		_link("Program", "Program"),
		_link("Course", "Course", onboard=1),
		_link("Topic", "Topic"),
		_link("Room", "Room", onboard=1),

		# Content Masters
		_card_break("Content Masters"),
		_link("Article", "Article"),
		_link("Video", "Video"),
		_link("Quiz", "Quiz"),

		# Settings
		_card_break("Settings"),
		_link("Education Settings", "Education Settings"),
		_link("Vidyaan Settings", "Vidyaan Settings"),
		_link("Student Category", "Student Category"),
		_link("Student Batch Name", "Student Batch Name"),
		_link("Grading Scale", "Grading Scale", onboard=1),
		_link("Academic Term", "Academic Term"),
		_link("Academic Year", "Academic Year"),

		# Admission
		_card_break("Admission"),
		_link("Student Applicant", "Student Applicant"),
		_link("Student Admission", "Student Admission"),
		_link("Program Enrollment", "Program Enrollment"),
		_link("Course Enrollment", "Course Enrollment"),

		# Fees
		_card_break("Fees"),
		_link("Fee Structure", "Fee Structure"),
		_link("Fee Category", "Fee Category"),
		_link("Fee Schedule", "Fee Schedule"),
		_link("Fees", "Fees"),
		_link("Student Fee Collection Report", "Student Fee Collection", link_type="Report", is_query_report=1, dependencies="Fees"),
		_link("Program wise Fee Collection Report", "Program wise Fee Collection", link_type="Report", is_query_report=1, dependencies="Fees"),

		# Schedule
		_card_break("Schedule"),
		_link("Course Schedule", "Course Schedule"),
		_link("Course Scheduling Tool", "Course Scheduling Tool"),
		_link("Routine Generation", "Routine Generation"),

		# Attendance
		_card_break("Attendance"),
		_link("Student Attendance", "Student Attendance"),
		_link("Student Leave Application", "Student Leave Application"),
		_link("Student Monthly Attendance Sheet", "Student Monthly Attendance Sheet", link_type="Report", is_query_report=1, dependencies="Student Attendance"),
		_link("Absent Student Report", "Absent Student Report", link_type="Report", is_query_report=1, dependencies="Student Attendance"),
		_link("Student Batch-Wise Attendance", "Student Batch-Wise Attendance", link_type="Report", is_query_report=1, dependencies="Student Attendance"),
		_link("Course Enrollment", "Course Enrollment"),
		_link("Course Activity", "Course Activity"),
		_link("Quiz Activity", "Quiz Activity"),

		# Assessment
		_card_break("Assessment"),
		_link("Assessment Plan", "Assessment Plan"),
		_link("Assessment Group", "Assessment Group"),
		_link("Assessment Result", "Assessment Result"),
		_link("Assessment Criteria", "Assessment Criteria"),

		# Assessment Reports
		_card_break("Assessment Reports"),
		_link("Course wise Assessment Report", "Course wise Assessment Report", link_type="Report", is_query_report=1, dependencies="Assessment Result"),
		_link("Final Assessment Grades", "Final Assessment Grades", link_type="Report", is_query_report=1, dependencies="Assessment Result"),
		_link("Assessment Plan Status", "Assessment Plan Status", link_type="Report", is_query_report=1, dependencies="Assessment Plan"),
		_link("Student Report Generation Tool", "Student Report Generation Tool"),

		# Tools
		_card_break("Tools"),
		_link("Student Attendance Tool", "Student Attendance Tool"),
		_link("Assessment Result Tool", "Assessment Result Tool"),
		_link("Student Group Creation Tool", "Student Group Creation Tool"),
		_link("Program Enrollment Tool", "Program Enrollment Tool"),
		_link("Course Scheduling Tool", "Course Scheduling Tool"),

		# Other Reports
		_card_break("Other Reports"),
		_link("Student and Guardian Contact Details", "Student and Guardian Contact Details", link_type="Report", is_query_report=1, dependencies="Program Enrollment"),
	]

	workspace = frappe.get_doc({
		"doctype": "Workspace",
		"title": workspace_name,
		"label": workspace_name,
		"name": workspace_name,
		"module": "Vidyaan",
		"icon": "education",
		"public": 1,
		"content": json.dumps(content),
	})

	for shortcut in shortcuts:
		workspace.append("shortcuts", shortcut)

	for link in links:
		workspace.append("links", link)

	workspace.append("roles", {"role": "System Manager"})
	workspace.append("roles", {"role": "Institute Admin"})

	workspace.insert(ignore_permissions=True)


def _card_break(label):
	return {
		"type": "Card Break",
		"label": label,
		"hidden": 0,
		"is_query_report": 0,
		"link_count": 0,
		"onboard": 0,
	}


def _link(label, link_to, link_type="DocType", onboard=0, is_query_report=0, dependencies=""):
	return {
		"type": "Link",
		"label": label,
		"link_to": link_to,
		"link_type": link_type,
		"hidden": 0,
		"onboard": onboard,
		"is_query_report": is_query_report,
		"dependencies": dependencies,
		"link_count": 0,
	}
