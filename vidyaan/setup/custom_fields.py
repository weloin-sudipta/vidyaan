import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def cleanup_stale_fields():
    """Remove orphan custom fields from previous Vidyaan installs that block reinstall."""
    stale_fieldnames = ["institute"]
    education_doctypes = [
        "Student", "Instructor", "Program", "Course", "Topic", "Article",
        "Program Enrollment", "Course Schedule", "Student Group", "Student Attendance"
    ]
    for dt in education_doctypes:
        for fn in stale_fieldnames:
            cf_name = f"{dt}-{fn}"
            if frappe.db.exists("Custom Field", cf_name):
                frappe.delete_doc("Custom Field", cf_name, ignore_permissions=True)
    frappe.db.commit()

def create_vidyaan_custom_fields():
    """
    Injects a mandatory 'Company' field into standard ERPNext Education Doctypes
    to enable Multi-Tenant SaaS Isolation per School/Institute.
    """
    # Clean up orphan fields from previous installs (fixes BUG-001)
    cleanup_stale_fields()

    # The doctypes we must isolate per school
    education_doctypes = [
        "Student", 
        "Instructor", 
        "Program", 
        "Course", 
        "Topic", 
        "Article", 
        "Program Enrollment", 
        "Course Schedule", 
        "Student Group", 
        "Student Attendance"
    ]

    custom_fields = {}
    
    for dt in education_doctypes:
        custom_fields[dt] = [
            {
                "fieldname": "company",
                "label": "Institute / Company",
                "fieldtype": "Link",
                "options": "Company",
                "insert_after": "naming_series" if dt in ["Student", "Instructor"] else "",
                "reqd": 1, # Mandatory for True SaaS isolation
                "in_list_view": 1,
                "in_standard_filter": 1,
                "default": "frappe.defaults.get_user_default('Company')"
            }
        ]

    # Create the company fields natively
    create_custom_fields(custom_fields)

    # Inject Instructor Course Mapping table onto Instructor doctype
    instructor_fields = {
        "Instructor": [
            {
                "fieldname": "course_mapping_section",
                "fieldtype": "Section Break",
                "label": "Course & Program Mapping",
                "insert_after": "instructor_log"
            },
            {
                "fieldname": "course_mappings",
                "fieldtype": "Table",
                "label": "Courses I Teach",
                "options": "Instructor Course Mapping",
                "insert_after": "course_mapping_section"
            }
        ]
    }
    create_custom_fields(instructor_fields)

    # Student Group → dedicated classroom (one room per section, never changes).
    # Required because ERPNext Course Schedule has a mandatory `room` field, and
    # Vidyaan's routine generator inherits the section's room into every slot.
    student_group_room = {
        "Student Group": [
            {
                "fieldname": "room",
                "label": "Classroom",
                "fieldtype": "Link",
                "options": "Room",
                "insert_after": "company",
                "reqd": 0,  # not enforced at form save — enforced at routine submit
                "in_list_view": 1,
                "description": "Dedicated classroom for this section. "
                               "Required before submitting a Routine Generation.",
            }
        ]
    }
    create_custom_fields(student_group_room)

    # Student Leave Application → workflow_state.
    # ERPNext Education's Student Leave Application has no workflow_state or status
    # field. We inject one so Frappe's Workflow engine (Student Leave Approval)
    # can persist state transitions. Without this field, the workflow engine
    # silently fails to save the state name, and every Leave doc looks identical.
    student_leave_workflow_state = {
        "Student Leave Application": [
            {
                "fieldname": "workflow_state",
                "label": "Workflow State",
                "fieldtype": "Link",
                "options": "Workflow State",
                "insert_after": "amended_from",
                "read_only": 1,
                "hidden": 1,
                "no_copy": 1,
                "print_hide": 1,
                "report_hide": 1,
                "allow_on_submit": 1,
            }
        ]
    }
    create_custom_fields(student_leave_workflow_state)
