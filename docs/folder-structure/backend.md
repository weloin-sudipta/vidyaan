# Vidyaan Backend Documentation

> **Framework:** Frappe Framework 15 + ERPNext 15 + Education Module
> **Architecture:** Multi-tenant SaaS with Company-based isolation
> **Location:** `apps/vidyaan/vidyaan/`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Multi-Tenant Isolation](#2-multi-tenant-isolation)
3. [Custom Doctypes](#3-custom-doctypes)
4. [Native Doctypes Used](#4-native-doctypes-used)
5. [Customizations to Native Doctypes](#5-customizations-to-native-doctypes)
6. [API Endpoints](#6-api-endpoints)
7. [Document Event Hooks](#7-document-event-hooks)
8. [Setup & Installation](#8-setup--installation)
9. [Roles & Permissions](#9-roles--permissions)

---

## 1. Architecture Overview

```
Frappe Framework 15
├── ERPNext 15 (Core business logic)
├── Education Module (Academic entities)
└── Vidyaan App (Customizations + SaaS features)
    ├── Custom Doctypes (7 new)
    ├── Custom Fields (11 native doctypes modified)
    ├── Document Hooks (2 doctypes extended)
    ├── API Methods (69 whitelisted endpoints)
    ├── Setup Wizard (Company onboarding)
    └── Multi-tenant Isolation (Company field injection)
```

**Key Design Decisions:**
- **Multi-tenant SaaS:** Each school = one Company record, all data isolated by `company` field
- **Minimal Custom Doctypes:** Reuse Education module entities where possible
- **Company Field Injection:** Automatic `company` field added to 10 native doctypes
- **Role-Based Access:** Institute Admin (school admin) vs System Administrator (SaaS admin)
- **Setup Wizard:** Mandatory first-run configuration for new installations

---

## 2. Multi-Tenant Isolation

### Company Field Injection

Vidyaan automatically adds a mandatory `company` field to **10 native Education doctypes**:

| Doctype | Field Location | Purpose |
|---------|---------------|---------|
| Student | After `naming_series` | Student belongs to institute |
| Instructor | After `naming_series` | Teacher belongs to institute |
| Program | First field | Class belongs to institute |
| Course | First field | Subject belongs to institute |
| Topic | First field | Chapter belongs to institute |
| Article | First field | Material belongs to institute |
| Program Enrollment | First field | Enrollment belongs to institute |
| Course Schedule | First field | Timetable slot belongs to institute |
| Student Group | First field | Section belongs to institute |
| Student Attendance | First field | Attendance belongs to institute |

**Field Specification (identical for all):**
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

**Implementation:** `vidyaan/setup/custom_fields.py` → `create_vidyaan_custom_fields()`

### Data Isolation

- All queries automatically filtered by user's default Company
- User Permissions created: `User → Company` for each institute admin
- API methods respect Company context
- No cross-institute data leakage

---

## 3. Custom Doctypes

Vidyaan adds **7 new doctypes** to extend Education module functionality:

### 3.1 Vidyaan Settings (Singleton)

> Global configuration for timetable generation and institute defaults.

**Key Fields:**
- `company` (Link) - Institute
- `default_academic_year` (Link) - Current year
- `default_periods_per_day` (Int) - Default 5
- `period_timings` (Table) - Child table of time slots

**Purpose:** Central config for routine generation solver.

### 3.2 Period Timing (Child Table)

> Time slots for school periods.

**Fields:** `period_number`, `start_time`, `end_time`

**Parent:** Vidyaan Settings

### 3.3 Instructor Course Mapping (Child Table)

> Maps teachers to subjects they can teach.

**Fields:** `course`, `program`, `is_preferred`

**Parent:** Instructor doctype (custom field)

### 3.4 Routine Generation (Main DocType)

> AI-powered timetable generator using OR-Tools.

**Key Methods:**
- `check_readiness()` - Validates data completeness
- `generate_routine()` - Runs constraint solver
- `create_course_schedules()` - Converts output to Course Schedules

**Fields:** Programs batch, day checkboxes, constraint sliders, output slots table.

### 3.5 Routine Slot (Child Table)

> Individual generated timetable entry.

**Fields:** `student_group`, `day`, `period`, `instructor`, `course`, `room`

**Parent:** Routine Generation

### 3.6 Routine Generation Program (Child Table)

> Links programs to a generation batch.

**Fields:** `program` (Link)

**Parent:** Routine Generation

### 3.7 Publication (Main DocType)

> School communications with approval workflow.

**Fields:** `title`, `type`, `content`, `target_student_group`, `approver_role`, `status`

**Workflow:** Draft → Pending → Approved/Rejected

---

## 4. Native Doctypes Used

Vidyaan leverages **20+ native Education doctypes** without modification:

| Category | Doctypes |
|----------|----------|
| **Academic Structure** | Program, Course, Topic, Article |
| **People** | Student, Instructor, Employee, User, Guardian |
| **Enrollment** | Program Enrollment, Student Group |
| **Scheduling** | Course Schedule, Academic Year, Academic Term |
| **Assessment** | Assessment Plan, Assessment Result, Assessment Group, Grading Scale |
| **Attendance** | Student Attendance |
| **Finance** | Fee Structure, Fees |
| **Facilities** | Room |
| **Organization** | Company |

---

## 5. Customizations to Native Doctypes

### Custom Fields Added

**Instructor Doctype:**
- `course_mappings` (Table) - Child table for teacher-subject mapping

### Document Event Hooks

**Assessment Result:**
- `validate` + `before_submit`: Enforces examiner/supervisor permissions
- **Logic:** Only designated examiner or supervisor can grade

**Assessment Plan:**
- `on_submit`: Auto-creates Publication notice for exams
- **Logic:** Creates draft notice targeting the student group

### Print Formats

**Student Doctype:**
- "Admit Card" format (Jinja template)
- Shows upcoming exams in ID card layout

---

## 6. API Endpoints

Vidyaan provides **69 whitelisted API methods** organized by module:

### Core Setup
- `vidyaan.setup.wizard.complete_setup()` - Setup wizard completion

### Profile & Authentication
- `vidyaan.api_folder.profile.get_user_info()` - User profile with role detection

### Assignments
- `vidyaan.api_folder.assignments.get_assignments()` - Student assignments list
- `vidyaan.api_folder.assignments.submit_assignment()` - File upload submission

### Attendance
- `vidyaan.api_folder.attendance.get_attendance()` - Calendar data
- `vidyaan.api_folder.attendance.get_attendance_summary()` - Stats

### Exams & Grading
- `vidyaan.api_folder.exam.get_exams()` - Schedule
- `vidyaan.api_folder.exam.get_results()` - Results
- `vidyaan.api_folder.grading.*` - Mark entry and validation

### Teacher Data
- `vidyaan.api_folder.teacher_data.*` - Dashboard data, schedules

### Library Management
- `vidyaan.library_management.api.*` - Books, borrowing, requests

### Routine Generation
- `vidyaan.api_folder.routine.check_readiness()` - Pre-generation validation
- `vidyaan.api_folder.routine.generate_routine()` - AI solver execution

### Events & Notices
- `vidyaan.api_folder.event.get_all_events()` - Calendar events
- `vidyaan.api_folder.desk_approval.*` - Publications workflow

---

## 7. Document Event Hooks

### Assessment Result Validation

```python
# vidyaan/events.py
def validate_assessment_result(doc, method):
    # Skip for System Manager / Institute Admin
    if "System Manager" in frappe.get_roles() or "Institute Admin" in frappe.get_roles():
        return
    
    # For instructors: check if they're the designated examiner/supervisor
    plan = frappe.get_doc("Assessment Plan", doc.assessment_plan)
    user_employees = frappe.get_all("Employee", filters={"user_id": frappe.session.user})
    
    for emp in user_employees:
        instructor = frappe.get_value("Instructor", {"employee": emp.name})
        if instructor and instructor in [plan.examiner, plan.supervisor]:
            return
    
    frappe.throw("Only the designated examiner or supervisor can submit grades")
```

### Assessment Publication Creation

```python
# vidyaan/utils.py
def create_assessment_publication(doc, method):
    # Auto-create notice when assessment plan is submitted
    if frappe.get_value("Publication", {"title": f"Assessment: {doc.name}"}):
        return  # Already exists
    
    pub = frappe.get_doc({
        "doctype": "Publication",
        "title": f"Assessment: {doc.name}",
        "type": "Notice",
        "content": f"Assessment scheduled for {doc.course} on {doc.date}",
        "target_student_group": doc.student_group,
        "status": "Draft",
        "approver_role": "Academic Manager"
    })
    pub.insert(ignore_permissions=True)
```

---

## 8. Setup & Installation

### Installation Sequence

1. **Custom Fields:** Inject `company` field into 10 native doctypes
2. **Roles:** Create "Institute Admin" and "Instructor" roles
3. **Permissions:** Grant full access to admins on education doctypes
4. **Assessment Groups:** Create "Exams" and "Assignments" tree nodes
5. **Print Format:** Install "Admit Card" template
6. **Onboarding:** Create module onboarding steps
7. **Default User:** Create `vidyaan@weloin.com` admin account

### Setup Wizard

- **Trigger:** `vidyaan_setup_complete` bootinfo flag = 0
- **Dialog:** Non-dismissible modal collecting institute details
- **Completion:** Calls `complete_setup()` whitelisted method
- **Redirect:** To `/app/vidyaan-dashboard`

---

## 9. Roles & Permissions

### Custom Roles Created

| Role | Desk Access | Permissions |
|------|-------------|-------------|
| **Institute Admin** | Yes | Full CRUD on all education doctypes within their Company |
| **Instructor** | Yes | Limited permissions, per-document access control |

### Permission Matrix

**System Administrator & Institute Admin:**
- Full access (Create, Read, Write, Delete, Submit) on:
  - All Vidyaan custom doctypes
  - All Education doctypes
  - Company, User, Employee records

**Instructor:**
- Read access to assigned Student Groups, Courses
- Write access to Assessment Results (only as designated examiner)
- Create access to Course Schedules (limited)

---

## Doctype Relationships

```
Company (Institute)
├── Vidyaan Settings
│   └── Period Timing
├── Program (Class)
│   ├── Course (Subject)
│   │   ├── Topic → Article
│   │   └── Assessment Criteria
│   ├── Student Group (Section)
│   │   ├── Student
│   │   ├── Instructor
│   │   │   └── Instructor Course Mapping
│   │   ├── Course Schedule
│   │   ├── Assessment Plan → Assessment Result
│   │   └── Student Attendance
│   ├── Program Enrollment
│   └── Fee Structure → Fees
├── Routine Generation
│   ├── Routine Generation Program
│   └── Routine Slot
└── Publication
```

---

*Last updated: 2026-04-01*