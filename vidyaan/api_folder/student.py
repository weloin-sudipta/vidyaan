import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user, _get_user_company


@frappe.whitelist()
def get_student_by_institute(user_email=None):
    """Get students by institute with enrollment details for teacher students page."""
    company = _get_user_company()
    if not company:
        return []

    filters = {"company": company}
    if user_email:
        filters["student_email_id"] = user_email

    students = frappe.get_all(
        "Student",
        filters=filters,
        fields=["name", "first_name", "last_name", "student_email_id",
                "image", "gender", "company"],
        order_by="first_name asc",
        ignore_permissions=True,
    )

    # Enrich with enrollment data (teacher students page expects these)
    for s in students:
        s["student"] = s["name"]
        s["student_name"] = f"{s['first_name']} {s.get('last_name', '')}".strip()
        enrollment = frappe.get_all(
            "Program Enrollment",
            filters={"student": s["name"], "docstatus": 1},
            fields=["program", "academic_year", "academic_term", "enrollment_date", "name"],
            order_by="creation desc",
            limit=1,
            ignore_permissions=True,
        )
        if enrollment:
            s["program"] = enrollment[0].program
            s["academic_year"] = enrollment[0].academic_year or ""
            s["academic_term"] = enrollment[0].academic_term or ""
            s["enrollment_date"] = str(enrollment[0].enrollment_date) if enrollment[0].enrollment_date else ""
        else:
            s["program"] = ""
            s["academic_year"] = ""
            s["academic_term"] = ""
            s["enrollment_date"] = ""

    return students


@frappe.whitelist()
def get_student_dashboard_data():
    """Aggregated dashboard data for the logged-in student."""
    student = _get_student_for_user()
    if not student:
        return {"error": "No student record found"}

    # Attendance summary
    total_att = frappe.db.count("Student Attendance", {
        "student": student.name, "docstatus": 1
    })
    present = frappe.db.count("Student Attendance", {
        "student": student.name, "status": "Present", "docstatus": 1
    })
    absent = frappe.db.count("Student Attendance", {
        "student": student.name, "status": "Absent", "docstatus": 1
    })
    leave_days = total_att - present - absent

    # Get student groups
    groups = frappe.get_all(
        "Student Group Student",
        filters={"student": student.name, "active": 1},
        pluck="parent"
    )

    # Upcoming exams
    upcoming_exams = []
    if groups:
        upcoming_exams = frappe.get_all(
            "Assessment Plan",
            filters={
                "student_group": ["in", groups],
                "docstatus": 1,
                "schedule_date": [">=", frappe.utils.today()]
            },
            fields=["name", "assessment_name", "course", "schedule_date",
                    "assessment_group", "from_time", "to_time"],
            order_by="schedule_date asc",
            limit=5
        )

    # Pending assignments (assessment plans with group=Assignments, no result yet)
    pending_assignments = []
    if groups:
        assignment_plans = frappe.get_all(
            "Assessment Plan",
            filters={
                "student_group": ["in", groups],
                "docstatus": 1,
                "assessment_group": ["like", "%Assignment%"]
            },
            fields=["name", "assessment_name", "course", "schedule_date"],
            order_by="schedule_date desc",
            limit=5
        )
        for ap in assignment_plans:
            has_result = frappe.db.exists("Assessment Result", {
                "student": student.name,
                "assessment_plan": ap.name,
                "docstatus": 1
            })
            if not has_result:
                pending_assignments.append(ap)

    # Recent notices
    notices = frappe.get_all(
        "Publication",
        filters={"status": "Approved", "docstatus": 1},
        fields=["name", "title", "type", "publish_date"],
        order_by="publish_date desc",
        limit=5
    )

    # Enrollment info
    enrollment = frappe.get_all(
        "Program Enrollment",
        filters={"student": student.name, "docstatus": 1},
        fields=["program", "academic_year", "academic_term"],
        order_by="creation desc",
        limit=1
    )

    program_name = enrollment[0].program if enrollment else ""
    academic_year = enrollment[0].academic_year if enrollment else ""
    academic_term = enrollment[0].academic_term if enrollment else ""

    # Courses from enrolled program
    courses = []
    if program_name:
        program_courses = frappe.get_all(
            "Program Course",
            filters={"parent": program_name},
            fields=["course", "required"],
        )
        for pc in program_courses:
            course_name = frappe.db.get_value("Course", pc.course, "course_name") or pc.course
            courses.append({
                "name": course_name,
                "code": pc.course,
                "id": pc.course,
                "credits": 1,
            })

    # Today's classes
    today_classes = []
    if groups:
        raw_classes = frappe.get_all(
            "Course Schedule",
            filters={
                "student_group": ["in", groups],
                "schedule_date": frappe.utils.today()
            },
            fields=["course", "instructor_name", "from_time", "to_time", "room"],
            order_by="from_time asc"
        )
        for cls in raw_classes:
            course_name = frappe.db.get_value("Course", cls.course, "course_name") or cls.course
            from_time = str(cls.from_time)[:5] if cls.from_time else ""
            to_time = str(cls.to_time)[:5] if cls.to_time else ""
            today_classes.append({
                "subject": course_name,
                "teacher": cls.instructor_name or "",
                "startTime": from_time,
                "endTime": to_time,
                "room": cls.room or "",
                "type": "Lecture",
            })

    # Fees data
    fees_data = {"fees": [], "total_outstanding": 0, "currency": "INR"}
    try:
        default_currency = frappe.defaults.get_global_default("currency") or "USD"
        invoices = frappe.db.get_all(
            "Sales Invoice",
            filters={"student": student.name, "docstatus": ["!=", 2]},
            fields=["name", "posting_date", "due_date", "status", "grand_total", "outstanding_amount", "currency", "remarks", "customer_name", "fee_schedule"],
            order_by="posting_date desc"
        )
        
        total_outstanding = sum(inv.get("outstanding_amount", 0) for inv in invoices)
        
        fee_list = []
        for inv in invoices:
            fee_structure_name = ""
            if inv.get("fee_schedule"):
                fee_structure_name = frappe.db.get_value("Fee Schedule", inv.fee_schedule, "fee_structure") or ""
            fee_structure = fee_structure_name or inv.get("remarks", "")[:50] if inv.get("remarks") else f"Fee for {inv.customer_name}" if inv.get("customer_name") else "Tuition Fee"
            
            invoice_items = frappe.db.get_all(
                "Sales Invoice Item",
                filters={"parent": inv.name},
                fields=["item_name", "amount"]
            )
            breakout = [{"label": row.item_name or row.item_code or "Fee Component", "value": float(row.amount or 0)} for row in invoice_items]
            
            fee_list.append({
                "name": inv.name,
                "posting_date": inv.posting_date,
                "due_date": inv.due_date,
                "status": inv.status,
                "grand_total": float(inv.grand_total or 0),
                "outstanding_amount": float(inv.outstanding_amount or 0),
                "paid_amount": float(inv.grand_total or 0) - float(inv.outstanding_amount or 0),
                "currency": inv.currency,
                "fee_structure": fee_structure,
                "remarks": inv.remarks or "",
                "breakout": breakout
            })
        
        fees_data = {
            "fees": fee_list,
            "total_outstanding": float(total_outstanding),
            "currency": invoices[0].currency if invoices else default_currency
        }
    except Exception as e:
        frappe.log_error(f"Error fetching fees in dashboard: {str(e)}")

    # Wrap fees for the fees tab (expects dashboardData.fees.fees)
    fees = {
        "fees": fees_data["fees"],
        "total": sum(f.get("grand_total", 0) or 0 for f in fees_data["fees"]),
        "outstanding": fees_data["total_outstanding"],
    }

    # Format upcoming exams for frontend (expects: id, title, date, description, day, month)
    assessments = []
    for exam in upcoming_exams:
        schedule_date = exam.schedule_date
        if schedule_date:
            from datetime import datetime
            if isinstance(schedule_date, str):
                dt = datetime.strptime(schedule_date, "%Y-%m-%d")
            else:
                dt = schedule_date
            day = str(dt.day)
            month = dt.strftime("%b")
        else:
            day = ""
            month = ""

        course_name = frappe.db.get_value("Course", exam.course, "course_name") or exam.course
        assessments.append({
            "id": exam.name,
            "title": course_name,
            "subject": course_name,
            "date": str(exam.schedule_date) if exam.schedule_date else "",
            "description": exam.assessment_name or "",
            "day": day,
            "month": month,
            "from_time": str(exam.from_time) if exam.from_time else "",
            "to_time": str(exam.to_time) if exam.to_time else "",
            "assessment_group": exam.assessment_group or "",
        })

    student_name = f"{student.first_name} {student.last_name or ''}".strip()

    return {
        # Frontend expects "student_info" with these exact fields
        "student_info": {
            "name": student_name,
            "studentId": student.name,
            "program": program_name,
            "semester": academic_term or academic_year,
            "image": student.image or "",
        },
        # Also keep flat keys for backward compat
        "student": {
            "name": student.name,
            "first_name": student.first_name,
            "last_name": student.last_name or "",
            "image": student.image or "",
        },
        "program": program_name,
        "academic_year": academic_year,
        # Frontend expects "courses" array for program subjects
        "courses": courses,
        # Frontend expects "assessments" with id, title, date, day, month
        "assessments": assessments,
        # Also keep original keys
        "upcoming_exams": upcoming_exams,
        "pending_assignments": pending_assignments,
        "notices": notices,
        "today_classes": today_classes,
        # Frontend expects attendance with present_days, absent_days, leave_days, total_days
        "attendance": {
            "present_days": present,
            "absent_days": absent,
            "leave_days": leave_days,
            "total_days": total_att,
            # Also keep original keys
            "total": total_att,
            "present": present,
            "percentage": round((present / total_att * 100), 1) if total_att > 0 else 0,
        },
        # Frontend expects "fees"
        "fees": fees,
    }
