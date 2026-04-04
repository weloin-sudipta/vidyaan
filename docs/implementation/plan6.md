# Plan 6: Backend Bug Fixes & Setup Repair

## Status: Completed

## Problem Statement

The Vidyaan backend code is **structurally complete and healthy** — all Python files compile, all hooks reference existing functions, all doctypes have valid JSON + Python definitions. However, the **installation ran incompletely**, leaving the system in a half-configured state:

### Current State (Verified via bench console)

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| DocTypes (7 custom) | All exist | All exist | OK |
| Roles (3: System Admin, Institute Admin, Instructor) | All exist | All exist | OK |
| Vidyaan Dashboard workspace | Exists | Exists | OK |
| Default user (vidyaan@weloin.com) | Exists | **MISSING** | BROKEN |
| Company field on Student | Exists | **MISSING** (orphan `institute` field instead) | BROKEN |
| Company field on Instructor | Exists | **MISSING** (orphan `institute` field instead) | BROKEN |
| Company field on 8 other doctypes | Exists | **MISSING** | BROKEN |
| Instructor Course Mapping table | On Instructor | **MISSING** | BROKEN |
| Assessment Groups (Exams, Assignments) | Exist | **MISSING** | BROKEN |
| Period Timings (5 default) | In Vidyaan Settings | **0 rows** | BROKEN |
| Admit Card print format | Exists | **MISSING** | BROKEN |
| vidyaan_setup_complete flag | 0 | **None** | BROKEN |
| Publication permissions | Include Institute Admin | **System Manager only** | BUG-003 |
| Assessment publication approver | Institute Admin | **"Academic Manager" (doesn't exist)** | BUG-002 |

### Root Cause

**BUG-001**: The orphan `institute` custom field on Student (from a prior install) caused `create_vidyaan_custom_fields()` to fail. Since `install()` calls functions sequentially, everything after `create_vidyaan_custom_fields()` also failed: settings, workspace refresh, admit card, assessment groups. The roles already existed from a prior run so they weren't recreated.

---

## Fix Plan

### Fix 1: Clean up stale custom fields before creating new ones (BUG-001)

**File:** `vidyaan/setup/custom_fields.py`

Add a `cleanup_stale_fields()` function at the start of `create_vidyaan_custom_fields()` that removes any orphan custom fields from previous Vidyaan installs before creating the correct ones.

```python
def cleanup_stale_fields():
    """Remove orphan custom fields from previous installs."""
    stale = frappe.get_all("Custom Field",
        filters={"fieldname": "institute"},
        pluck="name"
    )
    for name in stale:
        frappe.delete_doc("Custom Field", name, ignore_permissions=True)
    frappe.db.commit()
```

### Fix 2: Fix Publication approver role (BUG-002)

**File:** `vidyaan/utils.py`

Change `"approver_role": "Academic Manager"` to `"approver_role": "Institute Admin"` in `create_assessment_publication()`. The "Academic Manager" role was never created and doesn't exist.

### Fix 3: Fix Publication permissions (BUG-003)

**File:** `vidyaan/vidyaan/doctype/publication/publication.json`

Add Institute Admin role with full CRUD + submit/cancel permissions to the `permissions` array. Currently only System Manager has access.

### Fix 4: Strengthen examiner validation (BUG-004)

**File:** `vidyaan/events.py`

Add a fallback: if the User → Employee → Instructor chain fails, try looking up Instructor directly by checking if any Instructor has an employee whose user_id matches the current user. Provide clear error messages.

### Fix 5: Re-run setup to populate missing data

After applying code fixes, re-run the install function via bench console to populate:
- Default user
- Custom fields (company on 10 doctypes + Instructor Course Mapping)
- Period timings
- Assessment groups
- Admit card print format
- vidyaan_setup_complete flag

---

## Files Changed

| File | Change Type | Description |
|------|------------|-------------|
| `vidyaan/setup/custom_fields.py` | MODIFY | Add `cleanup_stale_fields()` before creating fields |
| `vidyaan/utils.py` | MODIFY | Change approver_role from "Academic Manager" to "Institute Admin" |
| `vidyaan/vidyaan/doctype/publication/publication.json` | MODIFY | Add Institute Admin + Instructor permissions |
| `vidyaan/events.py` | MODIFY | Add fallback instructor lookup + better error messages |
| `vidyaan/setup/install.py` | MODIFY | Fix Print Format field name (`html` not `format`), fix Assessment Group tree rebuild |
| `vidyaan/setup/roles.py` | REWRITE | Complete rewrite — always applies permissions (not just on first create), covers 42+ doctypes per admin role, 26 for Instructor |
| `vidyaan/setup/user.py` | REWRITE | Always ensures correct roles even on existing user, uses `Desk User` (Frappe v15 name for System User) |

---

## Verification

After implementation:
1. All 7 custom doctypes exist
2. Company field exists on all 10 education doctypes
3. Instructor Course Mapping table exists on Instructor
4. Default user exists with correct roles
5. Period timings populated (5 rows)
6. Assessment groups exist (Exams, Assignments)
7. Admit Card print format exists
8. Publication has Institute Admin permissions
9. Assessment publication uses "Institute Admin" as approver
10. `bench start` runs without errors
11. Login page loads at dev.localhost:8000
