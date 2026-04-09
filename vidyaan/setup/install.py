# vidyaan/setup/install.py
import frappe
from vidyaan.setup.user import create_default_user
from vidyaan.setup.roles import create_roles

from vidyaan.setup.workspace import create_vidyaan_workspace
from vidyaan.setup.custom_fields import create_vidyaan_custom_fields
from vidyaan.setup.onboarding import create_vidyaan_onboarding

def install():
    create_roles()
    create_default_user()
    create_vidyaan_custom_fields()
    create_vidyaan_onboarding()
    setup_vidyaan_settings()
    create_vidyaan_workspace()
    setup_admit_card_print_format()
    setup_assessment_groups()
    setup_student_noc_workflow()
    setup_student_leave_workflow()

def setup_vidyaan_settings():
    """Initialize Vidyaan Settings with default period timings."""
    settings = frappe.get_single("Vidyaan Settings")
    
    if not settings.period_timings:
        default_timings = [
            {"period_number": 1, "start_time": "09:00:00", "end_time": "09:45:00"},
            {"period_number": 2, "start_time": "09:45:00", "end_time": "10:30:00"},
            {"period_number": 3, "start_time": "10:30:00", "end_time": "11:15:00"},
            {"period_number": 4, "start_time": "11:30:00", "end_time": "12:15:00"},
            {"period_number": 5, "start_time": "12:15:00", "end_time": "13:00:00"},
        ]
        for timing in default_timings:
            settings.append("period_timings", timing)
        settings.save(ignore_permissions=True)

def after_install():
    # Call user and role creation scripts
    install()

    # Vidyaan custom setup wizard is disabled — let the default Frappe/ERPNext
    # setup wizard run on first login. Do not force System Settings.setup_complete.

def setup_admit_card_print_format():
    """Create the Admit Card print format for Students."""
    if not frappe.db.exists("Print Format", "Admit Card"):
        import os
        template_path = os.path.join(frappe.get_app_path("vidyaan"), "templates", "admit_card.html")
        with open(template_path, "r") as f:
            html_content = f.read()

        frappe.get_doc({
            "doctype": "Print Format",
            "name": "Admit Card",
            "doc_type": "Student",
            "html": html_content,
            "print_format_type": "Jinja",
            "standard": "No",
            "custom_format": 1
        }).insert(ignore_permissions=True)

def setup_assessment_groups():
    """Setup default Assessment Groups for Exams and Assignments."""
    from frappe.utils.nestedset import rebuild_tree

    # Ensure the nested set tree is valid (lft/rgt populated)
    rebuild_tree("Assessment Group", "parent_assessment_group")

    # Find the root node
    root = frappe.db.get_value("Assessment Group", {"is_group": 1, "lft": 1}, "name")
    if not root:
        return

    for name in ["Exams", "Assignments"]:
        if not frappe.db.exists("Assessment Group", name):
            try:
                frappe.get_doc({
                    "doctype": "Assessment Group",
                    "assessment_group_name": name,
                    "parent_assessment_group": root,
                    "is_group": 1
                }).insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), f"setup_assessment_groups: failed to create {name}")


def _collect_workflow_roles(states_data, transitions_data):
    """Collect every role referenced by a workflow definition."""
    roles = set()
    for s in states_data:
        r = (s.get("allow_edit") or "").strip()
        if r:
            roles.add(r)
    for t in transitions_data:
        r = (t.get("allowed") or "").strip()
        if r:
            roles.add(r)
    return roles


def _missing_roles(roles):
    return [r for r in roles if not frappe.db.exists("Role", r)]


def _ensure_workflow_masters(states_data, transitions_data):
    """Create Workflow State and Workflow Action Master rows idempotently."""
    for s in states_data:
        name = s["state"]
        if not frappe.db.exists("Workflow State", name):
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": name,
            }).insert(ignore_permissions=True)
    for t in transitions_data:
        action = t["action"]
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action,
            }).insert(ignore_permissions=True)


def _install_workflow(workflow_name, document_type, states_data, transitions_data):
    """Create a workflow doc with role guarding and idempotency.

    - Skips with a loud log if a required role is missing (fails loudly, not silently).
    - Skips if the target doctype does not exist.
    - Skips if the workflow is already installed.
    - Ensures Workflow State / Workflow Action Master masters exist first.
    """
    if not frappe.db.exists("DocType", document_type):
        frappe.log_error(
            f"[vidyaan] Skipping workflow '{workflow_name}': doctype '{document_type}' not found.",
            "vidyaan workflow install",
        )
        return False

    if frappe.db.exists("Workflow", workflow_name):
        return False

    required_roles = _collect_workflow_roles(states_data, transitions_data)
    missing = _missing_roles(required_roles)
    if missing:
        # Loud failure: log error row visible in Error Log, do NOT silently proceed.
        frappe.log_error(
            f"[vidyaan] Cannot install workflow '{workflow_name}' — missing roles: {missing}. "
            f"Create these roles and re-run migrate.",
            "vidyaan workflow install",
        )
        return False

    _ensure_workflow_masters(states_data, transitions_data)

    workflow = frappe.get_doc({
        "doctype": "Workflow",
        "workflow_name": workflow_name,
        "document_type": document_type,
        "is_active": 1,
        "override_status": 0,
        "send_email_alert": 1,
        "workflow_state_field": "workflow_state",
        "states": states_data,
        "transitions": transitions_data,
    })

    try:
        workflow.insert(ignore_permissions=True)
        frappe.db.commit()
        return True
    except Exception as e:
        frappe.log_error(
            f"Failed to create workflow '{workflow_name}': {str(e)}",
            "vidyaan workflow install",
        )
        return False


def setup_student_noc_workflow():
    """Create workflow for Student NOC approval process."""
    states_data = [
        {"state": "Draft", "doc_status": "0", "allow_edit": "Student"},
        {"state": "Pending Review", "doc_status": "1", "allow_edit": "Instructor"},
        {"state": "Library Clearance", "doc_status": "1", "allow_edit": "Librarian"},
        {"state": "Accounts Clearance", "doc_status": "1", "allow_edit": "Institute Admin"},
        {"state": "Lab Clearance", "doc_status": "1", "allow_edit": "Instructor"},
        {"state": "Hostel Clearance", "doc_status": "1", "allow_edit": "Instructor"},
        {"state": "Final Approval", "doc_status": "1", "allow_edit": "Institute Admin"},
        {"state": "Approved", "doc_status": "1", "allow_edit": ""},
        # Rejected only transitions from submitted (doc_status=1) states, so 2 = cancelled.
        {"state": "Rejected", "doc_status": "2", "allow_edit": ""},
    ]

    transitions_data = [
        {"state": "Draft", "action": "Submit", "next_state": "Pending Review", "allowed": "Student"},
        {"state": "Pending Review", "action": "Send to Library", "next_state": "Library Clearance", "allowed": "Instructor"},
        {"state": "Library Clearance", "action": "Clear", "next_state": "Accounts Clearance", "allowed": "Librarian"},
        {"state": "Library Clearance", "action": "Reject", "next_state": "Rejected", "allowed": "Librarian"},
        {"state": "Accounts Clearance", "action": "Clear", "next_state": "Lab Clearance", "allowed": "Institute Admin"},
        {"state": "Accounts Clearance", "action": "Reject", "next_state": "Rejected", "allowed": "Institute Admin"},
        {"state": "Lab Clearance", "action": "Clear", "next_state": "Hostel Clearance", "allowed": "Instructor"},
        {"state": "Lab Clearance", "action": "Reject", "next_state": "Rejected", "allowed": "Instructor"},
        {"state": "Hostel Clearance", "action": "Clear", "next_state": "Final Approval", "allowed": "Instructor"},
        {"state": "Hostel Clearance", "action": "Reject", "next_state": "Rejected", "allowed": "Instructor"},
        {"state": "Final Approval", "action": "Approve", "next_state": "Approved", "allowed": "Institute Admin"},
        {"state": "Final Approval", "action": "Reject", "next_state": "Rejected", "allowed": "Institute Admin"},
    ]

    _install_workflow("Student NOC Approval", "Student NOC", states_data, transitions_data)


def setup_student_leave_workflow():
    """Create workflow for Student Leave Application approval process."""
    states_data = [
        {"state": "Draft", "doc_status": "0", "allow_edit": "Student"},
        {"state": "Pending Review", "doc_status": "1", "allow_edit": "Instructor"},
        {"state": "Approved", "doc_status": "1", "allow_edit": ""},
        # Rejected only transitions from Pending Review (doc_status=1), so 2 = cancelled.
        {"state": "Rejected", "doc_status": "2", "allow_edit": ""},
    ]

    transitions_data = [
        {"state": "Draft", "action": "Submit", "next_state": "Pending Review", "allowed": "Student"},
        {"state": "Pending Review", "action": "Approve", "next_state": "Approved", "allowed": "Instructor"},
        {"state": "Pending Review", "action": "Reject", "next_state": "Rejected", "allowed": "Instructor"},
    ]

    _install_workflow("Student Leave Approval", "Student Leave Application", states_data, transitions_data)
