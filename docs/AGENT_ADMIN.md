# Admin Panel Agent — Vidyaan Project Rules

> **READ THIS ENTIRE FILE BEFORE WRITING ANY CODE.**
> This file defines the mandatory workflow, rules, and constraints for any AI/agent working on Vidyaan admin panel (Frappe Desk, permissions, roles, doctype access).

---

## Step 0 — Mandatory Pre-Read (DO NOT SKIP)

Before touching any code, read these files **in order**:

1. `docs/PROJECT.md` — understand Vidyaan as a multi-tenant SaaS ERP
2. `docs/DOCTYPES.md` — know every doctype, its source, and its purpose
3. `docs/CUSTOMIZATIONS.md` — know every custom field, hook, role, and permission
4. `docs/architecture_and_workflow.md` — understand the multi-tenant isolation model
5. `docs/FEATURES.md` — know what's done and what's planned
6. `docs/BACKLOG.md` — know active bugs (especially BUG-002, BUG-003 about permissions)

**If you have not read these files, STOP and read them now.**

---

## Core Principle — Admin Uses Frappe Desk Directly

**The admin panel IS Frappe Desk.** We do NOT build a custom admin frontend.

Admins (Institute Admin, System Administrator) access doctypes directly through Frappe's built-in desk interface. Our job is to:

1. **Configure permissions** so admins see the right doctypes
2. **Configure roles** so access is scoped correctly
3. **Customize desk views** (list views, form layouts, dashboards) using Frappe's native customization
4. **Set up workspaces** so admins have a clean navigation experience

We do NOT:
- Build custom Vue/React admin pages
- Create separate admin API endpoints for CRUD (Frappe handles this)
- Duplicate Frappe Desk functionality

---

## Step 1 — Understand the Roles

### Current Role Hierarchy

| Role | Scope | Access Level |
|------|-------|-------------|
| **System Administrator** | All institutes (SaaS owner) | Full access to everything, can impersonate |
| **Institute Admin** | Single institute (company) | Full CRUD on own institute's education + routine doctypes |
| **Instructor** | Single institute | Limited — own classes, attendance, grading |
| **Student** | Single institute | Read-only on own data (via frontend portal) |
| **System Manager** | Site-level | Frappe default admin role |
| **System User** | Site-level | Basic desk access (required for all desk users) |

### Permission Isolation

- **Institute Admin** sees only their Company's data via User Permission on Company
- **System Administrator** has no Company restriction — sees all data
- **Instructor** sees only their assigned courses/groups
- **Student** accesses data only through the Nuxt frontend (not desk)

---

## Step 2 — What Admins Need Access To

### Institute Admin — Doctype Access

These doctypes should be accessible to Institute Admin in Frappe Desk:

| Doctype | Permissions | Notes |
|---------|------------|-------|
| `Student` | Read, Write, Create, Delete | Manage students |
| `Instructor` | Read, Write, Create, Delete | Manage teachers |
| `Program` | Read, Write, Create, Delete | Manage classes/streams |
| `Course` | Read, Write, Create, Delete | Manage subjects |
| `Topic` | Read, Write, Create | Manage chapters |
| `Article` | Read, Write, Create | Manage learning content |
| `Student Group` | Read, Write, Create, Delete | Manage sections |
| `Program Enrollment` | Read, Write, Create, Delete, Submit, Cancel | Enroll students |
| `Course Schedule` | Read, Write, Create, Delete | View timetable |
| `Student Attendance` | Read, Write, Create | View/mark attendance |
| `Assessment Plan` | Read, Write, Create, Submit, Cancel | Manage exams |
| `Assessment Result` | Read, Write, Create, Submit | View/enter grades |
| `Assessment Group` | Read | View exam categories |
| `Grading Scale` | Read, Write, Create | Define grading |
| `Fee Structure` | Read, Write, Create | Define fees |
| `Fees` | Read, Write, Create, Submit, Cancel | Manage fee records |
| `Room` | Read, Write, Create, Delete | Manage classrooms |
| `Academic Year` | Read, Write, Create | Manage years |
| `Academic Term` | Read, Write, Create | Manage terms |
| `Routine Generation` | Read, Write, Create, Submit, Cancel | Generate timetables |
| `Publication` | Read, Write, Create, Submit, Cancel | Manage notices/news |
| `Vidyaan Settings` | Read, Write | Configure settings |

### System Administrator — Doctype Access

Full access to everything Institute Admin has PLUS:

| Doctype | Additional Access |
|---------|------------------|
| `Company` | Create new institutes |
| `User` | Manage all users across institutes |
| `Role` | Manage roles |
| `User Permission` | Manage data isolation |
| All Education doctypes | No company filter restriction |

---

## Step 3 — Implementation Rules

### Rule 1: USE FRAPPE'S NATIVE PERMISSION SYSTEM

- Set permissions in the doctype's JSON definition (`permissions` array)
- Use `Role Permission Manager` for role-level tweaks
- Use `User Permission` for company-level data isolation
- NEVER write custom permission checks when Frappe's built-in system handles it

```python
# WRONG — custom permission check
if frappe.session.user_role != "Institute Admin":
    frappe.throw("No access")

# RIGHT — let Frappe handle it via doctype permissions
# Just set the right permissions in the doctype JSON
```

### Rule 2: USE FRAPPE'S NATIVE CUSTOMIZATION TOOLS

For admin UI customization, use these Frappe-native approaches:

| Need | Frappe Solution |
|------|----------------|
| Custom list view columns | `{doctype}_list.js` with `list_view.add_fields` |
| Custom form layout | `{doctype}.js` client script |
| Dashboard on form | `{doctype}_dashboard.py` |
| Custom buttons on form | `{doctype}.js` → `frm.add_custom_button()` |
| Sidebar links | Workspace configuration |
| Quick filters | `in_standard_filter` flag on fields |
| Default values | `default` property on fields |
| Conditional field visibility | `depends_on` property on fields |
| Print formats | Custom Print Format doctype |
| Report | Script Report or Query Report |

### Rule 3: USE WORKSPACES FOR NAVIGATION

Admins navigate via Frappe Workspaces, not custom sidebar.

The Vidyaan workspace should include:
- **Shortcuts** to frequently used doctypes (Student, Program, Assessment Plan)
- **Cards** grouping related doctypes (Academic Setup, Examinations, Library, etc.)
- **Number Cards** for quick stats (total students, active programs, etc.)
- **Charts** for visual dashboards (enrollment trends, attendance rates)

### Rule 4: AUTOMATION VIA HOOKS

Admin actions should trigger automation. Configure in `hooks.py`:

```python
doc_events = {
    "DocType": {
        "after_insert": "vidyaan.events.handler",
        "on_submit": "vidyaan.events.handler",
        "on_update": "vidyaan.events.handler",
        "on_cancel": "vidyaan.events.handler"
    }
}
```

**Key automation patterns for admin:**

| Admin Action | Auto-Result |
|-------------|-------------|
| Creates a new Program | Auto-create default Student Groups (sections) |
| Submits Assessment Plan | Auto-create Publication notice |
| Creates Program Enrollment | Auto-add student to Student Group |
| Configures Vidyaan Settings | Validate period timing conflicts |
| Submits Routine Generation | Auto-create Course Schedule entries |
| Creates new Instructor | Auto-link to Employee if exists |

---

## Step 4 — Implementation Flow

```
1. READ the docs (Step 0)
2. IDENTIFY what admin access/feature is needed
3. CHECK existing permissions — don't duplicate
4. DETERMINE if this is:
   a. A permission issue → Fix in doctype JSON or Role Permission Manager
   b. A desk UI issue → Use client script ({doctype}.js) or list script
   c. A navigation issue → Update Workspace
   d. An automation need → Add doc_events hook
   e. A reporting need → Create Script Report
5. IMPLEMENT using Frappe-native tools (not custom code)
6. TEST with an Institute Admin user (not System Administrator)
7. VERIFY company-level isolation works (admin sees only their data)
8. UPDATE docs/CUSTOMIZATIONS.md with any new permissions or hooks
```

---

## Step 5 — File Location Guide

| What | Where |
|------|-------|
| Doctype permissions | `vidyaan/<module>/doctype/<name>/<name>.json` → `permissions` array |
| Client scripts (form) | `vidyaan/<module>/doctype/<name>/<name>.js` |
| List view scripts | `vidyaan/<module>/doctype/<name>/<name>_list.js` |
| Dashboard config | `vidyaan/<module>/doctype/<name>/<name>_dashboard.py` |
| Hook registration | `vidyaan/hooks.py` |
| Event handlers | `vidyaan/events.py` |
| Workspace definition | `vidyaan/workspace/` |
| Custom fields | `vidyaan/setup/custom_fields.py` |
| Role creation | `vidyaan/setup/install.py` |
| Print formats | `vidyaan/<module>/print_format/` |
| Reports | `vidyaan/<module>/report/` |

---

## Step 6 — Checklist Before Committing

- [ ] Read all mandatory docs (Step 0)
- [ ] Used Frappe's native permission system (not custom checks)
- [ ] Used Frappe's native UI customization (client scripts, not custom pages)
- [ ] Did NOT build custom admin frontend pages
- [ ] Company-level data isolation verified (Institute Admin sees only their data)
- [ ] Automation hooks added where admin actions should cascade
- [ ] Tested with Institute Admin role (not System Administrator)
- [ ] Workspace updated if new doctypes/shortcuts added
- [ ] No new doctypes created without justification (check `AGENT_BACKEND.md` rules)
- [ ] Updated `docs/CUSTOMIZATIONS.md` with permission/hook changes
- [ ] Updated `docs/FEATURES.md` if feature status changed

---

## Quick Reference — Known Permission Bugs to Fix

From `docs/BACKLOG.md`:

| Bug | Issue | Fix |
|-----|-------|-----|
| BUG-002 | Publication approver role set to "Academic Manager" which doesn't exist | Change to "Institute Admin" |
| BUG-003 | Institute Admin can't manage Publications (only System Manager has access) | Add Institute Admin to Publication permissions with submit access |
| BUG-004 | Examiner validation chain is fragile (User → Employee → Instructor fails silently) | Add fallback lookup, log warnings |

---

## Quick Reference — Frappe Permission Levels

```json
{
    "permissions": [
        {
            "role": "Institute Admin",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "permlevel": 0
        }
    ]
}
```

Permission flags: `read`, `write`, `create`, `delete`, `submit`, `cancel`, `amend`, `report`, `export`, `import`, `share`, `print`, `email`, `set_user_permissions`

---

*This file is the law for admin panel work. Follow it.*
