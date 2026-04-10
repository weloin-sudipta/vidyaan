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

    # Attendance pending: course schedules for today without attendance
    attendance_pending = []
    schedules_today = frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor.name,
            "schedule_date": frappe.utils.today()
        },
        fields=["name as schedule_id", "course", "student_group as batch", "schedule_date"],
        ignore_permissions=True
    )
    
    for sch in schedules_today:
        sch["course_name"] = frappe.db.get_value("Course", sch["course"], "course_name") or sch["course"]
        sch["total_students"] = frappe.db.count("Student Group Student", {"parent": sch["batch"], "active": 1})
        # Check if attendance exists for this schedule
        has_attendance = frappe.db.exists("Student Attendance", {
            "course_schedule": sch["schedule_id"],
            "docstatus": 1
        })
        # Also check if it's marked manually via tool (sometimes docstatus 1 is not the only check, but we rely on docstatus 1 student attendance)
        if not has_attendance:
            attendance_pending.append(sch)

    # Mark entry pending: submitted assessment plans with missing results
    mark_entry_pending = []
    plans = frappe.get_all(
        "Assessment Plan",
        filters={
            "examiner": instructor.name,
            "docstatus": 1,
            "schedule_date": ["<=", frappe.utils.today()]
        },
        fields=["name as assessment_id", "assessment_name as assessment_title", "course", "student_group", "schedule_date as assessment_date"],
        ignore_permissions=True,
    )
    for plan in plans:
        total_students = frappe.db.count("Student Group Student", {"parent": plan.student_group, "active": 1})
        marks_entered_count = frappe.db.count("Assessment Result", {"assessment_plan": plan.assessment_id, "docstatus": 1})
        if marks_entered_count < total_students:
            plan["total_students"] = total_students
            plan["marks_entered_count"] = marks_entered_count
            plan["pending_count"] = total_students - marks_entered_count
            mark_entry_pending.append(plan)

    from vidyaan.api_folder.applications import get_teacher_pending_applications
    applications_pending = get_teacher_pending_applications()

    return {
        "success": True,
        "attendance_pending": attendance_pending,
        "mark_entry_pending": mark_entry_pending,
        "review_pending": [],
        "application_pending": applications_pending
    }
