import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_instructor_for_user


@frappe.whitelist()
def get_my_exams():
    """Get all assessment plans where the logged-in user is examiner or supervisor."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return []

    exams = frappe.get_all(
        "Assessment Plan",
        filters={
            "docstatus": 1,
            "examiner": instructor.name
        },
        fields=[
            "name", "assessment_name", "course", "student_group",
            "assessment_group", "schedule_date", "from_time", "to_time",
            "room", "maximum_assessment_score", "grading_scale"
        ],
        order_by="schedule_date desc",
        ignore_permissions=True,
    )

    # Also include plans where instructor is supervisor
    supervisor_exams = frappe.get_all(
        "Assessment Plan",
        filters={
            "docstatus": 1,
            "supervisor": instructor.name,
            "examiner": ["!=", instructor.name]
        },
        fields=[
            "name", "assessment_name", "course", "student_group",
            "assessment_group", "schedule_date", "from_time", "to_time",
            "room", "maximum_assessment_score", "grading_scale"
        ],
        order_by="schedule_date desc",
        ignore_permissions=True,
    )

    all_exams = exams + supervisor_exams

    # Enrich with result count
    for exam in all_exams:
        exam["results_count"] = frappe.db.count(
            "Assessment Result", {"assessment_plan": exam.name, "docstatus": 1}
        )
        # Get student count from group
        exam["student_count"] = frappe.db.count(
            "Student Group Student", {"parent": exam.student_group, "active": 1}
        )
        exam["grading_complete"] = exam["results_count"] >= exam["student_count"]

    return all_exams


@frappe.whitelist()
def get_my_courses():
    """Get instructor profile with course mappings (instructor_log)."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return {}

    # Get course mappings
    mappings = frappe.get_all(
        "Instructor Course Mapping",
        filters={"parent": instructor.name, "parenttype": "Instructor"},
        fields=["course", "course_name", "program", "is_preferred"]
    )

    return {
        "instructor_id": instructor.name,
        "instructor_name": instructor.instructor_name,
        "instructor_log": mappings
    }


@frappe.whitelist()
def get_exam_students(assessment_plan=None):
    """Get all students for an assessment plan with existing result data."""
    if not assessment_plan:
        frappe.throw(_("Assessment Plan is required"))

    plan = frappe.get_doc("Assessment Plan", assessment_plan)

    # Get students from the student group
    group_students = frappe.get_all(
        "Student Group Student",
        filters={"parent": plan.student_group, "active": 1},
        fields=["student", "student_name"]
    )

    # Get existing results
    existing_results = {}
    results = frappe.get_all(
        "Assessment Result",
        filters={"assessment_plan": assessment_plan},
        fields=["name", "student", "total_score", "grade", "comment"]
    )
    for r in results:
        existing_results[r.student] = r

    students = []
    for gs in group_students:
        result = existing_results.get(gs.student)
        students.append({
            "student": gs.student,
            "student_name": gs.student_name,
            "result_id": result.name if result else None,
            "score": result.total_score if result else None,
            "grade": result.grade if result else None,
            "comment": result.comment if result else ""
        })

    return {
        "plan": {
            "name": plan.name,
            "assessment_name": plan.assessment_name,
            "course": plan.course,
            "student_group": plan.student_group,
            "schedule_date": str(plan.schedule_date) if plan.schedule_date else "",
            "maximum_assessment_score": plan.maximum_assessment_score,
            "grading_scale": plan.grading_scale or ""
        },
        "students": students
    }


@frappe.whitelist()
def submit_exam_results(assessment_plan=None, results=None):
    """Submit or update assessment results for students."""
    if not assessment_plan or not results:
        frappe.throw(_("Assessment plan and results are required"))

    import json
    if isinstance(results, str):
        results = json.loads(results)

    plan = frappe.get_doc("Assessment Plan", assessment_plan)

    saved = []
    errors = []

    for entry in results:
        student = entry.get("student")
        score = float(entry.get("score", 0))
        comment = entry.get("comment", "")

        if not student:
            continue

        try:
            # Check for existing result
            existing = frappe.db.get_value(
                "Assessment Result",
                {"assessment_plan": assessment_plan, "student": student},
                "name"
            )

            if existing:
                result_doc = frappe.get_doc("Assessment Result", existing)
                result_doc.total_score = score
                result_doc.comment = comment
                if result_doc.details:
                    for detail in result_doc.details:
                        detail.score = score
                result_doc.save()
                saved.append(student)
            else:
                # Build assessment detail rows from plan criteria
                details = []
                if plan.assessment_criteria:
                    for criteria in plan.assessment_criteria:
                        details.append({
                            "assessment_criteria": criteria.assessment_criteria,
                            "maximum_score": criteria.maximum_score,
                            "score": score
                        })

                result_doc = frappe.get_doc({
                    "doctype": "Assessment Result",
                    "assessment_plan": assessment_plan,
                    "student": student,
                    "student_group": plan.student_group,
                    "academic_year": plan.academic_year if hasattr(plan, "academic_year") else "",
                    "academic_term": plan.academic_term if hasattr(plan, "academic_term") else "",
                    "course": plan.course,
                    "assessment_group": plan.assessment_group,
                    "total_score": score,
                    "comment": comment,
                    "grading_scale": plan.grading_scale or "",
                    "maximum_score": plan.maximum_assessment_score,
                    "details": details
                })
                result_doc.insert()
                saved.append(student)

        except Exception as e:
            frappe.log_error(f"submit_exam_results error for {student}: {e}")
            errors.append({"student": student, "error": str(e)})

    return {
        "success": True,
        "saved": len(saved),
        "errors": errors
    }
