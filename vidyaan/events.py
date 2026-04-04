import frappe
from frappe import _


def on_program_enrollment_created(doc, method):
    """
    When a Program Enrollment is created:
    1. Auto-add the student to relevant Student Groups for this program
    2. Auto-create Course Enrollments for each course in the program
    """
    try:
        _auto_add_to_student_groups(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "on_program_enrollment_created: auto-add to Student Group failed")

    try:
        _auto_create_course_enrollments(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "on_program_enrollment_created: auto-create Course Enrollment failed")


def _auto_add_to_student_groups(doc):
    """Add the enrolled student to all active Student Groups for this program and company."""
    student_groups = frappe.get_all(
        "Student Group",
        filters={"program": doc.program, "company": doc.company, "disabled": 0},
        pluck="name"
    )

    for sg_name in student_groups:
        sg = frappe.get_doc("Student Group", sg_name)
        # Check if student is already in the group
        already_in = any(row.student == doc.student for row in (sg.students or []))
        if not already_in:
            sg.append("students", {
                "student": doc.student,
                "student_name": doc.student_name,
                "active": 1
            })
            sg.save(ignore_permissions=True)


def _auto_create_course_enrollments(doc):
    """Auto-create Course Enrollment for each course in the enrolled program."""
    courses = frappe.get_all(
        "Program Course", filters={"parent": doc.program}, pluck="course"
    )

    for course in courses:
        if not frappe.db.exists("Course Enrollment", {
            "student": doc.student,
            "course": course,
            "program_enrollment": doc.name
        }):
            frappe.get_doc({
                "doctype": "Course Enrollment",
                "student": doc.student,
                "course": course,
                "program_enrollment": doc.name,
                "enrollment_date": frappe.utils.nowdate()
            }).insert(ignore_permissions=True)


def validate_assessment_result(doc, method):
	"""
	Strict Grading Permission: Ensure the logged-in user is the Examiner or Supervisor
	specified on the Assessment Plan, otherwise block them from saving Assessment Results.
	"""
	# Allow System Manager and Institute Admin to grade anyone
	roles = frappe.get_roles()
	if "System Manager" in roles or "Institute Admin" in roles:
		return

	if "Instructor" in roles:
		plan = frappe.get_doc("Assessment Plan", doc.assessment_plan)

		if plan.examiner or plan.supervisor:
			user_instructors = _get_user_instructors(frappe.session.user)

			if not user_instructors:
				frappe.throw(_(
					"Your account is not linked to an Instructor profile. "
					"Ask an administrator to create an Employee and Instructor record linked to your User account."
				))

			if plan.examiner not in user_instructors and plan.supervisor not in user_instructors:
				frappe.throw(_(
					"Access Denied: You are not the Examiner or Supervisor for this Assessment Plan. "
					"Only {0} (Examiner) or {1} (Supervisor) can grade this assessment."
				).format(plan.examiner or "N/A", plan.supervisor or "N/A"))


def _get_user_instructors(user):
	"""
	Resolve the current user to their Instructor record(s).
	Tries: User → Employee → Instructor (primary path)
	Fallback: Instructor → Employee → User (reverse lookup)
	"""
	# Primary path: User → Employee → Instructor
	user_employees = frappe.get_all("Employee", filters={"user_id": user}, pluck="name")
	if user_employees:
		instructors = frappe.get_all(
			"Instructor", filters={"employee": ["in", user_employees]}, pluck="name"
		)
		if instructors:
			return instructors

	# Fallback: find any Instructor whose linked Employee has this user_id
	instructors = frappe.db.sql("""
		SELECT inst.name
		FROM `tabInstructor` inst
		JOIN `tabEmployee` emp ON inst.employee = emp.name
		WHERE emp.user_id = %s
	""", (user,), pluck="name")

	return instructors or []
