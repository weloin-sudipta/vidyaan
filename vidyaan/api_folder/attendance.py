import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user


@frappe.whitelist()
def get_attendance(month=None, year=None):
    """Get attendance records for the logged-in student for a given month/year.
    Returns a dict keyed by 'YYYY-M-D' (JS-compatible: 0-based month, no padding)
    with values 'P' (Present), 'A' (Absent), or 'L' (Leave).
    """
    student = _get_student_for_user()
    if not student:
        return {}

    if not month and month != 0:
        from datetime import date
        today = date.today()
        month = today.month - 1  # JS sends 0-based
        year = today.year

    month = int(month)
    year = int(year)

    # Frontend sends JS 0-based month (0=Jan, 3=Apr), convert to 1-based
    actual_month = month + 1
    if actual_month > 12:
        actual_month = 1
        year += 1

    start_date = f"{year}-{actual_month:02d}-01"
    if actual_month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{actual_month + 1:02d}-01"

    records = frappe.get_all(
        "Student Attendance",
        filters=[
            ["student", "=", student.name],
            ["date", ">=", start_date],
            ["date", "<", end_date],
            ["docstatus", "=", 1]
        ],
        fields=["date", "status"],
        ignore_permissions=True,
    )

    # Build map with JS-compatible keys: "YYYY-M-D" (0-based month, no zero-padding)
    attendance_map = {}
    for r in records:
        d = r.date
        if isinstance(d, str):
            from datetime import datetime
            d = datetime.strptime(d, "%Y-%m-%d").date()
        # Key: "YYYY-{0-based month}-{day}" to match frontend lookup
        key = f"{d.year}-{d.month - 1}-{d.day}"
        status = r.status
        if status == "Present":
            attendance_map[key] = "P"
        elif status == "Absent":
            attendance_map[key] = "A"
        elif status == "Leave":
            attendance_map[key] = "L"
        else:
            attendance_map[key] = status[0].upper() if status else "P"

    return attendance_map


@frappe.whitelist()
def get_attendance_summary():
    """Get overall attendance summary for the logged-in student.

    Returns:
    - rate, total_present, total_absent, total_leave (for profile tab stat cards)
    - months: [{name, present, absent, leave, percent}] (for profile tab table)
    """
    student = _get_student_for_user()
    if not student:
        return {
            "total": 0, "present": 0, "absent": 0, "leave": 0,
            "percentage": 0, "rate": 0,
            "total_present": 0, "total_absent": 0, "total_leave": 0,
            "months": [],
        }

    total = frappe.db.count("Student Attendance", {
        "student": student.name, "docstatus": 1
    })
    present = frappe.db.count("Student Attendance", {
        "student": student.name, "status": "Present", "docstatus": 1
    })
    absent = frappe.db.count("Student Attendance", {
        "student": student.name, "status": "Absent", "docstatus": 1
    })
    leave = frappe.db.count("Student Attendance", {
        "student": student.name, "status": "Leave", "docstatus": 1
    })

    percentage = round((present / total * 100), 1) if total > 0 else 0

    # Build monthly breakdown for the attendance register table
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    records = frappe.get_all(
        "Student Attendance",
        filters={"student": student.name, "docstatus": 1},
        fields=["date", "status"],
        order_by="date asc",
        ignore_permissions=True,
    )

    monthly = {}  # key: "YYYY-MM"
    for r in records:
        d = r.date
        if isinstance(d, str):
            from datetime import datetime
            d = datetime.strptime(d, "%Y-%m-%d").date()
        key = f"{d.year}-{d.month:02d}"
        if key not in monthly:
            monthly[key] = {"present": 0, "absent": 0, "leave": 0}
        if r.status == "Present":
            monthly[key]["present"] += 1
        elif r.status == "Absent":
            monthly[key]["absent"] += 1
        else:
            monthly[key]["leave"] += 1

    months = []
    for ym in sorted(monthly.keys()):
        year_part, month_part = ym.split("-")
        m = monthly[ym]
        month_total = m["present"] + m["absent"] + m["leave"]
        pct = round((m["present"] / month_total * 100), 1) if month_total > 0 else 0
        months.append({
            "name": f"{month_names[int(month_part) - 1]} {year_part}",
            "present": m["present"],
            "absent": m["absent"],
            "leave": m["leave"],
            "percent": pct,
        })

    return {
        "total": total,
        "present": present,
        "absent": absent,
        "leave": leave,
        "percentage": percentage,
        "rate": percentage,
        "total_present": present,
        "total_absent": absent,
        "total_leave": leave,
        "months": months,
    }
