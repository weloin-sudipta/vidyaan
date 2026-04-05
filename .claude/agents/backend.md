# Backend Agent — Vidyaan Project Rules

> **READ THIS ENTIRE FILE BEFORE WRITING ANY CODE.**
> This file defines the mandatory workflow, rules, and constraints for any AI/agent working on Vidyaan backend (Python, Frappe, doctypes, hooks, API).

---

## Step 0 — Mandatory Pre-Read (DO NOT SKIP)

Before touching any code, read these files **in order**:

1. `docs/overview.md` — understand what Vidyaan is
2. `docs/folder-structure/backend.md` — know every doctype and what it maps to
3. `docs/architecture.md` — understand multi-tenant SaaS architecture
4. `docs/future-scope.md` — know active bugs and priorities
5. `docs/modules/` — understand past plans and phased roadmap

**If you have not read these files, STOP and read them now.** Do not assume anything about the project structure.

---

## Step 1 — Understand the Task

Before writing code, answer these questions (internally):

1. What is the feature/fix being requested?
2. Which existing doctypes are involved? (check `docs/DOCTYPES.md`)
3. Does the backend already support this partially? (check `docs/FEATURES.md`)
4. Is there an implementation plan for this? (check `docs/IMPLEMENTATION_PLAN.md`)
5. Will this change affect other features? (trace dependencies)

---

## Step 2 — Doctype Rules (CRITICAL)

### Rule 1: USE EXISTING DOCTYPES FIRST

Vidyaan is built on top of **Frappe + ERPNext + Education**. These provide 23+ native doctypes. Before creating anything new:

- Check `docs/DOCTYPES.md` — the "School Concept → Doctype Mapping" table
- Check if a native doctype already handles the concept
- Check if a custom field on an existing doctype would solve the need
- Check if a child table on an existing doctype would work

**Decision tree:**
```
Can a native Education/ERPNext doctype handle this?
  ├── YES → Use it. Add custom fields if needed.
  │         Register fields in vidyaan/setup/custom_fields.py
  │
  └── NO → Can a custom field or child table on an existing doctype work?
      ├── YES → Add the custom field. Do NOT create a new doctype.
      │
      └── NO → Is this genuinely a new concept with no native equivalent?
          ├── YES → Create a new doctype. Document it in DOCTYPES.md.
          │         Justify WHY in a comment at the top of the doctype JSON.
          │
          └── NO → You are wrong. Go back to step 1.
```

### Rule 2: AVOID CREATING NEW DOCTYPES

This is repeated intentionally. **Do not create new doctypes unless absolutely necessary.**

Ask yourself:
- Can I use `Assessment Plan` / `Assessment Result` instead of a custom exam doctype?
- Can I use `Course Schedule` instead of a custom timetable entry?
- Can I use `Student Attendance` instead of a custom attendance tracker?
- Can I use `Program Enrollment` instead of a custom registration doctype?
- Can I use the `Publication` doctype (already custom) for announcements?

If the answer to any of these is yes, use the native/existing doctype.

### Rule 3: Multi-Tenant Isolation

Every doctype that holds institute-specific data MUST have a `company` field. Check `docs/CUSTOMIZATIONS.md` for the pattern. If you add a new doctype or query existing ones, ensure company-level filtering is applied.

---

## Step 3 — Code Quality Rules

### Write Optimized Code

- **No redundant queries** — use `frappe.get_all()` with proper filters, fields, and limit
- **No N+1 queries** — if you need related data, fetch it in bulk, not in a loop
- **Use `frappe.db.sql()` only when ORM can't handle it** — prefer `frappe.get_all`, `frappe.get_doc`
- **Cache repeated lookups** — use `frappe.cache()` or local variables
- **Minimal imports** — only import what you use

### Write Automation Code (Hooks & Events)

This is a key requirement. When one doctype changes, related doctypes should auto-update if needed.

**Use document event hooks in `vidyaan/hooks.py`:**
```python
doc_events = {
    "Assessment Plan": {
        "on_submit": "vidyaan.events.on_assessment_plan_submit",
        "on_cancel": "vidyaan.events.on_assessment_plan_cancel"
    },
    "Program Enrollment": {
        "after_insert": "vidyaan.events.on_enrollment_created"
    }
}
```

**Automation patterns to follow:**

| Trigger | Auto-Action |
|---------|------------|
| Assessment Plan submitted | Auto-create Publication notice (already exists) |
| Student Attendance marked | Update attendance summary/stats if cached |
| Program Enrollment created | Auto-add student to relevant Student Groups |
| Routine Generation submitted | Auto-create Course Schedule entries (already exists) |
| Fee Structure changed | Regenerate pending Fee records |
| Instructor Course Mapping updated | Validate routine conflicts |

**Rules for hooks:**
- Put hook functions in `vidyaan/events.py` or `vidyaan/api_folder/<module>.py`
- Always wrap in try/except to prevent cascading failures
- Log errors with `frappe.log_error()`, never silently swallow exceptions
- Use `frappe.enqueue()` for heavy operations (email, PDF generation, bulk updates)
- Test that cancelling/amending the trigger doctype reverses the auto-action

### Don't Break Existing Code

- **Before modifying any file**, read it completely first
- **Search for all usages** of any function/method you change (`grep -r "function_name"`)
- **Check hooks.py** to see if the doctype you're modifying has event hooks
- **Check the frontend composables** (`frontend/composable/`) to see if your API changes break any frontend call
- **Run existing tests** before and after your changes
- **Never modify a whitelisted API's return structure** without checking all frontend callers

### API Endpoint Rules

- Whitelisted methods go in `vidyaan/api_folder/` or the relevant doctype module
- Use `@frappe.whitelist()` decorator
- Always validate permissions inside the method — don't rely solely on the decorator
- Return consistent response shapes: `{"message": data}` or raise `frappe.throw()`
- Document parameters with docstrings

---

## Step 4 — Implementation Flow

```
1. READ the docs (Step 0)
2. UNDERSTAND the task (Step 1)
3. SEARCH for existing code that does something similar
4. CHECK if existing doctypes handle the need (Step 2)
5. PLAN the minimal changes needed
6. READ every file you plan to modify
7. WRITE the code — minimal, optimized, with automation hooks
8. VERIFY no side effects on other features
9. TEST the changes
10. UPDATE docs if you created new doctypes or APIs
```

---

## Step 5 — File Location Guide

| What | Where |
|------|-------|
| Custom fields setup | `vidyaan/setup/custom_fields.py` |
| Document event hooks | `vidyaan/events.py` |
| Hook registration | `vidyaan/hooks.py` |
| API endpoints | `vidyaan/api_folder/<module>.py` |
| Library APIs | `vidyaan/library_management/api.py` |
| Publication logic | `vidyaan/desk_approval/doctype/publication/` |
| Routine generation | `vidyaan/routine/` |
| Doctype definitions | `vidyaan/<module>/doctype/<doctype_name>/` |
| Setup/install logic | `vidyaan/setup/` |

---

## Step 6 — Checklist Before Committing

- [ ] Read all mandatory docs (Step 0)
- [ ] Used existing doctypes — did NOT create unnecessary new ones
- [ ] Company field present on any new institute-scoped doctype
- [ ] Automation hooks added where one doctype change affects another
- [ ] No N+1 queries, no redundant DB calls
- [ ] No breaking changes to existing API return structures
- [ ] All `frappe.whitelist()` methods validate permissions
- [ ] Error handling with `frappe.log_error()` on hook functions
- [ ] No hardcoded values — use Vidyaan Settings or site config
- [ ] Searched for side effects on other features
- [ ] Updated `docs/DOCTYPES.md` if new doctype was created (with justification)
- [ ] Updated `docs/FEATURES.md` if feature status changed
- [ ] Updated `docs/CUSTOMIZATIONS.md` if new hooks/fields added

---

## ARCHITECTURE CHANGE PROTOCOL

If you add, remove, or significantly modify:
- New DocTypes or custom fields
- New whitelisted API methods
- New hooks or events
- Changes to existing DocType structures
- Major backend feature additions

THEN call the ARCHIVIST agent to update docs:

```
Call archivist to sync docs with new architecture changes.
```

This ensures docs/FEATURES.md and docs/DOCTYPES.md stay accurate with the current backend.

---

*This file is the law for backend work. Follow it.*
