import frappe
from frappe.permissions import add_permission, update_permission_property


def create_roles():
    """Create Vidyaan roles and assign permissions to all required doctypes."""
    _ensure_roles_exist()
    _apply_all_permissions()


def _ensure_roles_exist():
    """Create roles if they don't already exist."""
    for role in ["System Administrator", "Institute Admin", "Instructor", "Librarian"]:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": 1
            }).insert(ignore_permissions=True)


def _apply_all_permissions():
    """Apply permissions for all Vidyaan roles across all required doctypes.

    This runs every time (not just on first install) to ensure permissions
    are always correct even after reinstall or migration.
    """
    # ── System Administrator & Institute Admin: Full CRUD on education + vidyaan doctypes ──
    admin_roles = ["System Administrator", "Institute Admin"]

    # Education doctypes — full CRUD
    education_crud = [
        "Student", "Instructor", "Program", "Course", "Topic", "Article",
        "Program Enrollment", "Student Group", "Student Attendance", "Course Schedule",
        "Room", "Academic Year", "Academic Term", "Grading Scale",
        "Guardian", "Student Category", "Student Batch Name",
        "Student Applicant", "Student Admission", "Student Log",
        "Student Leave Application", "Assessment Criteria",
        "Video", "Quiz", "Fee Category", "Fee Schedule",
    ]
    for role in admin_roles:
        for dt in education_crud:
            _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # Education doctypes — CRUD + submit/cancel (submittable)
    education_submittable = [
        "Assessment Plan", "Assessment Result", "Fee Structure", "Fees",
    ]
    for role in admin_roles:
        for dt in education_submittable:
            _set_permission(dt, role, read=1, write=1, create=1, delete=1,
                            submit=1, cancel=1, amend=1, select=1, share=1)

    # Education read-only doctypes
    education_readonly = [
        "Assessment Group", "Course Enrollment", "Course Activity", "Quiz Activity",
    ]
    for role in admin_roles:
        for dt in education_readonly:
            _set_permission(dt, role, read=1, select=1)

    # Education tools
    education_tools = [
        "Assessment Result Tool", "Student Attendance Tool",
        "Student Report Generation Tool", "Course Scheduling Tool",
        "Student Group Creation Tool", "Program Enrollment Tool",
    ]
    for role in admin_roles:
        for dt in education_tools:
            _set_permission(dt, role, read=1, write=1, create=1)

    # ERPNext/HR doctypes needed by admin
    erpnext_crud = ["Company", "Employee"]
    for role in admin_roles:
        for dt in erpnext_crud:
            _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # Frappe core doctypes needed for desk access
    frappe_read = [
        "Page", "Workspace", "DocType", "Module Def", "Print Format", "Report",
        "Dashboard", "Dashboard Chart", "Number Card",
    ]
    for role in admin_roles:
        for dt in frappe_read:
            _set_permission(dt, role, read=1, select=1)

    # User management (admin only)
    for role in admin_roles:
        _set_permission("User", role, read=1, write=1, create=1, select=1, share=1)

    # Education Settings
    for role in admin_roles:
        _set_permission("Education Settings", role, read=1, write=1, create=1, select=1)

    # Vidyaan custom doctypes (already have permissions in JSON, but ensure consistency)
    for role in admin_roles:
        _set_permission("Vidyaan Settings", role, read=1, write=1, create=1, select=1)
        _set_permission("Routine Generation", role, read=1, write=1, create=1, delete=1,
                        submit=1, cancel=1, amend=1, select=1, share=1)
        _set_permission("Publication", role, read=1, write=1, create=1, delete=1,
                        submit=1, cancel=1, amend=1, select=1, share=1)

    # ── Instructor: Limited permissions ──
    instructor_role = "Instructor"

    # Read-only for instructors
    instructor_read = [
        "Student", "Instructor", "Student Group", "Program", "Course Schedule",
        "Assessment Group", "Academic Year", "Academic Term", "Grading Scale",
        "Room", "Program Enrollment",
    ]
    for dt in instructor_read:
        _set_permission(dt, instructor_role, read=1, select=1)

    # Instructors can create/edit content
    instructor_crud = ["Topic", "Article", "Course"]
    for dt in instructor_crud:
        _set_permission(dt, instructor_role, read=1, write=1, create=1, delete=1, select=1)

    # Instructors can manage attendance
    _set_permission("Student Attendance", instructor_role, read=1, write=1, create=1, select=1)
    _set_permission("Student Attendance Tool", instructor_role, read=1, write=1, create=1)

    # Instructors can view and create assessment plans, enter results
    _set_permission("Assessment Plan", instructor_role, read=1, write=1, create=1,
                    submit=1, cancel=1, select=1)
    _set_permission("Assessment Result", instructor_role, read=1, write=1, create=1,
                    submit=1, select=1)
    _set_permission("Assessment Result Tool", instructor_role, read=1, write=1, create=1)

    # Instructors can read publications
    _set_permission("Publication", instructor_role, read=1, select=1)

    # Instructors need desk access
    for dt in ["Page", "Workspace", "Module Def"]:
        _set_permission(dt, instructor_role, read=1, select=1)

    frappe.db.commit()


def _set_permission(doctype, role, **perms):
    """Safely add or update a permission entry for a role on a doctype.

    Skips silently if the doctype doesn't exist (e.g., optional modules).
    """
    if not frappe.db.exists("DocType", doctype):
        return

    try:
        # Ensure the role has a permission row on this doctype
        add_permission(doctype, role, 0)
    except Exception:
        pass

    # Apply each permission flag
    for perm_type, value in perms.items():
        try:
            update_permission_property(doctype, role, 0, perm_type, value)
        except Exception:
            pass
