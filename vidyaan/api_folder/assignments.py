import frappe
from frappe import _
from frappe.utils import now_datetime, today, getdate
from vidyaan.api_folder.profile import (
    _get_student_for_user,
    _get_instructor_for_user,
    _get_user_company,
)


# ═══════════════════════════════════════════════════════════════════════════
# NEW ASSIGNMENT SYSTEM  (Assignment DocType)
# ═══════════════════════════════════════════════════════════════════════════


# ─── Internal helpers ────────────────────────────────────────────────────

def _require_instructor():
    """Return the Instructor record for the current user, or throw."""
    instructor = _get_instructor_for_user()
    if not instructor:
        frappe.throw(_("No Instructor record found for the current user."),
                     frappe.PermissionError)
    return instructor


def _require_student():
    """Return the Student record for the current user, or throw."""
    student = _get_student_for_user()
    if not student:
        frappe.throw(_("No Student record found for the current user."),
                     frappe.PermissionError)
    return student


def _check_instructor_owns(assignment_doc, instructor):
    """Throw PermissionError if instructor does not own the assignment."""
    if assignment_doc.instructor != instructor.name:
        frappe.throw(
            _("You do not have permission to modify Assignment '{0}'.").format(
                assignment_doc.name
            ),
            frappe.PermissionError,
        )


def _resolve_target_groups(assign_to, student_groups_list, course, instructor):
    """Return a validated list of Student Group names for the assignment.

    assign_to: "All Enrolled" | "Specific Groups"
    student_groups_list: list of names (used only for Specific Groups)
    """
    if assign_to == "All Enrolled":
        groups = get_instructor_student_groups(course=course)
        names = [g["name"] if isinstance(g, dict) else g.name for g in groups]
        if not names:
            frappe.throw(
                _(
                    "No student groups found for course '{0}'. "
                    "Open the Course in Frappe Desk and confirm you are mapped to it as an "
                    "instructor (Instructor → Courses), AND that the course is part of a "
                    "Program with an active Student Group. Alternatively switch to "
                    "'Specific Groups' and pick groups manually."
                ).format(course)
            )
        return names
    else:
        # Specific Groups
        if not student_groups_list:
            frappe.throw(_("At least one Student Group is required when 'Assign To' is 'Specific Groups'."))
        validated = []
        for sg in student_groups_list:
            if not frappe.db.exists("Student Group", sg):
                frappe.throw(_("Student Group '{0}' not found.").format(sg))
            validated.append(sg)
        return validated


# ─── Instructor: create / manage ────────────────────────────────────────

@frappe.whitelist()
def create_assignment(data=None):
    """Create a new Assignment document (status remains Draft).

    data keys: title, course, topic, due_date, max_score, assign_to,
               student_groups (list), description, assignment_file
    Returns: {success, name}
    """
    import json
    if not data:
        frappe.throw(_("No data provided."))
    if isinstance(data, str):
        data = json.loads(data)

    instructor = _require_instructor()

    title = (data.get("title") or "").strip()
    course = (data.get("course") or "").strip()
    due_date = data.get("due_date") or ""
    max_score = float(data.get("max_score") or 100)
    assign_to = (data.get("assign_to") or "All Enrolled").strip()
    student_groups_list = data.get("student_groups") or []
    description = data.get("description") or ""
    assignment_file = data.get("assignment_file") or ""
    topic = data.get("topic") or None

    if not title:
        frappe.throw(_("Title is required."))
    if not course:
        frappe.throw(_("Course is required."))
    if not frappe.db.exists("Course", course):
        frappe.throw(_("Course '{0}' not found.").format(course))
    if not due_date:
        frappe.throw(_("Due Date is required."))

    target_group_names = _resolve_target_groups(assign_to, student_groups_list, course, instructor)

    target_rows = [{"student_group": sg} for sg in target_group_names]

    doc = frappe.get_doc({
        "doctype": "Assignment",
        "title": title,
        "course": course,
        "topic": topic,
        "instructor": instructor.name,
        "due_date": due_date,
        "max_score": max_score,
        "assign_to": assign_to,
        "description": description,
        "assignment_file": assignment_file,
        "status": "Draft",
        "target_groups": target_rows,
    })
    doc.insert(ignore_permissions=False)

    return {"success": True, "name": doc.name}


@frappe.whitelist()
def publish_assignment(name=None):
    """Publish a Draft assignment and populate the submissions child table.

    For each target group, fetches all active Student Group Student rows and
    appends one Assignment Submission row per unique student.
    Returns: {success, name, submission_count}
    """
    if not name:
        frappe.throw(_("Assignment name is required."))

    instructor = _require_instructor()
    doc = frappe.get_doc("Assignment", name)
    _check_instructor_owns(doc, instructor)

    # Idempotent: already published
    if doc.status == "Published":
        submission_count = len(doc.submissions or [])
        return {"success": True, "name": doc.name, "submission_count": submission_count}

    if doc.status == "Closed":
        frappe.throw(_("Cannot publish a Closed assignment."))

    # Collect unique students across all target groups
    seen_students = set()
    new_rows = []

    for tg_row in (doc.target_groups or []):
        sg = tg_row.student_group
        if not sg:
            continue
        members = frappe.get_all(
            "Student Group Student",
            filters={"parent": sg, "active": 1},
            fields=["student"]
        )
        for m in members:
            if m.student and m.student not in seen_students:
                seen_students.add(m.student)
                new_rows.append({
                    "student": m.student,
                    "student_group": sg,
                    "status": "Pending",
                })

    # Append rows only for students not already present
    existing_students = {r.student for r in (doc.submissions or [])}
    for row in new_rows:
        if row["student"] not in existing_students:
            doc.append("submissions", row)

    doc.status = "Published"
    if not doc.published_on:
        doc.published_on = now_datetime()

    doc.save(ignore_permissions=True)

    return {
        "success": True,
        "name": doc.name,
        "submission_count": len([r for r in doc.submissions if r.student]),
    }


@frappe.whitelist()
def update_assignment(name=None, data=None):
    """Update a Draft assignment's editable fields.

    Only allowed when status == "Draft". Owner instructor only.
    Returns: {success, name}
    """
    import json
    if not name:
        frappe.throw(_("Assignment name is required."))
    if not data:
        frappe.throw(_("No data provided."))
    if isinstance(data, str):
        data = json.loads(data)

    instructor = _require_instructor()
    doc = frappe.get_doc("Assignment", name)
    _check_instructor_owns(doc, instructor)

    if doc.status != "Draft":
        frappe.throw(_("Only Draft assignments can be updated. Current status: {0}.").format(doc.status))

    editable = ["title", "topic", "due_date", "max_score", "description", "assignment_file"]
    for field in editable:
        if field in data and data[field] is not None:
            doc.set(field, data[field])

    # Re-sync target_groups when provided
    if "student_groups" in data and data["student_groups"] is not None:
        incoming = data["student_groups"]
        for sg in incoming:
            if not frappe.db.exists("Student Group", sg):
                frappe.throw(_("Student Group '{0}' not found.").format(sg))
        doc.target_groups = []
        for sg in incoming:
            doc.append("target_groups", {"student_group": sg})

    doc.save(ignore_permissions=False)
    return {"success": True, "name": doc.name}


@frappe.whitelist()
def delete_assignment(name=None):
    """Delete a Draft assignment. Blocked if any submission has a score.

    Owner instructor only.
    Returns: {success}
    """
    if not name:
        frappe.throw(_("Assignment name is required."))

    instructor = _require_instructor()
    doc = frappe.get_doc("Assignment", name)
    _check_instructor_owns(doc, instructor)

    for row in (doc.submissions or []):
        if row.score is not None and row.score != 0:
            frappe.throw(
                _(
                    "Cannot delete Assignment '{0}': one or more submissions have "
                    "already been graded. Close the assignment instead."
                ).format(doc.title)
            )

    frappe.delete_doc("Assignment", name, ignore_permissions=False)
    return {"success": True}


@frappe.whitelist()
def close_assignment(name=None):
    """Set a Published assignment's status to Closed. Owner only.

    Returns: {success}
    """
    if not name:
        frappe.throw(_("Assignment name is required."))

    instructor = _require_instructor()
    doc = frappe.get_doc("Assignment", name)
    _check_instructor_owns(doc, instructor)

    doc.status = "Closed"
    doc.save(ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def get_instructor_assignments(course=None, status=None):
    """Get all assignments belonging to the current instructor.

    Optional filters: course, status
    Returns a list of assignment objects enriched with submission counts.
    """
    instructor = _require_instructor()

    filters = {"instructor": instructor.name}
    if course:
        filters["course"] = course
    if status:
        filters["status"] = status

    assignments = frappe.get_all(
        "Assignment",
        filters=filters,
        fields=[
            "name", "title", "course", "topic", "instructor",
            "due_date", "max_score", "assign_to", "status",
            "published_on", "description", "assignment_file",
        ],
        order_by="due_date desc",
    )

    if not assignments:
        return []

    # Resolve course_name in bulk
    course_names_map = {}
    course_ids = list({a.course for a in assignments if a.course})
    if course_ids:
        for row in frappe.get_all("Course", filters={"name": ["in", course_ids]},
                                  fields=["name", "course_name"]):
            course_names_map[row.name] = row.course_name

    # Fetch target_groups and submissions in bulk
    assignment_names = [a.name for a in assignments]

    tg_rows = frappe.get_all(
        "Assignment Target Group",
        filters={"parent": ["in", assignment_names], "parenttype": "Assignment"},
        fields=["parent", "student_group", "student_group_name"],
    )
    tg_map = {}
    for r in tg_rows:
        tg_map.setdefault(r.parent, []).append({
            "student_group": r.student_group,
            "student_group_name": r.student_group_name,
        })

    sub_rows = frappe.get_all(
        "Assignment Submission",
        filters={"parent": ["in", assignment_names], "parenttype": "Assignment"},
        fields=["parent", "status", "score"],
    )
    sub_map = {}
    for r in sub_rows:
        sub_map.setdefault(r.parent, []).append(r)

    for a in assignments:
        a["course_name"] = course_names_map.get(a.course, a.course)
        a["target_groups"] = tg_map.get(a.name, [])
        subs = sub_map.get(a.name, [])
        a["submission_count"] = len(subs)
        a["graded_count"] = sum(1 for s in subs if s.status == "Graded")
        a["pending_count"] = sum(1 for s in subs if s.status in ("Pending", "Submitted", "Late"))

    return assignments


@frappe.whitelist()
def get_assignment_detail(name=None):
    """Get full assignment details including all submissions.

    Owner instructor only.
    Returns the full document dict with resolved student names.
    """
    if not name:
        frappe.throw(_("Assignment name is required."))

    instructor = _require_instructor()
    doc = frappe.get_doc("Assignment", name)
    _check_instructor_owns(doc, instructor)

    result = doc.as_dict()

    # Resolve course_name
    result["course_name"] = frappe.db.get_value("Course", doc.course, "course_name") or doc.course

    return result


# ─── Instructor: grading ────────────────────────────────────────────────

@frappe.whitelist()
def grade_submission(assignment=None, student=None, score=None, remarks=""):
    """Grade a single student's submission on an assignment.

    Owner instructor only. score must be between 0 and max_score.
    Returns: {success}
    """
    if not assignment:
        frappe.throw(_("Assignment name is required."))
    if not student:
        frappe.throw(_("Student is required."))
    if score is None:
        frappe.throw(_("Score is required."))

    instructor = _require_instructor()
    doc = frappe.get_doc("Assignment", assignment)
    _check_instructor_owns(doc, instructor)

    score = float(score)
    if score < 0:
        frappe.throw(_("Score cannot be negative."))
    if score > doc.max_score:
        frappe.throw(
            _("Score {0} exceeds max score {1} for this assignment.").format(score, doc.max_score)
        )

    # Find the submission row
    target_row = None
    for row in (doc.submissions or []):
        if row.student == student:
            target_row = row
            break

    if not target_row:
        frappe.throw(
            _("No submission row found for student '{0}' in assignment '{1}'.").format(
                student, assignment
            )
        )

    target_row.score = score
    target_row.remarks = remarks
    target_row.graded_by = frappe.session.user
    target_row.graded_on = now_datetime()
    target_row.status = "Graded"

    doc.save(ignore_permissions=True)
    return {"success": True}


# ─── Student: submit / view ─────────────────────────────────────────────

@frappe.whitelist()
def submit_student_assignment(assignment=None, submission_file=None, submission_text=None):
    """Record a student's submission on a Published assignment.

    Late submissions are allowed but marked with status "Late".
    Returns: {success}
    """
    if not assignment:
        frappe.throw(_("Assignment name is required."))

    student = _require_student()
    doc = frappe.get_doc("Assignment", assignment)

    if doc.status != "Published":
        frappe.throw(
            _("Assignment '{0}' is not currently accepting submissions (status: {1}).").format(
                assignment, doc.status
            )
        )

    # Find the student's submission row
    target_row = None
    for row in (doc.submissions or []):
        if row.student == student.name:
            target_row = row
            break

    if not target_row:
        frappe.throw(_("You are not enrolled in this assignment."))

    # Determine if late
    is_late = doc.due_date and getdate(doc.due_date) < getdate(today())
    new_status = "Late" if is_late else "Submitted"

    if submission_file:
        target_row.submission_file = submission_file
    if submission_text:
        target_row.submission_text = submission_text
    target_row.submitted_on = now_datetime()
    target_row.status = new_status

    doc.save(ignore_permissions=True)
    return {"success": True}


@frappe.whitelist()
def get_student_assignments():
    """Get all Published assignments that the current student appears in.

    Returns a list with the student's own submission details embedded.
    Replaces the legacy get_assignments endpoint.
    """
    student = _require_student()

    # Find all submission rows for this student across all assignments
    sub_rows = frappe.get_all(
        "Assignment Submission",
        filters={
            "student": student.name,
            "parenttype": "Assignment",
        },
        fields=[
            "parent", "submitted_on", "submission_file", "submission_text",
            "score", "remarks", "graded_on", "status",
        ],
    )

    if not sub_rows:
        return []

    assignment_names = list({r.parent for r in sub_rows})
    sub_by_assignment = {r.parent: r for r in sub_rows}

    assignments = frappe.get_all(
        "Assignment",
        filters={
            "name": ["in", assignment_names],
            "status": "Published",
        },
        fields=[
            "name", "title", "course", "topic", "due_date", "max_score",
            "description", "assignment_file", "status",
        ],
    )

    # Bulk resolve course names
    course_ids = list({a.course for a in assignments if a.course})
    course_names_map = {}
    if course_ids:
        for row in frappe.get_all("Course", filters={"name": ["in", course_ids]},
                                  fields=["name", "course_name"]):
            course_names_map[row.name] = row.course_name

    result = []
    for a in assignments:
        sub = sub_by_assignment.get(a.name, {})
        sub_status = sub.get("status") if isinstance(sub, dict) else getattr(sub, "status", None)
        is_overdue = (
            a.due_date
            and getdate(a.due_date) < getdate(today())
            and sub_status not in ("Submitted", "Graded", "Late")
        )
        result.append({
            "name": a.name,
            "title": a.title,
            "course": a.course,
            "course_name": course_names_map.get(a.course, a.course),
            "topic": a.topic,
            "due_date": str(a.due_date) if a.due_date else "",
            "max_score": a.max_score,
            "description": a.description or "",
            "assignment_file": a.assignment_file or "",
            "status": a.status,
            "my_submission": {
                "submitted_on": str(sub.get("submitted_on") or "") if isinstance(sub, dict)
                                else str(getattr(sub, "submitted_on", "") or ""),
                "submission_file": (sub.get("submission_file") if isinstance(sub, dict)
                                    else getattr(sub, "submission_file", None)) or "",
                "submission_text": (sub.get("submission_text") if isinstance(sub, dict)
                                    else getattr(sub, "submission_text", None)) or "",
                "score": (sub.get("score") if isinstance(sub, dict)
                          else getattr(sub, "score", None)),
                "remarks": (sub.get("remarks") if isinstance(sub, dict)
                            else getattr(sub, "remarks", None)) or "",
                "graded_on": str((sub.get("graded_on") if isinstance(sub, dict)
                                  else getattr(sub, "graded_on", None)) or ""),
                "status": sub_status or "Pending",
            },
            "is_overdue": is_overdue,
        })

    return result


# ─── Shared helpers (kept for both old and new systems) ─────────────────

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
    """Get student groups the logged-in instructor teaches.

    Honors TWO data models simultaneously (whichever is populated):
      1. Explicit  — Student Group Instructor child rows (the Education
                     module's native model).
      2. Implicit  — Instructor Course Mapping rows on the Instructor doc.
                     A group is included if its program is one the
                     instructor teaches the given course in.

    The union of both is returned, deduplicated, optionally filtered by
    course (the course must also be present in each group's program).
    """
    instructor = _get_instructor_for_user()
    if not instructor:
        return []

    company = _get_user_company()

    # ── 1. Explicit links (Student Group Instructor) ──────────────────────
    explicit_names = set(frappe.get_all(
        "Student Group Instructor",
        filters={"instructor": instructor.name},
        pluck="parent",
    ))

    # ── 2. Implicit links (Instructor Course Mapping → program → groups) ──
    icm_filters = {"parent": instructor.name, "parenttype": "Instructor"}
    if course:
        icm_filters["course"] = course
    programs_taught = list({
        row for row in frappe.get_all(
            "Instructor Course Mapping",
            filters=icm_filters,
            pluck="program",
        ) if row
    })

    implicit_names = set()
    if programs_taught:
        sg_filters = {"program": ["in", programs_taught], "disabled": 0}
        if company:
            sg_filters["company"] = company
        implicit_names = set(frappe.get_all(
            "Student Group",
            filters=sg_filters,
            pluck="name",
        ))

    union_names = list(explicit_names | implicit_names)
    if not union_names:
        return []

    sg_filters = {"name": ["in", union_names], "disabled": 0}
    if company:
        sg_filters["company"] = company

    groups = frappe.get_all(
        "Student Group",
        filters=sg_filters,
        fields=["name", "student_group_name", "program"],
        order_by="student_group_name asc",
    )

    # When a specific course is requested, ensure each group's program
    # actually contains that course (defensive — implicit list is already
    # filtered, but explicit list may include groups whose program does not).
    if course:
        groups = [
            g for g in groups
            if frappe.db.exists("Program Course", {"parent": g.program, "course": course})
        ]

    return groups


# ─── Backward-compatibility thin wrapper ────────────────────────────────

@frappe.whitelist()
def submit_assignment(assignment_name=None, submission_file=None):
    """Thin wrapper kept for frontend backward-compatibility.

    DEPRECATED: migrate callers to submit_student_assignment().
    Delegates to the new submit_student_assignment() function.
    """
    return submit_student_assignment(
        assignment=assignment_name,
        submission_file=submission_file,
    )


# ═══════════════════════════════════════════════════════════════════════════
# LEGACY FUNCTIONS  (Assessment Plan based — kept for safe migration)
# Renamed with _legacy suffix. Do NOT call these from new code.
# ═══════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_assignments_legacy():
    """LEGACY: Get assignment-type Assessment Plans for the student.

    Replaced by get_student_assignments().
    """
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

        course_name = frappe.db.get_value("Course", p.course, "course_name") or p.course
        p["title"] = p.assessment_name or course_name
        p["course_name"] = course_name
        p["due_date"] = str(p.schedule_date) if p.schedule_date else ""
        p["description"] = p.assessment_name or ""
        p["assignment_file"] = None

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
def get_instructor_assignment_templates_legacy(course=None):
    """LEGACY: Get assignment-type Assessment Plans created by this instructor.

    Replaced by get_instructor_assignments().
    """
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
def create_assignment_template_legacy(data=None):
    """LEGACY: Create Assessment Plan based assignments.

    Replaced by create_assignment().
    """
    if not data:
        frappe.throw(_("No data provided"))

    import json
    if isinstance(data, str):
        data = json.loads(data)

    instructor = _get_instructor_for_user()
    if not instructor:
        frappe.throw(_("No instructor record found for the logged-in user"))

    title = (data.get("title") or "").strip()
    course = (data.get("course") or "").strip()
    if not title:
        frappe.throw(_("Title is required"))
    if not course:
        frappe.throw(_("Course is required"))
    if not frappe.db.exists("Course", course):
        match = frappe.db.get_value("Course", {"course_name": course}, "name")
        if not match:
            frappe.throw(_("Course '{0}' not found").format(course))
        course = match

    schedule_date = data.get("due_date") or data.get("deadline") or frappe.utils.today()

    course_doc = frappe.get_doc("Course", course)
    grading_scale = course_doc.default_grading_scale
    if not grading_scale:
        grading_scale = frappe.db.get_value("Grading Scale", {}, "name")
    if not grading_scale:
        frappe.throw(_(
            "No Grading Scale found. Set a default grading scale on the Course "
            "or create at least one Grading Scale."
        ))

    assessment_group = (
        data.get("assessment_group")
        or frappe.db.get_value("Assessment Group", {"assessment_group_name": "Assignments", "is_group": 0}, "name")
        or frappe.db.get_value("Assessment Group", {"is_group": 0}, "name")
    )
    if not assessment_group:
        frappe.throw(_(
            "No leaf Assessment Group found. Please create an Assessment Group "
            "(e.g. 'Assignments') under your root assessment group first."
        ))

    max_score = float(data.get("max_score") or 100)
    criteria_rows = []
    if course_doc.assessment_criteria:
        for cc in course_doc.assessment_criteria:
            weightage = float(cc.weightage or 0)
            row_score = round((weightage / 100.0) * max_score, 2) if weightage else max_score
            criteria_rows.append({
                "assessment_criteria": cc.assessment_criteria,
                "maximum_score": row_score,
            })
    if not criteria_rows:
        fallback = frappe.db.get_value("Assessment Criteria", {}, "name")
        if not fallback:
            frappe.throw(_(
                "Course '{0}' has no assessment criteria and no Assessment "
                "Criteria records exist. Add at least one before creating "
                "assignments."
            ).format(course))
        criteria_rows.append({
            "assessment_criteria": fallback,
            "maximum_score": max_score,
        })

    assign_to = (data.get("assign_to") or "").strip()
    explicit_group = (data.get("student_group") or "").strip()

    target_groups = []
    if assign_to == "All Enrolled":
        groups = get_instructor_student_groups(course=course)
        target_groups = [g["name"] if isinstance(g, dict) else g.name for g in groups]
        if not target_groups:
            frappe.throw(_(
                "No student groups found for course '{0}' that you are assigned to. "
                "Either create/join a student group or pick 'Specific Group'."
            ).format(course))
    else:
        if not explicit_group:
            frappe.throw(_("Student Group is required when not assigning to all enrolled"))
        if not frappe.db.exists("Student Group", explicit_group):
            frappe.throw(_("Student Group '{0}' not found").format(explicit_group))
        target_groups = [explicit_group]

    description = data.get("description") or ""
    assignment_file = data.get("assignment_file") or ""
    created = []

    for sg in target_groups:
        try:
            plan = frappe.get_doc({
                "doctype": "Assessment Plan",
                "assessment_name": title,
                "course": course,
                "student_group": sg,
                "assessment_group": assessment_group,
                "grading_scale": grading_scale,
                "schedule_date": schedule_date,
                "from_time": "00:00:00",
                "to_time": "23:59:00",
                "maximum_assessment_score": max_score,
                "examiner": instructor.name,
                "assessment_criteria": criteria_rows,
            })
            plan.insert()

            if description:
                plan.add_comment("Comment", text=description)

            if assignment_file:
                try:
                    frappe.get_doc({
                        "doctype": "File",
                        "file_url": assignment_file,
                        "attached_to_doctype": "Assessment Plan",
                        "attached_to_name": plan.name,
                    }).insert(ignore_permissions=True)
                except Exception:
                    frappe.log_error(
                        title="create_assignment_template_legacy: file attach failed",
                        message=frappe.get_traceback(),
                    )

            created.append(plan.name)
        except frappe.DuplicateEntryError:
            frappe.log_error(
                title="create_assignment_template_legacy: duplicate skipped",
                message=f"Duplicate Assessment Plan for group {sg}",
            )
            continue

    if not created:
        frappe.throw(_("No assignments were created. Please check the inputs and try again."))

    return {
        "success": True,
        "created": created,
        "count": len(created),
        "name": created[0],
    }


@frappe.whitelist()
def publish_assignment_template_legacy(template_name=None):
    """LEGACY: Submit (publish) an assignment Assessment Plan.

    Replaced by publish_assignment().
    """
    if not template_name:
        frappe.throw(_("Template name is required"))

    plan = frappe.get_doc("Assessment Plan", template_name)
    plan.submit()

    return {"success": True, "name": plan.name}


@frappe.whitelist()
def get_template_submissions_legacy(template_name=None):
    """LEGACY: Get student submissions (Assessment Results) for an assignment.

    Replaced by get_assignment_detail().
    """
    if not template_name:
        return []

    return frappe.get_all(
        "Assessment Result",
        filters={"assessment_plan": template_name},
        fields=[
            "name", "student", "student_name", "total_score",
            "grade", "docstatus", "comment"
        ],
        order_by="student_name asc"
    )


@frappe.whitelist()
def grade_assignment_legacy(assignment_name=None, score=None, remarks=""):
    """LEGACY: Grade a student's assignment (Assessment Result).

    Replaced by grade_submission().
    """
    if not assignment_name:
        frappe.throw(_("Assignment name is required"))

    result = frappe.get_doc("Assessment Result", assignment_name)
    if result.docstatus == 1:
        frappe.throw(_("Result already submitted"))

    if result.details:
        for detail in result.details:
            detail.score = float(score) if score else 0

    result.total_score = float(score) if score else 0
    result.comment = remarks
    result.save()

    return {"success": True, "name": result.name}
