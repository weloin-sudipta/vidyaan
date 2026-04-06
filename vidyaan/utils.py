import frappe
from frappe import _

def extend_bootinfo(bootinfo):
    # Legacy flag — the custom Vidyaan setup wizard has been removed in favor of
    # the default Frappe/ERPNext wizard. Kept as 1 so any stale client code treats
    # setup as complete and does not trigger the old overlay.
    bootinfo.vidyaan_setup_complete = 1

def create_assessment_publication(doc, method):
    """
    Automatically creates a Publication (Notice) when an Assessment Plan is submitted.
    """
    try:
        # Check if a publication already exists for this assessment to avoid duplicates
        existing = frappe.db.exists("Publication", {"title": f"Assessment: {doc.name}"})
        if existing:
            return

        # Create the Publication document
        pub = frappe.get_doc({
            "doctype": "Publication",
            "title": f"Assessment: {doc.name}",
            "type": "Notice",
            "content": f"""
                <h3>Assessment Schedule Announced</h3>
                <p>An assessment for <b>{doc.assessment_group}</b> has been scheduled.</p>
                <ul>
                    <li><b>Course:</b> {doc.course}</li>
                    <li><b>Date:</b> {doc.schedule_date if hasattr(doc, 'schedule_date') else 'TBD'}</li>
                </ul>
                <p>Please check the assessment plan for more details.</p>
            """,
            "publish_date": frappe.utils.nowdate(),
            "target_type": "Student Group",
            "target_student_group": doc.student_group,
            "approval_type": "By Role",
            "approver_role": "Institute Admin",
            "status": "Draft",
            "is_global": 0
        })
        
        pub.insert(ignore_permissions=True)
        
        # Notify the user that a notice was created
        frappe.msgprint(_("A Publication (Notice) has been automatically created for this assessment: {0}").format(pub.name))

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_assessment_publication failed")
        # We don't throw here to avoid blocking the Assessment Plan submission if only the notification fails
