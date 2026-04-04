# Vidyaan - Customizations to Existing Doctypes

This document lists every modification Vidyaan makes to native Frappe/ERPNext/Education doctypes — custom fields, document hooks, and behavioral changes.

---

## 1. Custom Fields Injected

### Company Field (Multi-Tenant Isolation)

The following **10 native Education doctypes** receive a mandatory `company` field:

| Doctype | Insert After | In List View | In Standard Filter |
|---------|-------------|-------------|-------------------|
| Student | `naming_series` | Yes | Yes |
| Instructor | `naming_series` | Yes | Yes |
| Program | *(first field)* | Yes | Yes |
| Course | *(first field)* | Yes | Yes |
| Topic | *(first field)* | Yes | Yes |
| Article | *(first field)* | Yes | Yes |
| Program Enrollment | *(first field)* | Yes | Yes |
| Course Schedule | *(first field)* | Yes | Yes |
| Student Group | *(first field)* | Yes | Yes |
| Student Attendance | *(first field)* | Yes | Yes |

**Field Details (same for all 10):**

```python
{
    "fieldname": "company",
    "label": "Institute / Company",
    "fieldtype": "Link",
    "options": "Company",
    "reqd": 1,                    # Mandatory
    "in_list_view": 1,
    "in_standard_filter": 1,
    "default": "frappe.defaults.get_user_default('Company')"
}
```

**Source:** `vidyaan/setup/custom_fields.py` → `create_vidyaan_custom_fields()`

---

### Instructor Course Mapping Table

The **Instructor** doctype also receives two additional custom fields:

| Field | Type | Label | Insert After |
|-------|------|-------|-------------|
| `course_mapping_section` | Section Break | "Course & Program Mapping" | `instructor_log` |
| `course_mappings` | Table → `Instructor Course Mapping` | "Courses I Teach" | `course_mapping_section` |

This adds a child table to the Instructor form where admins can define which subjects and classes each teacher is qualified to teach.

**Source:** `vidyaan/setup/custom_fields.py` → `create_vidyaan_custom_fields()`

---

## 2. Document Event Hooks

Defined in `vidyaan/hooks.py` under `doc_events`:

### Assessment Result — Validate & Before Submit

```python
"Assessment Result": {
    "validate": "vidyaan.events.validate_assessment_result",
    "before_submit": "vidyaan.events.validate_assessment_result"
}
```

**What it does:** Enforces that only the designated Examiner or Supervisor (from the linked Assessment Plan) can save or submit grades.

**Logic flow:**
1. Skip check for System Manager and Institute Admin roles
2. For Instructors: lookup the Assessment Plan linked to this result
3. Find all Employee records for the current user
4. Find all Instructor records linked to those employees
5. Check if any of those instructors match the plan's `examiner` or `supervisor`
6. If no match → throw permission error

**Source:** `vidyaan/events.py` → `validate_assessment_result(doc, method)`

---

### Assessment Plan — On Submit

```python
"Assessment Plan": {
    "on_submit": "vidyaan.utils.create_assessment_publication"
}
```

**What it does:** Automatically creates a Publication (Notice) when an Assessment Plan is submitted.

**Logic flow:**
1. Check if a publication already exists with name `"Assessment: {plan_name}"`
2. If exists, return (prevent duplicates)
3. Create new Publication:
   - Title: `"Assessment: {plan_name}"`
   - Type: `"Notice"`
   - Content: HTML with course, date, assessment_group details
   - Target: `plan.student_group`
   - Status: `"Draft"`
   - Approval: By Role → `"Academic Manager"`
4. Insert with `ignore_permissions=True`
5. Show success message (catches and logs errors silently)

**Source:** `vidyaan/utils.py` → `create_assessment_publication(doc, method)`

---

## 3. Boot Info Extension

```python
# hooks.py
extend_bootinfo = "vidyaan.utils.extend_bootinfo"
```

**What it does:** Adds `vidyaan_setup_complete` flag to the Frappe boot data sent to the browser on every page load.

**Purpose:** The frontend setup wizard (`vidyaan_setup.js`) checks this flag — if `0`, shows the mandatory setup dialog.

**Source:** `vidyaan/utils.py` → `extend_bootinfo(bootinfo)`

---

## 4. App-Include JavaScript

```python
# hooks.py
app_include_js = "/assets/vidyaan/js/vidyaan_setup.js"
```

**What it does:** Loads the setup wizard JavaScript on every Desk page.

**Behavior:**
- On `frappe.ready()`, checks: user is not Guest AND `vidyaan_setup_complete === 0`
- Shows a non-dismissible modal dialog collecting institute details
- Calls `vidyaan.setup.wizard.complete_setup()` whitelisted method
- On success, redirects to `/app/vidyaan-dashboard`

**Source:** `vidyaan/public/js/vidyaan_setup.js`

---

## 5. Custom Print Format

### Admit Card (on Student Doctype)

**What it does:** Adds an "Admit Card" print format option to the Student doctype.

**Details:**
- Name: `"Admit Card"`
- DocType: `Student`
- Format Type: Jinja
- Template: Fetches upcoming Assessment Plans and displays exam schedule in ID card format

**Created by:** `vidyaan/setup/install.py` → `setup_admit_card_print_format()`

**Template:** `vidyaan/templates/admit_card.html`

---

## 6. Roles & Permissions Added

### Custom Roles Created

| Role | Has Desk Access | Purpose |
|------|----------------|---------|
| Institute Admin | Yes (via System User) | School administrator with full education CRUD |
| Instructor | Yes (via System User) | Teacher role (minimal permissions, per-document access) |

**Note:** System Administrator and System Manager are native Frappe roles — Vidyaan assigns permissions to them but doesn't create them.

### Permission Grants

Both **System Administrator** and **Institute Admin** receive full permissions (Read, Write, Create, Delete, Select, Share) on:

**Core Doctypes:**
- Company, User, Employee, Instructor, Student, Program, Course
- Topic, Article, Program Enrollment, Student Group, Student Attendance
- Course Schedule, Routine Generation, Vidyaan Settings

**UI Doctypes:**
- Page, Workspace, DocType, Module Def, Print Format, Report

**Source:** `vidyaan/setup/roles.py` → `create_roles()`

---

## 7. Assessment Group Tree Nodes

Two Assessment Group nodes are created during installation:

| Name | Is Group | Parent |
|------|----------|--------|
| Exams | Yes | All Assessment Groups (root) |
| Assignments | Yes | All Assessment Groups (root) |

These serve as categories to distinguish exams from homework/assignments when creating Assessment Plans.

**Source:** `vidyaan/setup/install.py` → `setup_assessment_groups()`

---

## 8. Module Onboarding Steps

Three onboarding steps are created for the Vidyaan module:

| Step | Action DocType | Description |
|------|---------------|-------------|
| Create a Class Program | Program | "Set up your first Class to organize subjects" |
| Add a Subject Course | Course | "Create subjects like Mathematics, Physics" |
| Onboard Instructors | Instructor | "Add Teacher profiles to manage classes" |

Bundled into Module Onboarding: **"Vidyaan Institute Setup"**

**Source:** `vidyaan/setup/onboarding.py`

---

## 9. Default User Created

| Field | Value |
|-------|-------|
| Email | vidyaan@weloin.com |
| Full Name | Vidyaan Administrator |
| Password | Vidyan@2026 |
| Roles | System User, System Administrator |

**Source:** `vidyaan/setup/user.py` → `create_default_user()`

---

## Summary Table

| What Changed | Where | Type of Change |
|-------------|-------|---------------|
| Student | Custom Field: `company` | Mandatory Link to Company |
| Instructor | Custom Field: `company` | Mandatory Link to Company |
| Instructor | Custom Field: `course_mappings` | Child Table (Instructor Course Mapping) |
| Program | Custom Field: `company` | Mandatory Link to Company |
| Course | Custom Field: `company` | Mandatory Link to Company |
| Topic | Custom Field: `company` | Mandatory Link to Company |
| Article | Custom Field: `company` | Mandatory Link to Company |
| Program Enrollment | Custom Field: `company` | Mandatory Link to Company |
| Course Schedule | Custom Field: `company` | Mandatory Link to Company |
| Student Group | Custom Field: `company` | Mandatory Link to Company |
| Student Attendance | Custom Field: `company` | Mandatory Link to Company |
| Assessment Result | Doc Event: validate + before_submit | Examiner/Supervisor permission check |
| Assessment Plan | Doc Event: on_submit | Auto-create Publication notice |
| Assessment Group | Tree nodes | "Exams" + "Assignments" categories |
| Student | Print Format | "Admit Card" Jinja template |
| Boot Info | extend_bootinfo | Setup completion flag |
| Desk JS | app_include_js | Setup wizard dialog |
