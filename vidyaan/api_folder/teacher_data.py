import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_instructor_for_user, _get_user_company


@frappe.whitelist()
def get_my_profile():
    """Get the logged-in instructor's profile and teaching info."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return None

    company = _get_user_company()

    # Get courses taught
    courses = frappe.get_all(
        "Instructor Course Mapping",
        filters={"parent": instructor.name, "parenttype": "Instructor"},
        fields=["course", "course_name", "program", "is_preferred"]
    )

    # Get student groups assigned
    groups = frappe.get_all(
        "Student Group Instructor",
        filters={"instructor": instructor.name},
        fields=["parent as student_group"]
    )
    group_names = [g.student_group for g in groups]

    group_details = []
    if group_names:
        group_details = frappe.get_all(
            "Student Group",
            filters={"name": ["in", group_names], "disabled": 0},
            fields=["name", "student_group_name", "program"]
        )

    # Employee details
    emp_data = {}
    if instructor.employee:
        emp_data = frappe.db.get_value(
            "Employee", instructor.employee,
            ["designation", "department", "cell_phone", "image"],
            as_dict=True
        ) or {}

    return {
        "instructor_id": instructor.name,
        "instructor_name": instructor.instructor_name,
        "company": instructor.company or company or "",
        "designation": emp_data.get("designation", ""),
        "department": emp_data.get("department", ""),
        "phone": emp_data.get("cell_phone", ""),
        "image": emp_data.get("image", ""),
        "courses": courses,
        "student_groups": group_details
    }


@frappe.whitelist()
def get_teacher_pending_tasks():
    """Get pending tasks for the instructor: attendance, grading, reviews."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return {"success": False, "message": "No instructor record found"}

    # Get instructor's student groups
    group_names = frappe.get_all(
        "Student Group Instructor",
        filters={"instructor": instructor.name},
        pluck="parent"
    )

    # Attendance pending: groups with no attendance for today
    attendance_pending = []
    if group_names:
        for gn in group_names:
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
        fields=["name", "assessment_name", "course", "student_group", "schedule_date"]
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
