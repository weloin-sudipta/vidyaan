import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user, _get_instructor_for_user, _get_user_company


# ─── Student-side APIs ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_assignments():
    """Get all assignment-type assessment plans for the logged-in student."""
    student = _get_student_for_user()
    if not student:
        return []

    groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student.name, "active": 1},
        pluck="parent"
    )
    if not groups:
        return []

    plans = frappe.get_all(
        "Assessment Plan",
        filters={
            "student_group": ["in", groups],
            "docstatus": 1,
            "assessment_group": ["like", "%Assignment%"]
        },
        fields=[
            "name", "assessment_name", "course", "student_group",
            "schedule_date", "maximum_assessment_score", "examiner",
            "assessment_group"
        ],
        order_by="schedule_date desc"
    )

    # Enrich with submission status and frontend-expected fields
    for p in plans:
        result = frappe.db.get_value(
            "Assessment Result",
            {"student": student.name, "assessment_plan": p.name, "docstatus": 1},
            ["total_score", "grade"],
            as_dict=True
        )
        p["submitted"] = bool(result)
        p["score"] = result.total_score if result else None
        p["grade"] = result.grade if result else None
        p["deadline"] = str(p.schedule_date) if p.schedule_date else ""

        # Frontend expects these fields:
        course_name = frappe.db.get_value("Course", p.course, "course_name") or p.course
        p["title"] = p.assessment_name or course_name
        p["course_name"] = course_name
        p["due_date"] = str(p.schedule_date) if p.schedule_date else ""
        p["description"] = p.assessment_name or ""
        p["assignment_file"] = None

        # Compute status: Active, Submitted, Overdue, Evaluated
        if result and p["grade"]:
            p["status"] = "Evaluated"
        elif result:
            p["status"] = "Submitted"
        elif p.schedule_date and str(p.schedule_date) < frappe.utils.today():
            p["status"] = "Overdue"
        else:
            p["status"] = "Active"

    return plans


@frappe.whitelist()
def submit_assignment(assignment_name=None, submission_file=None):
    """Record a student's assignment submission (attach file to assessment result)."""
    if not assignment_name:
        frappe.throw(_("Assignment name is required"))

    student = _get_student_for_user()
    if not student:
        frappe.throw(_("No student record found"))

    # Check if assessment plan exists
    if not frappe.db.exists("Assessment Plan", assignment_name):
        frappe.throw(_("Assignment not found"))

    return {
        "success": True,
        "message": "Assignment submission recorded",
        "assignment": assignment_name,
        "file": submission_file or ""
    }


# ─── Teacher-side APIs ──────────────────────────────────────────────────────

@frappe.whitelist()
def get_instructor_courses():
    """Get courses the logged-in instructor teaches."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return []

    mappings = frappe.get_all(
        "Instructor Course Mapping",
        filters={"parent": instructor.name, "parenttype": "Instructor"},
        fields=["course", "course_name", "program"]
    )

    # Deduplicate by course
    seen = set()
    courses = []
    for m in mappings:
        if m.course not in seen:
            seen.add(m.course)
            course_name = m.course_name or frappe.db.get_value("Course", m.course, "course_name") or m.course
            courses.append({
                "name": m.course,
                "course_name": course_name,
                "program": m.program
            })

    return courses


@frappe.whitelist()
def get_instructor_student_groups(course=None):
    """Get student groups the logged-in instructor is assigned to."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return []

    company = _get_user_company()

    # Get groups where this instructor is listed
    filters = [
        ["Student Group Instructor", "instructor", "=", instructor.name]
    ]

    groups = frappe.get_all(
        "Student Group",
        filters={"company": company, "disabled": 0} if company else {"disabled": 0},
        fields=["name", "student_group_name", "program"],
        order_by="student_group_name asc"
    )

    # Filter to groups where instructor is assigned
    result = []
    for g in groups:
        instructors = frappe.get_all(
            "Student Group Instructor",
            filters={"parent": g.name, "instructor": instructor.name},
            pluck="instructor"
        )
        if instructors:
            if not course or frappe.db.exists("Program Course", {"parent": g.program, "course": course}):
                result.append(g)

    return result


@frappe.whitelist()
def get_instructor_assignment_templates(course=None):
    """Get assignment-type assessment plans created by this instructor."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return []

    filters = {
        "examiner": instructor.name,
        "docstatus": ["in", [0, 1]],
        "assessment_group": ["like", "%Assignment%"]
    }
    if course:
        filters["course"] = course

    return frappe.get_all(
        "Assessment Plan",
        filters=filters,
        fields=[
            "name", "assessment_name", "course", "student_group",
            "schedule_date", "maximum_assessment_score", "docstatus",
            "assessment_group"
        ],
        order_by="schedule_date desc"
    )


@frappe.whitelist()
def create_assignment_template(data=None):
    """Create a new assignment-type Assessment Plan."""
    if not data:
        frappe.throw(_("No data provided"))

    import json
    if isinstance(data, str):
        data = json.loads(data)

    instructor = _get_instructor_for_user()
    if not instructor:
        frappe.throw(_("No instructor record found"))

    plan = frappe.get_doc({
        "doctype": "Assessment Plan",
        "assessment_name": data.get("title", "Assignment"),
        "course": data.get("course"),
        "student_group": data.get("student_group"),
        "assessment_group": data.get("assessment_group", "Assignments"),
        "schedule_date": data.get("deadline") or frappe.utils.today(),
        "maximum_assessment_score": data.get("max_score", 100),
        "examiner": instructor.name,
    })
    plan.insert()

    return {"success": True, "name": plan.name}


@frappe.whitelist()
def publish_assignment_template(template_name=None):
    """Submit (publish) an assignment Assessment Plan."""
    if not template_name:
        frappe.throw(_("Template name is required"))

    plan = frappe.get_doc("Assessment Plan", template_name)
    plan.submit()

    return {"success": True, "name": plan.name}


@frappe.whitelist()
def get_template_submissions(template_name=None):
    """Get all student submissions (assessment results) for an assignment."""
    if not template_name:
        return []

    results = frappe.get_all(
        "Assessment Result",
        filters={"assessment_plan": template_name},
        fields=[
            "name", "student", "student_name", "total_score",
            "grade", "docstatus", "comment"
        ],
        order_by="student_name asc"
    )

    return results


@frappe.whitelist()
def grade_assignment(assignment_name=None, score=None, remarks=""):
    """Grade a student's assignment (update assessment result score)."""
    if not assignment_name:
        frappe.throw(_("Assignment name is required"))

    result = frappe.get_doc("Assessment Result", assignment_name)
    if result.docstatus == 1:
        frappe.throw(_("Result already submitted"))

    # Update score in detail rows if they exist
    if result.details:
        for detail in result.details:
            detail.score = float(score) if score else 0

    result.total_score = float(score) if score else 0
    result.comment = remarks
    result.save()

    return {"success": True, "name": result.name}
