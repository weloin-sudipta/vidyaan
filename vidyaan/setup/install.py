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
    
    # Bypass default ERPNext wizard
    if not frappe.db.get_single_value('System Settings', 'setup_complete'):
        frappe.db.set_single_value('System Settings', 'setup_complete', 1)
    
    # Initialize custom setup flag
    frappe.defaults.set_global_default('vidyaan_setup_complete', 0)

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
