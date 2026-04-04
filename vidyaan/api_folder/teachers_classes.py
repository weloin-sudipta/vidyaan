import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_instructor_for_user


@frappe.whitelist()
def get_my_classes():
    """Get today's class schedule for the logged-in instructor."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return {"classes": []}

    schedules = frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor.name,
            "schedule_date": frappe.utils.today()
        },
        fields=[
            "name", "student_group", "course", "instructor",
            "from_time", "to_time", "room", "schedule_date"
        ],
        order_by="from_time asc"
    )

    classes = []
    for s in schedules:
        course_name = frappe.db.get_value("Course", s.course, "course_name") or s.course
        group_name = frappe.db.get_value("Student Group", s.student_group, "student_group_name") or s.student_group

        # Get students in this group
        students = frappe.get_all(
            "Student Group Student",
            filters={"parent": s.student_group, "active": 1},
            fields=["student", "student_name"]
        )

        # Check attendance status for each student
        for st in students:
            att = frappe.db.get_value(
                "Student Attendance",
                {"student": st.student, "date": frappe.utils.today(), "student_group": s.student_group},
                "status"
            )
            st["status"] = att.lower() if att else ""

        classes.append({
            "name": s.name,
            "course": s.course,
            "course_name": course_name,
            "student_group": s.student_group,
            "group_name": group_name,
            "from_time": str(s.from_time) if s.from_time else "",
            "to_time": str(s.to_time) if s.to_time else "",
            "room": s.room or "",
            "students": students
        })

    return {"classes": classes}


@frappe.whitelist()
def mark_attendance_bulk(course_schedule=None, students=None):
    """Mark attendance for multiple students at once."""
    if not course_schedule or not students:
        frappe.throw(_("Course schedule and students are required"))

    import json
    if isinstance(students, str):
        students = json.loads(students)

    # Validate course schedule exists
    if not frappe.db.exists("Course Schedule", course_schedule):
        frappe.throw(_("Course Schedule not found"))

    cs = frappe.get_doc("Course Schedule", course_schedule)

    success = []
    failed = []

    for st in students:
        student_id = st.get("student")
        status = st.get("status", "Present")

        if not student_id:
            continue

        try:
            # Check if attendance already exists for today
            existing = frappe.db.get_value(
                "Student Attendance",
                {"student": student_id, "date": frappe.utils.today(), "student_group": cs.student_group},
                "name"
            )

            if existing:
                # Update existing
                frappe.db.set_value("Student Attendance", existing, "status", status)
                success.append(student_id)
            else:
                # Create new
                att = frappe.get_doc({
                    "doctype": "Student Attendance",
                    "student": student_id,
                    "student_group": cs.student_group,
                    "course_schedule": course_schedule,
                    "date": frappe.utils.today(),
                    "status": status,
                    "company": cs.company if hasattr(cs, "company") and cs.company else ""
                })
                att.insert(ignore_permissions=True)
                att.submit()
                success.append(student_id)

        except Exception as e:
            frappe.log_error(f"Attendance failed for {student_id}: {e}")
            failed.append({"student": student_id, "error": str(e)})

    return {
        "success": success,
        "failed": failed,
        "total": len(students),
        "marked": len(success)
    }
