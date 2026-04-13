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
    """Apply permissions for all Vidyaan roles.

    Institute Admin gets access ONLY to Vidyaan, Library, and Education
    module doctypes — NOT ERPNext core or HRMS.

    System Administrator retains full access across all modules.
    """

    # ──────────────────────────────────────────────────────────
    # System Administrator: full access to everything
    # ──────────────────────────────────────────────────────────
    _apply_system_admin_permissions()

    # ──────────────────────────────────────────────────────────
    # Institute Admin: restricted to Vidyaan + Library + Education
    # ──────────────────────────────────────────────────────────
    _apply_institute_admin_permissions()

    # ──────────────────────────────────────────────────────────
    # Instructor: limited teaching permissions
    # ──────────────────────────────────────────────────────────
    _apply_instructor_permissions()

    frappe.db.commit()


def _apply_system_admin_permissions():
    """System Administrator gets full CRUD on all education + ERPNext doctypes."""
    role = "System Administrator"

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
    for dt in education_crud:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # Education — submittable
    for dt in ["Assessment Plan", "Assessment Result", "Fee Structure", "Fees"]:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1,
                        submit=1, cancel=1, amend=1, select=1, share=1)

    # Education read-only
    for dt in ["Assessment Group", "Course Enrollment", "Course Activity", "Quiz Activity"]:
        _set_permission(dt, role, read=1, select=1)

    # Education tools
    for dt in [
        "Assessment Result Tool", "Student Attendance Tool",
        "Student Report Generation Tool", "Course Scheduling Tool",
        "Student Group Creation Tool", "Program Enrollment Tool",
    ]:
        _set_permission(dt, role, read=1, write=1, create=1)

    # ERPNext / HR
    for dt in ["Company", "Employee"]:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # Frappe core (desk access)
    for dt in ["Page", "Workspace", "DocType", "Module Def", "Print Format",
               "Report", "Dashboard", "Dashboard Chart", "Number Card"]:
        _set_permission(dt, role, read=1, select=1)

    # User management
    _set_permission("User", role, read=1, write=1, create=1, select=1, share=1)

    # Settings
    _set_permission("Education Settings", role, read=1, write=1, create=1, select=1)
    _set_permission("Vidyaan Settings", role, read=1, write=1, create=1, select=1)
    _set_permission("Routine Generation", role, read=1, write=1, create=1, delete=1,
                    submit=1, cancel=1, amend=1, select=1, share=1)
    _set_permission("Publication", role, read=1, write=1, create=1, delete=1,
                    submit=1, cancel=1, amend=1, select=1, share=1)


def _apply_institute_admin_permissions():
    """Institute Admin: ONLY Vidyaan + Library + Education module access.

    No ERPNext core (Company, Employee), no System Manager, no User management.
    """
    role = "Institute Admin"

    # ── Education module doctypes (the school data this admin manages) ──
    education_crud = [
        "Student", "Instructor", "Program", "Course", "Topic", "Article",
        "Program Enrollment", "Student Group", "Student Attendance", "Course Schedule",
        "Room", "Academic Year", "Academic Term", "Grading Scale",
        "Guardian", "Student Category", "Student Batch Name",
        "Student Applicant", "Student Admission", "Student Log",
        "Student Leave Application", "Assessment Criteria",
        "Video", "Quiz", "Fee Category", "Fee Schedule",
    ]
    for dt in education_crud:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # Education — submittable
    for dt in ["Assessment Plan", "Assessment Result", "Fee Structure", "Fees"]:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1,
                        submit=1, cancel=1, amend=1, select=1, share=1)

    # Education read-only
    for dt in ["Assessment Group", "Course Enrollment", "Course Activity", "Quiz Activity"]:
        _set_permission(dt, role, read=1, select=1)

    # Education tools
    for dt in [
        "Assessment Result Tool", "Student Attendance Tool",
        "Student Report Generation Tool", "Course Scheduling Tool",
        "Student Group Creation Tool", "Program Enrollment Tool",
    ]:
        _set_permission(dt, role, read=1, write=1, create=1)

    # Education Settings (read + write so admin can configure academic settings)
    _set_permission("Education Settings", role, read=1, write=1, create=1, select=1)

    # ── Vidyaan module doctypes ──
    _set_permission("Vidyaan Settings", role, read=1, write=1, create=1, select=1)
    _set_permission("Routine Generation", role, read=1, write=1, create=1, delete=1,
                    submit=1, cancel=1, amend=1, select=1, share=1)
    _set_permission("Publication", role, read=1, write=1, create=1, delete=1,
                    submit=1, cancel=1, amend=1, select=1, share=1)
    _set_permission("Assignment", role, read=1, write=1, create=1, delete=1, select=1, share=1)
    _set_permission("Assignment Submission", role, read=1, write=1, create=1, delete=1, select=1)
    _set_permission("Student NOC", role, read=1, write=1, create=1, delete=1,
                    submit=1, cancel=1, amend=1, select=1, share=1)
    _set_permission("Student Request", role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # ── Library module doctypes ──
    library_doctypes = [
        "Book", "Book Category", "Book Copy", "Book Issue",
        "Book Request", "Book Tag", "Library", "Library Member",
    ]
    for dt in library_doctypes:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1, share=1)

    # ── Minimal Frappe core for desk access (read-only) ──
    for dt in ["Page", "Workspace", "Module Def", "Print Format", "Report"]:
        _set_permission(dt, role, read=1, select=1)


def _apply_instructor_permissions():
    """Instructor: limited teaching permissions."""
    role = "Instructor"

    # Read-only
    for dt in [
        "Student", "Instructor", "Student Group", "Program", "Course Schedule",
        "Assessment Group", "Academic Year", "Academic Term", "Grading Scale",
        "Room", "Program Enrollment",
    ]:
        _set_permission(dt, role, read=1, select=1)

    # Content creation
    for dt in ["Topic", "Article", "Course"]:
        _set_permission(dt, role, read=1, write=1, create=1, delete=1, select=1)

    # Attendance
    _set_permission("Student Attendance", role, read=1, write=1, create=1, select=1)
    _set_permission("Student Attendance Tool", role, read=1, write=1, create=1)

    # Assessment
    _set_permission("Assessment Plan", role, read=1, write=1, create=1,
                    submit=1, cancel=1, select=1)
    _set_permission("Assessment Result", role, read=1, write=1, create=1,
                    submit=1, select=1)
    _set_permission("Assessment Result Tool", role, read=1, write=1, create=1)

    # Read publications
    _set_permission("Publication", role, read=1, select=1)

    # Desk access
    for dt in ["Page", "Workspace", "Module Def"]:
        _set_permission(dt, role, read=1, select=1)


def _set_permission(doctype, role, **perms):
    """Safely add or update a permission entry for a role on a doctype.

    Skips silently if the doctype doesn't exist (e.g., optional modules).
    """
    if not frappe.db.exists("DocType", doctype):
        return

    try:
        add_permission(doctype, role, 0)
    except Exception:
        pass

    for perm_type, value in perms.items():
        try:
            update_permission_property(doctype, role, 0, perm_type, value)
        except Exception:
            pass
