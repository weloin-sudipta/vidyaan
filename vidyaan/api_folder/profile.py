import frappe
from frappe import _
import json


def _get_user_company():
    """Get the company for the current user from User Permission."""
    company = frappe.defaults.get_user_default("Company")
    if not company:
        companies = frappe.get_all(
            "User Permission",
            filters={"user": frappe.session.user, "allow": "Company"},
            pluck="for_value",
            limit=1
        )
        company = companies[0] if companies else None
    return company


def _get_student_for_user(user=None):
    """Resolve User → Student record."""
    user = user or frappe.session.user
    students = frappe.get_all(
        "Student",
        filters={"student_email_id": user},
        fields=["name", "first_name", "last_name", "student_email_id", "image",
                "date_of_birth", "gender", "blood_group", "student_mobile_number",
                "address_line_1", "city", "state", "company"],
        limit=1
    )
    return students[0] if students else None


def _get_instructor_for_user(user=None):
    """Resolve User → Employee → Instructor."""
    user = user or frappe.session.user
    employees = frappe.get_all("Employee", filters={"user_id": user}, pluck="name")
    if employees:
        instructors = frappe.get_all(
            "Instructor",
            filters={"employee": ["in", employees]},
            fields=["name", "instructor_name", "employee", "company", "status"],
            limit=1
        )
        if instructors:
            return instructors[0]
    return None


def _get_primary_role():
    """Determine the user's primary Vidyaan role."""
    roles = frappe.get_roles()
    if "System Manager" in roles or "Administrator" in roles:
        return "admin"
    if "Institute Admin" in roles:
        return "admin"
    if "Instructor" in roles:
        return "teacher"
    # Check if user has a student record
    if _get_student_for_user():
        return "student"
    return "other"


@frappe.whitelist()
def get_user_info():
    """Returns basic user info + role for auth/profile bootstrapping."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)

    user_doc = frappe.get_doc("User", user)
    role = _get_primary_role()

    return {
        "email": user_doc.email,
        "first_name": user_doc.first_name or "",
        "last_name": user_doc.last_name or "",
        "full_name": user_doc.full_name or "",
        "user_image": user_doc.user_image or "",
        "role": role
    }


@frappe.whitelist()
def get_profile():
    """Returns detailed profile based on user's role (student or teacher)."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)

    role = _get_primary_role()
    user_doc = frappe.get_doc("User", user)

    base = {
        "email": user_doc.email,
        "first_name": user_doc.first_name or "",
        "last_name": user_doc.last_name or "",
        "full_name": user_doc.full_name or "",
        "user_image": user_doc.user_image or "",
        "role": role
    }

    if role == "student":
        student = _get_student_for_user(user)
        if student:
            # Get full student doc for all fields
            student_doc = frappe.get_doc("Student", student.name)
            student_name = f"{student.first_name} {student.last_name or ''}".strip()

            base.update({
                "student_id": student.name,
                "student_name": student_name,
                "date_of_birth": str(student.date_of_birth) if student.date_of_birth else "",
                "gender": student.gender or "",
                "blood_group": student.blood_group or "",
                "phone": student.student_mobile_number or "",
                "mobile_number": student.student_mobile_number or "",
                "address_line_1": student.address_line_1 or "",
                "address_line_2": getattr(student_doc, "address_line_2", "") or "",
                "city": student.city or "",
                "state": student.state or "",
                "country": getattr(student_doc, "country", "") or "India",
                "pincode": getattr(student_doc, "pincode", "") or "",
                "company": student.company or "",
                "photo_url": student.image or user_doc.user_image or "",
                "nationality": getattr(student_doc, "nationality", "") or "",
                "religion": getattr(student_doc, "religion", "") or "",
                "category": getattr(student_doc, "student_category", "") or "",
                "caste": "",
                "hostel_facility": "",
                "joining_date": str(student_doc.joining_date) if student_doc.joining_date else "",
            })

            # Get enrollment info
            enrollment = frappe.get_all(
                "Program Enrollment",
                filters={"student": student.name, "docstatus": 1},
                fields=["program", "academic_year", "academic_term", "enrollment_date"],
                order_by="creation desc",
                limit=1
            )
            if enrollment:
                base["program"] = enrollment[0].program
                base["program_name"] = frappe.db.get_value("Program", enrollment[0].program, "program_name") or enrollment[0].program
                base["academic_year"] = enrollment[0].academic_year or ""
                base["academic_term"] = enrollment[0].academic_term or ""
                base["program_session"] = enrollment[0].academic_year or ""
                base["program_enrollment_date"] = str(enrollment[0].enrollment_date) if enrollment[0].enrollment_date else ""

            # Get guardians
            guardians = []
            for g in (student_doc.get("guardians") or []):
                guardian_name = g.guardian_name or ""
                if not guardian_name and g.guardian:
                    guardian_name = frappe.db.get_value("Guardian", g.guardian, "guardian_name") or ""
                guardians.append({
                    "guardian": g.guardian or "",
                    "guardian_name": guardian_name,
                    "relation": g.relation or "",
                    "email": frappe.db.get_value("Guardian", g.guardian, "email_address") if g.guardian else "",
                    "mobile": frappe.db.get_value("Guardian", g.guardian, "mobile_number") if g.guardian else "",
                })
            base["guardians"] = guardians
            if guardians:
                base["parent_mobile_number"] = guardians[0].get("mobile", "")

    elif role == "teacher":
        instructor = _get_instructor_for_user(user)
        if instructor:
            base.update({
                "instructor_id": instructor.name,
                "instructor_name": instructor.instructor_name or "",
                "employee": instructor.employee or "",
                "company": instructor.company or "",
                "status": instructor.status or ""
            })

    return base


@frappe.whitelist()
def update_profile(data=None):
    """Update the current user's profile fields."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Not logged in"), frappe.AuthenticationError)

    if not data:
        frappe.throw(_("No data provided"))

    if isinstance(data, str):
        data = json.loads(data)

    allowed_user_fields = ["first_name", "last_name", "user_image"]
    user_doc = frappe.get_doc("User", user)
    changed = False

    for field in allowed_user_fields:
        if field in data and data[field] != user_doc.get(field):
            user_doc.set(field, data[field])
            changed = True

    if changed:
        user_doc.save(ignore_permissions=True)

    # Update student fields if applicable
    student = _get_student_for_user(user)
    if student:
        student_doc = frappe.get_doc("Student", student.name)
        student_fields = ["student_mobile_number", "address_line_1", "city", "state", "blood_group"]
        student_changed = False

        for field in student_fields:
            if field in data and data[field] != student_doc.get(field):
                student_doc.set(field, data[field])
                student_changed = True

        if student_changed:
            student_doc.save(ignore_permissions=True)

    return {"success": True}
