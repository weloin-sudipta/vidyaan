"""Install default Vidyaan workflows on existing sites.

Ensures that existing sites picking up this release get:
1. The `workflow_state` custom field on Student Leave Application (prerequisite
   for the Student Leave Approval workflow to actually persist state).
2. The Student Leave Approval workflow.
3. The Student NOC Approval workflow.
4. A fix for the pre-existing bad "Rejected" state (doc_status "0" → "2") on
   any workflow already installed on the site before this patch ran.

Idempotent: safe to re-run.
"""

import frappe

from vidyaan.setup.custom_fields import create_vidyaan_custom_fields
from vidyaan.setup.install import (
    setup_student_leave_workflow,
    setup_student_noc_workflow,
)


WORKFLOWS_TO_FIX_REJECTED = [
    "Student Leave Approval",
    "Student NOC Approval",
]


def _fix_rejected_state_doc_status(workflow_name: str) -> None:
    """Ensure the 'Rejected' state on an already-installed workflow is doc_status=2.

    Older installs created Rejected with doc_status='0', which is wrong: a
    rejection of a submitted doc should cancel it (docstatus=2), not leave it
    as a draft. This patch corrects the value in-place without recreating the
    workflow so that existing transitions remain intact.
    """
    if not frappe.db.exists("Workflow", workflow_name):
        return

    try:
        wf = frappe.get_doc("Workflow", workflow_name)
    except Exception as e:
        frappe.log_error(
            f"[vidyaan patch] Could not load workflow '{workflow_name}': {e}",
            "install_default_workflows",
        )
        return

    changed = False
    for state in wf.states:
        if state.state == "Rejected" and str(state.doc_status) != "2":
            state.doc_status = "2"
            changed = True

    if changed:
        try:
            wf.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(
                f"[vidyaan patch] Failed to save Rejected doc_status fix on "
                f"'{workflow_name}': {e}",
                "install_default_workflows",
            )


def execute():
    # 1. Ensure custom fields (incl. Student Leave Application.workflow_state)
    #    exist on this site. create_vidyaan_custom_fields is idempotent.
    try:
        create_vidyaan_custom_fields()
    except Exception as e:
        frappe.log_error(
            f"[vidyaan patch] create_vidyaan_custom_fields failed: {e}",
            "install_default_workflows",
        )

    # 2. Fix existing workflows before attempting re-install.
    for wf_name in WORKFLOWS_TO_FIX_REJECTED:
        _fix_rejected_state_doc_status(wf_name)

    # 3. Install workflows if missing. Both helpers no-op if the workflow
    #    already exists and log loudly if required roles are missing.
    try:
        setup_student_leave_workflow()
    except Exception as e:
        frappe.log_error(
            f"[vidyaan patch] setup_student_leave_workflow failed: {e}",
            "install_default_workflows",
        )

    try:
        setup_student_noc_workflow()
    except Exception as e:
        frappe.log_error(
            f"[vidyaan patch] setup_student_noc_workflow failed: {e}",
            "install_default_workflows",
        )

    frappe.db.commit()
