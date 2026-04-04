import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user


@frappe.whitelist()
def get_student_schedule():
    """Get weekly timetable for the logged-in student from Course Schedule."""
    student = _get_student_for_user()
    if not student:
        return {"success": False, "message": "No student record found"}

    # Find student's active groups
    groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student.name, "active": 1},
        pluck="parent"
    )
    if not groups:
        return {"success": True, "timetable": {}, "student_group": ""}

    # Get all course schedules for these groups
    schedules = frappe.get_all(
        "Course Schedule",
        filters={"student_group": ["in", groups]},
        fields=[
            "name", "student_group", "course", "instructor",
            "instructor_name", "from_time", "to_time", "room",
            "schedule_date"
        ],
        order_by="from_time asc"
    )

    # Build day-wise timetable
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timetable = {}

    for s in schedules:
        if s.schedule_date:
            from datetime import datetime
            if isinstance(s.schedule_date, str):
                dt = datetime.strptime(s.schedule_date, "%Y-%m-%d")
            else:
                dt = s.schedule_date
            day = day_names[dt.weekday()]
        else:
            continue

        if day not in timetable:
            timetable[day] = []

        # Format times
        from_time = str(s.from_time) if s.from_time else ""
        to_time = str(s.to_time) if s.to_time else ""

        # Get course name
        course_name = frappe.db.get_value("Course", s.course, "course_name") or s.course

        instructor_name = s.instructor_name or ""
        if not instructor_name and s.instructor:
            instructor_name = frappe.db.get_value("Instructor", s.instructor, "instructor_name") or ""

        timetable[day].append({
            "name": s.name,
            "course": s.course,
            # Frontend uses "subject" and "teacher"
            "subject": course_name,
            "teacher": instructor_name,
            # Keep original keys for backward compat
            "courseName": course_name,
            "instructor": s.instructor or "",
            "instructorName": instructor_name,
            "room": s.room or "",
            "startTime": from_time[:5] if len(from_time) >= 5 else from_time,
            "endTime": to_time[:5] if len(to_time) >= 5 else to_time,
            "type": "Lecture"
        })

    # Sort each day by start time
    for day in timetable:
        timetable[day].sort(key=lambda x: x["startTime"])

    primary_group = groups[0] if groups else ""
    group_name = frappe.db.get_value("Student Group", primary_group, "student_group_name") if primary_group else ""

    return {
        "success": True,
        "timetable": timetable,
        "student_group": group_name or primary_group
    }
