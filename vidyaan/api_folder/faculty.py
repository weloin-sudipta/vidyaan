import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_user_company


@frappe.whitelist()
def get_all_faculty_data():
    """Get all instructors for the current institute.

    Returns a list of objects shaped for the frontend:
    [{ instructor: {name, instructor_name, status, ...}, logs: [{course, program, academic_term}] }]
    """
    company = _get_user_company()

    filters = {}
    if company:
        filters["company"] = company

    instructors = frappe.get_all(
        "Instructor",
        filters=filters,
        fields=["name", "instructor_name", "employee", "company",
                "department", "image", "status", "naming_series"],
        order_by="instructor_name asc",
        ignore_permissions=True,
    )

    result = []
    for inst in instructors:
        # Get employee details for designation
        designation = ""
        phone = ""
        email = ""
        if inst.employee:
            emp = frappe.db.get_value(
                "Employee", inst.employee,
                ["designation", "department", "cell_number", "user_id", "image"],
                as_dict=True
            )
            if emp:
                designation = emp.designation or ""
                inst["department"] = emp.department or inst.get("department", "")
                phone = emp.cell_number or ""
                email = emp.user_id or ""
                inst["image"] = inst.image or emp.image or ""

        # Get courses taught via Instructor Course Mapping
        course_mappings = frappe.get_all(
            "Instructor Course Mapping",
            filters={"parent": inst.name, "parenttype": "Instructor"},
            fields=["course", "course_name", "program"],
            ignore_permissions=True,
        )

        # Get academic term from active groups where this instructor teaches
        academic_term = ""
        schedules = frappe.get_all(
            "Course Schedule",
            filters={"instructor": inst.name},
            fields=["student_group"],
            limit=1,
            ignore_permissions=True,
        )
        if schedules:
            group_term = frappe.db.get_value(
                "Student Group", schedules[0].student_group, "academic_term"
            )
            academic_term = group_term or ""

        # Build logs array from course mappings (what frontend expects)
        logs = []
        for cm in course_mappings:
            course_name = cm.course_name or frappe.db.get_value("Course", cm.course, "course_name") or cm.course
            logs.append({
                "course": course_name,
                "program": cm.program or "",
                "academic_term": academic_term,
            })

        result.append({
            "instructor": {
                "name": inst.name,
                "instructor_name": inst.instructor_name,
                "status": inst.status or "Active",
                "naming_series": inst.naming_series or "",
                "department": inst.department or "",
                "company": inst.company or "",
                "image": inst.image or "",
                "designation": designation,
                "phone": phone,
                "email": email,
            },
            "logs": logs,
        })

    return result
