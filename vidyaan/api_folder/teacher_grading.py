import json

import frappe
from frappe import _
from frappe.utils import flt

from vidyaan.api_folder.profile import _get_instructor_for_user


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _assert_can_grade(plan):
    """Only the plan's examiner or supervisor (or System Manager) may grade."""
    instructor = _get_instructor_for_user()
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" in roles or "Academics User" in roles:
        return
    if not instructor:
        frappe.throw(_("You are not registered as an instructor."), frappe.PermissionError)
    if plan.examiner != instructor.name and plan.supervisor != instructor.name:
        frappe.throw(
            _("You are not the examiner or supervisor of this assessment plan."),
            frappe.PermissionError,
        )


def _build_details_from_plan(plan, total_score):
    """Distribute the entered total proportionally across plan criteria.

    - Single criterion → criterion.score = total
    - Multiple criteria → score = total * (criterion_max / sum_max)
    Last row absorbs any rounding remainder so the sum exactly equals total.
    """
    if not plan.assessment_criteria:
        return []

    sum_max = sum(flt(c.maximum_score) for c in plan.assessment_criteria) or 1.0
    details = []
    running = 0.0
    last_idx = len(plan.assessment_criteria) - 1

    for i, criterion in enumerate(plan.assessment_criteria):
        if i == last_idx:
            # Last row absorbs the remainder so totals match exactly
            score = round(flt(total_score) - running, 2)
        else:
            score = round(flt(total_score) * flt(criterion.maximum_score) / sum_max, 2)
            running += score

        # Clamp to maximum to avoid validation throw on rounding edge cases
        if score > flt(criterion.maximum_score):
            score = flt(criterion.maximum_score)
        if score < 0:
            score = 0

        details.append({
            "assessment_criteria": criterion.assessment_criteria,
            "maximum_score": criterion.maximum_score,
            "score": score,
        })
    return details


def _apply_score_to_details(result_doc, plan, total_score):
    """Overwrite existing detail rows with proportionally distributed scores."""
    new_details = _build_details_from_plan(plan, total_score)
    result_doc.set("details", [])
    for d in new_details:
        result_doc.append("details", d)


def _save_one_result(plan, student, score, comment, submit):
    """Create / update / amend the Assessment Result for one student.

    Returns: dict with student, status (created|updated|amended), result_id, docstatus, grade
    Raises on validation error (caller handles).
    """
    score = flt(score)
    max_score = flt(plan.maximum_assessment_score) or 100.0

    if score < 0 or score > max_score:
        frappe.throw(_("Score must be between 0 and {0}").format(max_score))

    existing_name = frappe.db.get_value(
        "Assessment Result",
        {"assessment_plan": plan.name, "student": student, "docstatus": ["!=", 2]},
        "name",
    )

    status = "created"

    if existing_name:
        existing = frappe.get_doc("Assessment Result", existing_name)

        if existing.docstatus == 1:
            # Submitted → cancel + amend
            existing.cancel()
            new_doc = frappe.copy_doc(existing)
            new_doc.amended_from = existing.name
            _apply_score_to_details(new_doc, plan, score)
            new_doc.comment = comment or ""
            new_doc.insert(ignore_permissions=True)
            if submit:
                new_doc.submit()
            status = "amended"
            return {
                "student": student,
                "status": status,
                "result_id": new_doc.name,
                "docstatus": new_doc.docstatus,
                "grade": new_doc.grade,
                "total_score": new_doc.total_score,
            }
        else:
            # Draft → update in place
            _apply_score_to_details(existing, plan, score)
            existing.comment = comment or ""
            existing.save(ignore_permissions=True)
            if submit:
                existing.submit()
            status = "updated"
            return {
                "student": student,
                "status": status,
                "result_id": existing.name,
                "docstatus": existing.docstatus,
                "grade": existing.grade,
                "total_score": existing.total_score,
            }

    # No existing → create fresh
    new_doc = frappe.get_doc({
        "doctype": "Assessment Result",
        "assessment_plan": plan.name,
        "student": student,
        "student_group": plan.student_group,
        "academic_year": getattr(plan, "academic_year", None),
        "academic_term": getattr(plan, "academic_term", None),
        "course": plan.course,
        "assessment_group": plan.assessment_group,
        "comment": comment or "",
        "grading_scale": plan.grading_scale or "",
        "maximum_score": plan.maximum_assessment_score,
        "details": _build_details_from_plan(plan, score),
    })
    new_doc.insert(ignore_permissions=True)
    if submit:
        new_doc.submit()
    return {
        "student": student,
        "status": status,
        "result_id": new_doc.name,
        "docstatus": new_doc.docstatus,
        "grade": new_doc.grade,
        "total_score": new_doc.total_score,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Whitelisted endpoints
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_my_exams():
    """Get all assessment plans where the logged-in user is examiner or supervisor."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return []

    exams = frappe.get_all(
        "Assessment Plan",
        filters={"docstatus": 1, "examiner": instructor.name},
        fields=[
            "name", "assessment_name", "course", "student_group",
            "assessment_group", "schedule_date", "from_time", "to_time",
            "room", "maximum_assessment_score", "grading_scale",
        ],
        order_by="schedule_date desc",
        ignore_permissions=True,
    )

    supervisor_exams = frappe.get_all(
        "Assessment Plan",
        filters={
            "docstatus": 1,
            "supervisor": instructor.name,
            "examiner": ["!=", instructor.name],
        },
        fields=[
            "name", "assessment_name", "course", "student_group",
            "assessment_group", "schedule_date", "from_time", "to_time",
            "room", "maximum_assessment_score", "grading_scale",
        ],
        order_by="schedule_date desc",
        ignore_permissions=True,
    )

    all_exams = exams + supervisor_exams

    for exam in all_exams:
        exam["results_count"] = frappe.db.count(
            "Assessment Result", {"assessment_plan": exam.name, "docstatus": 1}
        )
        exam["draft_count"] = frappe.db.count(
            "Assessment Result", {"assessment_plan": exam.name, "docstatus": 0}
        )
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

    mappings = frappe.get_all(
        "Instructor Course Mapping",
        filters={"parent": instructor.name, "parenttype": "Instructor"},
        fields=["course", "course_name", "program", "is_preferred"],
    )

    return {
        "instructor_id": instructor.name,
        "instructor_name": instructor.instructor_name,
        "instructor_log": mappings,
    }


@frappe.whitelist()
def get_exam_students(assessment_plan=None):
    """Get all students for an assessment plan with existing result data + docstatus."""
    if not assessment_plan:
        frappe.throw(_("Assessment Plan is required"))

    plan = frappe.get_doc("Assessment Plan", assessment_plan)

    group_students = frappe.get_all(
        "Student Group Student",
        filters={"parent": plan.student_group, "active": 1},
        fields=["student", "student_name"],
    )

    # Latest result per student (skip cancelled)
    existing_results = {}
    results = frappe.get_all(
        "Assessment Result",
        filters={"assessment_plan": assessment_plan, "docstatus": ["!=", 2]},
        fields=["name", "student", "total_score", "grade", "comment", "docstatus"],
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
            "comment": result.comment if result else "",
            "docstatus": result.docstatus if result else None,  # 0=draft, 1=submitted
        })

    return {
        "plan": {
            "name": plan.name,
            "assessment_name": plan.assessment_name,
            "course": plan.course,
            "student_group": plan.student_group,
            "schedule_date": str(plan.schedule_date) if plan.schedule_date else "",
            "maximum_assessment_score": plan.maximum_assessment_score,
            "grading_scale": plan.grading_scale or "",
        },
        "students": students,
    }


@frappe.whitelist()
def submit_exam_results(assessment_plan=None, results=None, submit=True):
    """Save (and optionally submit) assessment results for one or many students.

    Args:
        assessment_plan: name of the Assessment Plan
        results: JSON string or list of {student, score, comment}
        submit: if truthy → call .submit() on each result (docstatus=1).
                if falsy → leave as draft (docstatus=0).
    """
    if not assessment_plan or not results:
        frappe.throw(_("Assessment plan and results are required"))

    if isinstance(results, str):
        results = json.loads(results)

    # Coerce submit flag (frontend may send "true"/"false"/"1"/"0")
    if isinstance(submit, str):
        submit = submit.lower() in ("1", "true", "yes")
    submit = bool(submit)

    plan = frappe.get_doc("Assessment Plan", assessment_plan)
    _assert_can_grade(plan)

    saved = []
    errors = []

    for entry in results:
        student = entry.get("student")
        if not student:
            continue
        score = entry.get("score")
        if score in (None, ""):
            continue  # skip blank rows — don't create empty drafts

        comment = entry.get("comment", "")

        try:
            res = _save_one_result(plan, student, score, comment, submit)
            saved.append(res)
        except Exception as e:
            frappe.log_error(
                title=f"submit_exam_results: {student}",
                message=frappe.get_traceback(),
            )
            errors.append({"student": student, "error": str(e)})

    return {
        "success": len(errors) == 0,
        "submitted": submit,
        "saved_count": len(saved),
        "saved": saved,
        "errors": errors,
    }


@frappe.whitelist()
def submit_single_result(assessment_plan=None, student=None, score=None, comment="", submit=True):
    """Save / submit a single student's result. Used by per-row save buttons."""
    if not assessment_plan or not student:
        frappe.throw(_("Assessment plan and student are required"))
    if score in (None, ""):
        frappe.throw(_("Score is required"))

    if isinstance(submit, str):
        submit = submit.lower() in ("1", "true", "yes")

    plan = frappe.get_doc("Assessment Plan", assessment_plan)
    _assert_can_grade(plan)

    try:
        res = _save_one_result(plan, student, score, comment, bool(submit))
        return {"success": True, "result": res}
    except Exception as e:
        frappe.log_error(
            title=f"submit_single_result: {student}",
            message=frappe.get_traceback(),
        )
        return {"success": False, "error": str(e)}
