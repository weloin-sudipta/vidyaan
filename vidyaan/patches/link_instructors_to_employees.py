"""Patch: Heal Instructors that have no Employee link.

Background:
    The teacher login flow (vidyaan.api_folder.profile._get_instructor_for_user)
    resolves User → Employee.user_id → Instructor.employee. If an Instructor was
    created without an `employee` link (e.g. by older test data scripts or manual
    Desk entry), the lookup fails and the teacher sees:

        "Your account is not linked to an Instructor profile."

    This patch:
        1. Finds every Instructor with no `employee`
        2. Tries to find a matching User (by full_name == instructor_name)
        3. Finds or creates an Employee for that user (with safe placeholder
           values for required fields the User doesn't have)
        4. Sets `instructor.employee = employee.name`

    Idempotent — safe to run multiple times. Skips silently when:
        - Instructor already has an employee link
        - No matching User can be found (logs a warning)
        - User has no Company / Gender (logs a warning, doesn't crash)
"""

import frappe
from frappe.utils import today


PLACEHOLDER_DOB = "1990-01-01"


def _find_user_for_instructor(instructor_name):
    """Match by User.full_name → Instructor.instructor_name."""
    user = frappe.db.get_value(
        "User",
        {"full_name": instructor_name, "enabled": 1},
        "name",
    )
    return user


def _resolve_company(user, fallback):
    """User Permission → first Company in system → fallback."""
    company = frappe.db.get_value(
        "User Permission",
        {"user": user, "allow": "Company"},
        "for_value",
    )
    if company:
        return company
    if fallback:
        return fallback
    first = frappe.db.get_value("Company", {}, "name")
    return first


def _ensure_employee(user, instructor_doc, company):
    """Find existing Employee for this user OR create one."""
    emp_name = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if emp_name:
        return emp_name

    user_doc = frappe.get_doc("User", user)
    gender = user_doc.gender or instructor_doc.gender
    if not gender:
        print(
            f"  ! Skipping {instructor_doc.name}: User {user} has no gender; "
            f"cannot create Employee."
        )
        return None
    if not company:
        print(
            f"  ! Skipping {instructor_doc.name}: no Company resolved for User {user}."
        )
        return None

    emp = frappe.get_doc({
        "doctype": "Employee",
        "first_name": user_doc.first_name or instructor_doc.instructor_name.split(" ")[0],
        "last_name": user_doc.last_name or "",
        "employee_name": user_doc.full_name or instructor_doc.instructor_name,
        "gender": gender,
        "date_of_birth": PLACEHOLDER_DOB,
        "date_of_joining": today(),
        "status": "Active",
        "company": company,
        "user_id": user,
    })
    emp.insert(ignore_permissions=True)
    print(f"  + Created Employee {emp.name} for User {user}")
    return emp.name


def execute():
    print("Patch: link_instructors_to_employees — start")

    orphans = frappe.get_all(
        "Instructor",
        filters={"employee": ["in", ["", None]]},
        fields=["name", "instructor_name", "company", "gender"],
    )

    if not orphans:
        print("  ✓ No orphan Instructors found. Nothing to do.")
        return

    print(f"  Found {len(orphans)} Instructor(s) without employee link.")

    healed = 0
    skipped = 0

    for row in orphans:
        instructor_doc = frappe.get_doc("Instructor", row.name)

        user = _find_user_for_instructor(instructor_doc.instructor_name)
        if not user:
            print(
                f"  ! Skipping {instructor_doc.name}: no matching User for "
                f"'{instructor_doc.instructor_name}'."
            )
            skipped += 1
            continue

        company = _resolve_company(user, instructor_doc.company)
        emp_name = _ensure_employee(user, instructor_doc, company)
        if not emp_name:
            skipped += 1
            continue

        # Link instructor → employee (use db_set to avoid re-running validate)
        instructor_doc.db_set("employee", emp_name, update_modified=False)
        healed += 1
        print(f"  ~ Linked Instructor {instructor_doc.name} → Employee {emp_name}")

    frappe.db.commit()
    print(
        f"Patch: link_instructors_to_employees — done. "
        f"Healed: {healed}, Skipped: {skipped}"
    )
