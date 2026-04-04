import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user


def _get_student_groups(student_name):
    """Get all Student Groups a student belongs to."""
    return frappe.get_all(
        "Student Group Student",
        filters={"student": student_name, "active": 1},
        pluck="parent"
    )


@frappe.whitelist()
def get_exams():
    """Get all assessment plans (exams) for the logged-in student."""
    student = _get_student_for_user()
    if not student:
        return []

    groups = _get_student_groups(student.name)
    if not groups:
        return []

    exams = frappe.get_all(
        "Assessment Plan",
        filters={
            "student_group": ["in", groups],
            "docstatus": 1
        },
        fields=[
            "name", "assessment_name", "course", "student_group",
            "assessment_group", "schedule_date", "from_time", "to_time",
            "room", "examiner", "supervisor", "maximum_assessment_score",
            "grading_scale", "academic_year"
        ],
        order_by="schedule_date desc"
    )

    # Enrich with frontend-expected field names
    for exam in exams:
        course_name = frappe.db.get_value("Course", exam.course, "course_name") or exam.course
        exam["exam_id"] = exam.name
        exam["subject"] = course_name
        exam["date"] = str(exam.schedule_date) if exam.schedule_date else ""
        exam["start_time"] = str(exam.from_time) if exam.from_time else ""
        exam["end_time"] = str(exam.to_time) if exam.to_time else ""
        exam["exam_type"] = exam.assessment_group or ""
        exam["exam_group"] = exam.assessment_group or ""
        # Use schedule_date as both start/end for individual exam entries
        exam["exam_start_date"] = str(exam.schedule_date) if exam.schedule_date else ""
        exam["exam_end_date"] = str(exam.schedule_date) if exam.schedule_date else ""

    return exams


@frappe.whitelist()
def get_results():
    """Get all assessment results for the logged-in student."""
    student = _get_student_for_user()
    if not student:
        return []

    results = frappe.get_all(
        "Assessment Result",
        filters={"student": student.name, "docstatus": 1},
        fields=[
            "name", "assessment_plan", "student", "student_name",
            "course", "assessment_group", "academic_year", "academic_term",
            "student_group", "total_score", "grade", "maximum_score",
            "grading_scale"
        ],
        order_by="creation desc"
    )

    # Get student's program for enrichment
    enrollment = frappe.get_all(
        "Program Enrollment",
        filters={"student": student.name, "docstatus": 1},
        fields=["program"],
        order_by="creation desc",
        limit=1
    )
    student_program = enrollment[0].program if enrollment else ""

    # Enrich with assessment plan details
    for r in results:
        plan = frappe.db.get_value(
            "Assessment Plan", r.assessment_plan,
            ["schedule_date", "from_time", "to_time", "maximum_assessment_score"],
            as_dict=True
        )
        if plan:
            r["schedule_date"] = str(plan.schedule_date) if plan.schedule_date else ""
            r["from_time"] = str(plan.from_time) if plan.from_time else ""
            r["to_time"] = str(plan.to_time) if plan.to_time else ""
            r["max_score"] = plan.maximum_assessment_score or 0

        # Ensure program and maximum_score are set
        if not r.get("program"):
            r["program"] = student_program
        if not r.get("maximum_score"):
            r["maximum_score"] = r.get("max_score", 0)

        # Resolve course name
        course_name = frappe.db.get_value("Course", r.course, "course_name") if r.course else r.course
        r["course"] = course_name or r.course

    return results


@frappe.whitelist()
def get_admit_data(exam_type=""):
    """Get admit card data — upcoming exams with student info."""
    student = _get_student_for_user()
    if not student:
        return []

    groups = _get_student_groups(student.name)
    if not groups:
        return []

    filters = {
        "student_group": ["in", groups],
        "docstatus": 1,
        "schedule_date": [">=", frappe.utils.today()]
    }

    if exam_type:
        filters["assessment_group"] = exam_type

    exams = frappe.get_all(
        "Assessment Plan",
        filters=filters,
        fields=[
            "name", "assessment_name", "course", "student_group",
            "assessment_group", "schedule_date", "from_time", "to_time",
            "room", "examiner", "supervisor", "maximum_assessment_score"
        ],
        order_by="schedule_date asc"
    )

    return {
        "student": {
            "name": student.name,
            "first_name": student.first_name,
            "last_name": student.last_name or "",
            "image": student.image or "",
            "company": student.company or ""
        },
        "exams": exams
    }
