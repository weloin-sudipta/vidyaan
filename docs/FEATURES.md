# Vidyaan - Features Reference

> Status Legend: **Done** = Implemented | **Partial** = Backend done, frontend pending | **Planned** = Designed but not built | **Idea** = Concept only

---

## 1. Multi-Tenant SaaS Isolation

**Status: Done**

Enables multiple schools to operate on a single Frappe site with complete data isolation.

| Capability | How It Works |
|-----------|-------------|
| Institute = Company | Each school is a `Company` doctype record |
| Mandatory Company field | Injected into 10 education doctypes via `custom_fields.py` |
| Auto-fill on forms | Default value pulls from `frappe.defaults.get_user_default('Company')` |
| List filtering | Company field is `in_standard_filter` and `in_list_view` |
| User Permission lockdown | Institute Admin gets User Permission on their Company — all queries auto-filtered |
| Ownership validation | Backend checks (e.g., routine generation) verify programs belong to admin's institute |

**Isolated Doctypes:** Student, Instructor, Program, Course, Topic, Article, Program Enrollment, Course Schedule, Student Group, Student Attendance

---

## 2. Setup Wizard

**Status: Done**

First-run onboarding that bootstraps a new institute.

| Step | What Happens |
|------|-------------|
| Login detection | `vidyaan_setup.js` checks `vidyaan_setup_complete === 0` on page load |
| Modal dialog | Non-dismissible dialog collects: Institute Name, Admin Email, Name, Password |
| Company creation | Creates Company doctype with auto-generated abbreviation |
| Admin user creation | Creates User with System Manager + Institute Admin roles |
| Redirect | Sends to `/app/vidyaan-dashboard` on success |

**Files:** `setup/wizard.py`, `public/js/vidyaan_setup.js`

---

## 3. AI-Powered Routine/Timetable Generation

**Status: Done**

Automated conflict-free timetable generation using Google OR-Tools CP-SAT constraint solver.

### Workflow
1. Admin creates `Routine Generation` document
2. Selects programs (classes) to generate for
3. Configures constraints (max subjects/day, teacher load, etc.)
4. Clicks "Check Readiness" — validates data completeness
5. Clicks "Generate Routine" — solver runs (up to timeout seconds)
6. Reviews generated `Routine Slots` in table
7. Submits — auto-creates native `Course Schedule` entries

### Constraints

| Constraint | Type | Default | Purpose |
|-----------|------|---------|---------|
| Teacher conflict | Hard | Always | No teacher teaches 2 sections at same time |
| Max subject/day/section | Hard | 2 | Prevent subject fatigue |
| Max teacher periods/day | Hard | 4 | Prevent teacher overload |
| Teacher weekly load (min-max) | Hard | 8-18 | Ensure fair distribution |
| Teacher preference | Soft | Via `is_preferred` | Optimize teacher satisfaction |

### Readiness Validation
Before generating, the system validates (all company-scoped):
- All programs belong to admin's institute
- Every program has courses assigned
- Every program has active Student Groups (sections)
- Every program has instructor mappings
- Enough teachers exist for total required slots

**Files:** `doctype/routine_generation/`, `doctype/routine_slot/`, `doctype/routine_generation_program/`

---

## 4. Instructor-Course Mapping

**Status: Done**

Links teachers to the subjects and classes they can teach — critical input for the routine solver.

| Field | Type | Purpose |
|-------|------|---------|
| `course` | Link → Course | Subject this teacher can teach |
| `program` | Link → Program | Class/stream they teach it in |
| `is_preferred` | Check | Soft preference flag for solver optimization |

Injected as a child table `course_mappings` on the native `Instructor` doctype via custom fields.

**Files:** `doctype/instructor_course_mapping/`, `setup/custom_fields.py`

---

## 5. Period Timing Configuration

**Status: Done**

Configurable time slots for each period in a school day, stored in `Vidyaan Settings`.

| Field | Type | Example |
|-------|------|---------|
| `period_number` | Int | 1, 2, 3... |
| `start_time` | Time | 09:00:00 |
| `end_time` | Time | 09:45:00 |

Default setup creates 5 periods from 09:00 to 13:00 (with a break after period 3).

Used by routine generation to convert abstract period numbers into actual Course Schedule times.

**Files:** `doctype/period_timing/`, `doctype/vidyaan_settings/`

---

## 6. Examinations & Assignments

**Status: Done (Zero New Doctypes)**

Complete assessment workflow using only native Education module doctypes.

### How It Works
- **Assessment Group** tree: "Exams" and "Assignments" as top-level categories
- **Assessment Plan**: Scheduled exam/assignment linked to Student Group, Course, Assessment Group
  - Includes: date, time, room, examiner, supervisor, max score, criteria
- **Assessment Result**: Per-student grade entry via Assessment Result Tool
- **Course Assessment Criteria**: Weightage (e.g., Assignments=20%, Final=80%)
- **Student Report Generation Tool**: Auto-calculates weighted scores → report cards

### Security Hook
Custom validation (`events.py`) ensures only the designated Examiner or Supervisor can enter/submit grades. Bypassed for System Manager and Institute Admin roles.

### Auto-Publication
When an Assessment Plan is submitted, a Publication (Notice) is auto-created targeting the relevant Student Group (`utils.py → create_assessment_publication`).

**Files:** `events.py` (validate_assessment_result), `utils.py` (create_assessment_publication)

---

## 7. Admit Cards

**Status: Done**

Custom Jinja print format on the Student doctype that auto-fetches upcoming Assessment Plans.

- Displays: Student info, Course, Date, Time, Room
- Format: ID-card style layout
- Trigger: Print → Select "Admit Card" format on any Student record

**Files:** `templates/admit_card.html`, `setup/install.py` (setup_admit_card_print_format)

---

## 8. Publication System

**Status: Done**

Unified system for school communications with approval workflow.

### Publication Types

| Type | Purpose | Required Fields |
|------|---------|----------------|
| Notice | Formal announcements | target_type, target_student_group (if targeted) |
| News | One-time publications | featured_image |
| Announcement | Quick general updates | (none extra) |

### Approval Workflow
- **By Role**: All users with the specified role get assigned
- **By User**: Specific user gets assigned
- Status flow: Draft → Pending → Approved/Rejected
- Approver sees Approve/Reject buttons on submitted documents

### Automation
- Assessment Plan submission → auto-creates Notice publication
- Auto-targets the Assessment Plan's Student Group
- Requires "Academic Manager" role approval

**Files:** `doctype/publication/`

---

## 9. Dashboard & Workspace

**Status: Done**

Vidyaan Dashboard workspace with:
- **Number Cards**: Total Students, Instructors, Programs, Courses
- **Shortcuts**: Organized into sections (Institute & Staff, Academics, Students, Routine & Settings)
- **Onboarding**: 3-step guided setup (Create Program, Add Course, Onboard Instructor)

**Files:** `setup/workspace.py`, `setup/onboarding.py`

---

## 10. Student/Teacher Frontend Portal

**Status: Partial (needs MaxEdu→Vidyaan migration)**

Nuxt 4 + Vue 3 application providing role-based portals.

### Student Portal
| Module | Pages |
|--------|-------|
| Dashboard | Attendance stats, assignments, exams, notices |
| Academics | Subjects, study materials, timetable |
| Exams | Schedule, results |
| Library | Book catalog, borrow requests, issued books |
| Documents | ID card, personal data, fees |
| Profile | Edit personal information |

### Teacher Portal
| Module | Pages |
|--------|-------|
| Dashboard | Daily routine, grading queue, announcements |
| Classes | Assigned classes/sections |
| Attendance | Mark student attendance |
| Assignments | Create, view submissions |
| Grading | Mark entry, performance, report cards |
| Lesson Planning | Course content planning |

### Admin Portal
| Module | Pages |
|--------|-------|
| Library | Book inventory, issuance tracking |
| Students | Student list, bulk operations |

### Known Issues
- Still branded as "MaxEdu" throughout
- API endpoints reference old `maxedu.api_folder` paths
- Role detection needs update for new role names

---

## 11. Weighted Grading & Report Cards

**Status: Done (Native)**

Uses native `Course Assessment Criteria` to define weightage per assessment type per course.

Example:
- Mathematics → Assignments: 20%, Mid-Term: 30%, Final: 50%
- System auto-calculates weighted scores via Student Report Generation Tool

No custom code needed — fully native Frappe Education feature.

---

## 12. Dynamic Application System

**Status: Idea (Plan 5 - Incomplete)**

Proposed system for Leave requests, Permission slips, etc. with multi-level approvals.

### Open Design Questions
1. Use Frappe Workflow system or custom Sequential Approval logic?
2. For multiple roles at one approval level, does ANY one approval move to next step?
3. Key-Value child table for dynamic fields — or separate doctypes per application type?

**Not yet implemented. Needs design decisions before proceeding.**
