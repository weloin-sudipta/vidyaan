import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_instructor_for_user, _get_user_company


@frappe.whitelist()
def get_my_profile():
    """Get the logged-in instructor's profile and teaching info.

    Returns nested structure for the teacher profile page:
    {
        user: { full_name, email, phone, gender, ... },
        instructor: { instructor_name, department, institute, status, image, instructor_log },
    }
    """
    instructor = _get_instructor_for_user()
    if not instructor:
        return None

    company = _get_user_company()
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    # ----------------------------
    # Courses (Instructor Log)
    # ----------------------------
    courses = frappe.get_all(
        "Instructor Course Mapping",
        filters={"parent": instructor.name, "parenttype": "Instructor"},
        fields=["course", "course_name", "program", "is_preferred"],
        ignore_permissions=True,
    )

    # Resolve course names if missing
    for c in courses:
        if not c.get("course_name"):
            c["course_name"] = (
                frappe.db.get_value("Course", c.get("course"), "course_name")
                or c.get("course")
            )

    # ----------------------------
    # Student Groups
    # ----------------------------
    groups = frappe.get_all(
        "Student Group Instructor",
        filters={"instructor": instructor.name},
        fields=["parent as student_group"],
        ignore_permissions=True,
    )

    group_names = [g.get("student_group") for g in groups if g.get("student_group")]

    group_details = []
    if group_names:
        group_details = frappe.get_all(
            "Student Group",
            filters={"name": ["in", group_names], "disabled": 0},
            fields=["name", "student_group_name", "program"],
            ignore_permissions=True,
        )

    # ----------------------------
    # Employee Details
    # ----------------------------
    emp_data = {}
    if instructor.employee:
        emp_data = frappe.db.get_value(
            "Employee",
            instructor.employee,
            ["designation", "department", "cell_number", "image"],
            as_dict=True,
        ) or {}

    # ----------------------------
    # Response
    # ----------------------------
    return {
        # Top-level (Backward Compatibility)
        "instructor_id": instructor.name,
        "instructor_name": instructor.instructor_name,
        "company": instructor.company or company or "",
        "designation": emp_data.get("designation", ""),
        "department": emp_data.get("department", instructor.get("department", "")),

        # ✅ FIXED HERE
        "phone": emp_data.get("cell_number", ""),

        "image": emp_data.get("image", instructor.get("image", "")),
        "courses": courses,
        "student_groups": group_details,

        # ----------------------------
        # User Info
        # ----------------------------
        "user": {
            "full_name": user_doc.full_name or "",
            "email": user_doc.email or "",
            "first_name": user_doc.first_name or "",
            "last_name": user_doc.last_name or "",
            "phone": user_doc.phone or "",
            "mobile_no": user_doc.mobile_no or "",
            "location": user_doc.location or "",
            "birth_date": str(user_doc.birth_date) if user_doc.birth_date else "",
            "gender": user_doc.gender or "",
            "language": user_doc.language or "",
            "time_zone": user_doc.time_zone or "",
            "last_login": str(user_doc.last_login) if user_doc.last_login else "",
            "last_active": str(user_doc.last_active) if user_doc.last_active else "",
            "user_type": user_doc.user_type or "",
            "user_image": user_doc.user_image or "",
            "roles": [{"role": r.role} for r in user_doc.get("roles", [])],
        },

        # ----------------------------
        # Instructor Info
        # ----------------------------
        "instructor": {
            "name": instructor.name,
            "instructor_name": instructor.instructor_name,
            "instructor_email": frappe.session.user,
            "department": emp_data.get("department", instructor.get("department", "")),
            "institute": instructor.company or company or "",
            "status": instructor.status or "Active",

            # Better fallback priority
            "image": (
                instructor.get("image")
                or emp_data.get("image")
                or user_doc.user_image
                or ""
            ),

            "instructor_log": courses,
        },
    }

@frappe.whitelist()
def get_teacher_pending_tasks():
    """Get pending tasks for the instructor: attendance, grading, reviews."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return {"success": False, "message": "No instructor record found",
                "attendance_pending": [], "mark_entry_pending": [], "review_pending": []}

    # Get instructor's student groups
    group_names = frappe.get_all(
        "Student Group Instructor",
        filters={"instructor": instructor.name},
        pluck="parent",
        ignore_permissions=True,
    )

    # Also get groups from Course Schedule
    schedule_groups = frappe.get_all(
        "Course Schedule",
        filters={"instructor": instructor.name},
        pluck="student_group",
        distinct=True,
        ignore_permissions=True,
    )
    all_groups = list(set(group_names + schedule_groups))

    # Attendance pending: groups with no attendance for today
    attendance_pending = []
    for gn in all_groups:
        has_attendance = frappe.db.exists("Student Attendance", {
            "student_group": gn,
            "date": frappe.utils.today(),
            "docstatus": 1
        })
        if not has_attendance:
            group_info = frappe.db.get_value(
                "Student Group", gn,
                ["student_group_name", "program"],
                as_dict=True
            )
            if group_info:
                attendance_pending.append({
                    "student_group": gn,
                    "group_name": group_info.student_group_name,
                    "program": group_info.program or ""
                })

    # Mark entry pending: submitted assessment plans with no results yet
    mark_entry_pending = []
    plans = frappe.get_all(
        "Assessment Plan",
        filters={
            "examiner": instructor.name,
            "docstatus": 1,
            "schedule_date": ["<=", frappe.utils.today()]
        },
        fields=["name", "assessment_name", "course", "student_group", "schedule_date"],
        ignore_permissions=True,
    )
    for plan in plans:
        result_count = frappe.db.count("Assessment Result", {
            "assessment_plan": plan.name, "docstatus": 1
        })
        if result_count == 0:
            mark_entry_pending.append(plan)

    return {
        "success": True,
        "attendance_pending": attendance_pending,
        "mark_entry_pending": mark_entry_pending,
        "review_pending": []
    }
