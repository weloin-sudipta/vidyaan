import json

import frappe
from frappe import _
from frappe.utils import today, getdate

from vidyaan.api_folder.profile import _get_instructor_for_user


def _build_class_payload(schedules, instructor, target_date):
    """Shared serializer for the schedule rows."""
    classes = []
    for s in schedules:
        course_name = (
            frappe.db.get_value("Course", s.course, "course_name") or s.course
        )
        group_name = (
            frappe.db.get_value("Student Group", s.student_group, "student_group_name")
            or s.student_group
        )
        program = s.program or frappe.db.get_value(
            "Student Group", s.student_group, "program"
        ) or ""

        students = frappe.get_all(
            "Student Group Student",
            filters={"parent": s.student_group, "active": 1},
            fields=["student", "student_name"],
            ignore_permissions=True,
        )

        # Attendance status for THIS schedule's date — never mix dates
        schedule_date = (
            str(s.schedule_date) if s.schedule_date else target_date
        )
        for st in students:
            att = frappe.db.get_value(
                "Student Attendance",
                {
                    "student": st.student,
                    "date": schedule_date,
                    "student_group": s.student_group,
                },
                "status",
            )
            st["status"] = att.lower() if att else ""

        classes.append({
            "name": s.name,
            "course": s.course,
            "course_name": course_name,
            "student_group": s.student_group,
            "group_name": group_name,
            "program": program,
            "instructor": instructor.name,
            "instructor_name": s.instructor_name or instructor.instructor_name,
            "from_time": str(s.from_time) if s.from_time else "",
            "to_time": str(s.to_time) if s.to_time else "",
            "room": s.room or "",
            "schedule_date": schedule_date,
            "total_students": len(students),
            "students": students,
        })
    return classes


@frappe.whitelist()
def get_my_classes(date=None):
    """Get class schedule for the logged-in instructor for the given date.

    Args:
        date: ISO date (YYYY-MM-DD). Defaults to today. NEVER falls back
              to a different date — if there are no classes that day, the
              `classes` list is empty. The response also includes
              `latest_available_date` so the UI can offer an explicit
              "view latest" jump instead of a silent date swap.
    """
    instructor = _get_instructor_for_user()
    if not instructor:
        return {"classes": [], "instructor": None, "date": None, "latest_available_date": None}

    target_date = str(getdate(date or today()))

    schedules = frappe.get_all(
        "Course Schedule",
        filters={
            "instructor": instructor.name,
            "schedule_date": target_date,
        },
        fields=[
            "name", "student_group", "course", "instructor",
            "instructor_name", "from_time", "to_time", "room",
            "schedule_date", "program",
        ],
        order_by="from_time asc",
        ignore_permissions=True,
    )

    classes = _build_class_payload(schedules, instructor, target_date)

    # Surface the latest available date so the UI can offer it as an opt-in
    latest_row = frappe.db.sql(
        """
        SELECT MAX(schedule_date) FROM `tabCourse Schedule`
        WHERE instructor = %s AND schedule_date <= %s
        """,
        (instructor.name, target_date),
        as_list=True,
    )
    latest_available_date = (
        str(latest_row[0][0]) if latest_row and latest_row[0][0] else None
    )

    return {
        "classes": classes,
        "instructor": instructor.instructor_name,
        "date": target_date,
        "latest_available_date": latest_available_date,
    }


@frappe.whitelist()
def mark_attendance_bulk(course_schedule=None, students=None):
    """Mark attendance for multiple students against ONE course schedule.

    The attendance date is derived from the course schedule's own
    `schedule_date` so the date and the schedule are always consistent.
    Existing rows are looked up by (student, course_schedule, date) so
    re-marking the same schedule on a different day creates a new row
    instead of overwriting the old one.
    """
    if not course_schedule or not students:
        frappe.throw(_("Course schedule and students are required"))

    if isinstance(students, str):
        students = json.loads(students)

    if not frappe.db.exists("Course Schedule", course_schedule):
        frappe.throw(_("Course Schedule not found"))

    cs = frappe.get_doc("Course Schedule", course_schedule)
    attendance_date = str(cs.schedule_date) if cs.schedule_date else today()

    success = []
    failed = []

    for st in students:
        student_id = st.get("student")
        status = st.get("status", "Present")
        if not student_id:
            continue

        try:
            existing = frappe.db.get_value(
                "Student Attendance",
                {
                    "student": student_id,
                    "course_schedule": course_schedule,
                    "date": attendance_date,
                },
                "name",
            )

            if existing:
                # If submitted, we can still set status via db_set without re-validating
                existing_doc = frappe.get_doc("Student Attendance", existing)
                if existing_doc.docstatus == 1:
                    existing_doc.db_set("status", status, update_modified=True)
                else:
                    existing_doc.status = status
                    existing_doc.save(ignore_permissions=True)
                    if existing_doc.docstatus == 0:
                        existing_doc.submit()
                success.append(student_id)
            else:
                att = frappe.get_doc({
                    "doctype": "Student Attendance",
                    "student": student_id,
                    "student_group": cs.student_group,
                    "course_schedule": course_schedule,
                    "date": attendance_date,
                    "status": status,
                    "company": getattr(cs, "company", "") or "",
                })
                att.insert(ignore_permissions=True)
                att.submit()
                success.append(student_id)

        except Exception as e:
            frappe.log_error(
                title=f"mark_attendance_bulk: {student_id}",
                message=frappe.get_traceback(),
            )
            failed.append({"student": student_id, "error": str(e)})

    return {
        "success": success,
        "failed": failed,
        "total": len(students),
        "marked": len(success),
        "date": attendance_date,
    }
