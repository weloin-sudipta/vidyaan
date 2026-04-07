"""
Patch: v0_create_assignment_doctype
Purpose: Reload the three new Assignment doctypes and migrate legacy
         Assessment Plan records whose assessment_group contains "Assignment"
         into the new Assignment + Assignment Submission model.

Safe to re-run: duplicate detection prevents creating the same assignment twice.
"""

import frappe
from frappe.utils import getdate


def execute():
    # ── Step 1: Reload the new doctypes ──────────────────────────────────
    for doctype in ("Assignment Target Group", "Assignment Submission", "Assignment"):
        frappe.reload_doc("vidyaan", "doctype", frappe.scrub(doctype))

    frappe.db.commit()

    # ── Step 2: Fetch legacy Assessment Plans tagged as Assignments ───────
    legacy_plans = frappe.get_all(
        "Assessment Plan",
        filters={
            "assessment_group": ["like", "%Assignment%"],
            "docstatus": ["in", [0, 1]],
        },
        fields=[
            "name", "assessment_name", "course", "student_group",
            "schedule_date", "maximum_assessment_score", "examiner", "docstatus",
        ],
    )

    migrated = 0
    skipped = 0
    failed = 0

    for plan in legacy_plans:
        try:
            title = plan.assessment_name or plan.name
            course = plan.course
            due_date = plan.schedule_date or frappe.utils.today()
            max_score = plan.maximum_assessment_score or 100
            instructor = plan.examiner
            student_group = plan.student_group
            status = "Published" if plan.docstatus == 1 else "Draft"

            # ── Duplicate check: same title + course + due_date + instructor ──
            existing = frappe.db.exists(
                "Assignment",
                {
                    "title": title,
                    "course": course,
                    "due_date": due_date,
                    "instructor": instructor,
                },
            )
            if existing:
                skipped += 1
                continue

            # ── Resolve instructor if missing ──────────────────────────────
            if not instructor:
                skipped += 1
                continue
            if not frappe.db.exists("Instructor", instructor):
                skipped += 1
                continue

            # ── Build target_groups row ────────────────────────────────────
            target_rows = []
            if student_group and frappe.db.exists("Student Group", student_group):
                target_rows = [{"student_group": student_group}]

            # ── Create the Assignment ──────────────────────────────────────
            doc = frappe.get_doc({
                "doctype": "Assignment",
                "title": title,
                "course": course,
                "instructor": instructor,
                "due_date": due_date,
                "max_score": max_score,
                "assign_to": "Specific Groups" if student_group else "All Enrolled",
                "status": status,
                "description": f"Migrated from Assessment Plan: {plan.name}",
                "target_groups": target_rows,
            })
            doc.insert(ignore_permissions=True)

            # ── Populate submissions from existing Assessment Results ──────
            if student_group and status == "Published":
                results = frappe.get_all(
                    "Assessment Result",
                    filters={
                        "assessment_plan": plan.name,
                        "docstatus": ["in", [0, 1]],
                    },
                    fields=["student", "total_score", "grade", "docstatus"],
                )
                seen = set()
                for r in results:
                    if not r.student or r.student in seen:
                        continue
                    seen.add(r.student)
                    sub_status = "Graded" if (r.total_score is not None and r.docstatus == 1) else "Submitted"
                    doc.append("submissions", {
                        "student": r.student,
                        "student_group": student_group,
                        "score": r.total_score,
                        "status": sub_status,
                    })

                if seen:
                    doc.save(ignore_permissions=True)

            frappe.db.commit()
            migrated += 1

        except Exception:
            frappe.log_error(
                title=f"v0_create_assignment_doctype: migration failed for plan {plan.name}",
                message=frappe.get_traceback(),
            )
            frappe.db.rollback()
            failed += 1

    frappe.logger().info(
        f"Assignment migration complete. migrated={migrated} skipped={skipped} failed={failed}"
    )
