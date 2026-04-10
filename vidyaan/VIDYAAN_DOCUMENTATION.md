# Vidyaan — School ERP System

## Overview

Vidyaan is a comprehensive **School ERP system** built on the **Frappe Framework** that extends ERPNext, HRMS, and Education modules. It provides a complete school management solution with multi-tenant SaaS isolation, student/teacher portals, attendance tracking, exam management, assignment handling, fees management, and more.

---

## Architecture

### Tech Stack
- **Backend**: Frappe Framework (Python)
- **Frontend**: Nuxt 4 (Vue 3 + TypeScript)
- **Database**: MariaDB (via Frappe)
- **Dependencies**: ERPNext, HRMS, Education (Frappe modules)

### Multi-Tenant Isolation
Vidyaan uses the `Company` field on all core education doctypes to enable per-school data isolation:
- Student, Instructor, Program, Course, Topic, Article
- Program Enrollment, Course Schedule, Student Group, Student Attendance

### Required Apps
```python
required_apps = ["erpnext", "hrms", "education"]
```

---

## Core Modules

### 1. Hooks & Events (`hooks.py`, `events.py`, `utils.py`)

**hooks.py**:
- App configuration with required apps
- Document events:
  - `Assessment Result`: validate/before_submit for grading permissions
  - `Assessment Plan`: on_submit → auto-create Publication
  - `Program Enrollment`: after_insert → auto-add to student groups & course enrollments
- Role home pages (Institute Admin, System Manager, Administrator → `vidyaan/dashboard`)
- Whitelisted method overrides for library management
- Website context (favicon, brand)

**events.py**:
- `on_program_enrollment_created()`: Auto-adds student to student groups and creates course enrollments
- `validate_assessment_result()`: Ensures only examiner/supervisor can grade (allows System Manager/Institute Admin override)

**utils.py**:
- `extend_bootinfo()`: Sets `vidyaan_setup_complete` flag
- `create_assessment_publication()`: Auto-creates Publication (Notice) when Assessment Plan is submitted

---

### 2. API Modules (`api_folder/`)

#### Profile Module (`profile.py`)
Core user resolution functions:
- `_get_user_company()`: Gets company from User Permission
- `_get_student_for_user()`: Resolves User → Student via `student_email_id`
- `_get_instructor_for_user()`: Resolves User → Employee → Instructor (multiple paths)
- `_get_primary_role()`: Determines user role (admin/teacher/student/other)

Public APIs:
- `get_user_info()`: Basic user info + role
- `get_profile()`: Detailed profile based on role (student/teacher)
- `update_profile()`: Update user/student fields

#### Student Module (`student.py`)
- `get_student_dashboard_data()`: Aggregated dashboard (attendance, exams, assignments, fees, today's classes, notices)
- `get_student_by_institute()`: Students with enrollment details (for teacher view)

#### Schedule Module (`schedule.py`)
- `get_student_schedule()`: Weekly timetable from Course Schedule

#### Attendance Module (`attendance.py`)
- `get_attendance()`: Monthly attendance records (JS 0-based month keys)
- `get_attendance_summary()`: Overall summary + monthly breakdown

#### Exam Module (`exam.py`)
- `get_exams()`: Assessment plans for student's groups
- `get_results()`: Student's assessment results
- `get_admit_data()`: Admit card data for upcoming exams

#### Fees Module (`fees.py`)
- `get_my_fee()`: All fee records with components

#### Notices Module (`notices.py`)
- `get_approved_notices()`: All approved publications (notices, news)
- `get_notice()`: Single publication by slug

#### Subjects Module (`subjects.py`)
- `get_program()`: Student's program with courses and topics (nested structure)

#### Study Materials Module (`study_materials.py`)
- `get_study_materials()`: Articles for student's courses
- `get_instructor_courses_with_topics()`: Instructor courses with nested topics
- `get_materials_by_teacher()`: Articles created by instructor
- `create_study_material()`: Create Article
- `update_study_material()`: Update Article
- `delete_study_material()`: Delete Article

#### Assignments Module (`assignments.py`)
**New Assignment System (Custom DocType):**
- `create_assignment()`: Create Assignment (Draft status)
- `publish_assignment()`: Publish and populate submissions
- `update_assignment()`: Update Draft assignment
- `delete_assignment()`: Delete Draft assignment
- `close_assignment()`: Close Published assignment
- `get_instructor_assignments()`: All instructor's assignments
- `get_assignment_detail()`: Full assignment with submissions
- `grade_submission()`: Grade a student's submission
- `submit_student_assignment()`: Student submits assignment (file/text)
- `get_student_assignments()`: Student's published assignments

**Legacy System (Assessment Plan):**
- `get_assignments_legacy()`: Assignment-type Assessment Plans
- `create_assignment_template_legacy()`: Create Assessment Plan
- `publish_assignment_template_legacy()`: Submit Assessment Plan
- `grade_assignment_legacy()`: Grade Assessment Result
- etc.

**Shared Helpers:**
- `get_instructor_courses()`: Instructor's courses
- `get_instructor_student_groups()`: Instructor's student groups (explicit + implicit)

#### Teacher Classes Module (`teachers_classes.py`)
- `get_my_classes()`: Instructor's class schedule for a date
- `mark_attendance_bulk()`: Bulk mark attendance for a course schedule

#### Teacher Grading Module (`teacher_grading.py`)
- `get_my_exams()`: Assessment plans where user is examiner/supervisor
- `get_my_courses()`: Instructor's course mappings
- `get_exam_students()`: Students in an assessment plan with results
- `submit_exam_results()`: Bulk save/submit results
- `submit_single_result()`: Single student result

#### Teacher Data Module (`teacher_data.py`)
- `get_my_profile()`: Instructor's profile with courses, groups, employee data
- `get_teacher_pending_tasks()`: Pending attendance, grading, applications

#### Faculty Module (`faculty.py`)
- `get_all_faculty_data()`: All instructors for the institute with course mappings

#### Applications Module (`applications.py`)
- `get_available_application_types()`: Available application types with workflow config
- `get_my_applications()`: Student's all applications (NOC, Request, Leave)
- `get_application_detail()`: Full application with workflow timeline
- `submit_noc()`: Submit Student NOC
- `submit_request()`: Submit Student Request
- `submit_leave()`: Submit Student Leave Application
- `get_leave_options()`: Student groups/schedules for leave
- `get_teacher_pending_applications()`: Teacher's pending applications
- `get_teacher_leave_statistics()`: Application statistics
- `review_application()`: Approve/reject via workflow

#### Event Module (`event.py`)
- `get_all_events()`: School events from Frappe Event doctype

---

### 3. Custom DocTypes (`doctype/`)

| DocType | Purpose |
|---------|---------|
| **Assignment** | New assignment system with target groups and submissions |
| **Assignment Target Group** | Link Assignment → Student Groups |
| **Assignment Submission** | Student submission records (file, text, score, status) |
| **Student Request** | General student requests |
| **Student NOC** | No Objection Certificate applications |
| **Publication** | Notices, news, announcements |
| **Vidyaan Settings** | App configuration |
| **Period Timing** | Class period timings |
| **Routine Generation Program** | Timetable generation |
| **Instructor Course Mapping** | Link Instructor → Course + Program |

---

### 4. Setup & Installation (`setup/`)

#### custom_fields.py
Creates custom fields on standard doctypes:
- `company` field (mandatory) on: Student, Instructor, Program, Course, Topic, Article, Program Enrollment, Course Schedule, Student Group, Student Attendance
- `course_mappings` table on Instructor doctype
- `room` field on Student Group (dedicated classroom)
- `workflow_state` on Student Leave Application

#### roles.py
Creates roles and applies permissions:
- **Institute Admin**: Full CRUD on education + vidyaan doctypes
- **Instructor**: Read on most, CRUD on content, attendance, assessment plans/results
- **Librarian**: (placeholder role)

#### Other Setup Files
- `install.py`: Post-install hook
- `workspace.py`: Desk workspace configuration
- `onboarding.py`: Onboarding steps
- `operations/institute_setup.py`: Institute setup operations
- `operations/install_fixtures.py`: Install default data

---

## User Roles & Permissions

### Role Hierarchy
1. **System Manager / Administrator**: Full access
2. **Institute Admin**: Full CRUD on education doctypes
3. **Instructor**: Limited - can teach, mark attendance, grade
4. **Student**: Portal access - view schedule, grades, assignments, fees

### Permission Model
- Role-based permissions via `roles.py`
- Document-level security via `events.py` (assessment grading)
- User permission for Company isolation

---

## Key Features

### Student Portal
- Dashboard (attendance, exams, assignments, fees, today's classes)
- Schedule/Timetable
- Exam results & Admit cards
- Fee payment tracking
- Notices/Publications
- Study materials
- Submit assignments
- Apply for Leave/NOC/Requests

### Teacher Portal
- Class schedule with attendance marking
- Create/manage assignments (new system + legacy)
- Grade submissions
- View student list
- Pending tasks (attendance, grading, applications)
- Applications for approval
- Teacher profile

### Admin Features
- Multi-school isolation via Company field
- Auto-publish notices on assessment plan submit
- Auto-enroll students in groups/courses
- Workflow-based application processing

---

## Data Flow

```
User Login
    ↓
profile._get_primary_role() → determine role
    ↓
Role-based API routing:
    ├── Student → student.py, schedule.py, attendance.py, etc.
    ├── Teacher → teachers_classes.py, teacher_grading.py, etc.
    └── Admin → full access
```

```
Program Enrollment Created
    ↓
events.on_program_enrollment_created()
    ├── _auto_add_to_student_groups()
    └── _auto_create_course_enrollments()
```

```
Assessment Plan Submitted
    ↓
utils.create_assessment_publication()
    └── Creates Publication (Notice)
```

---

## Frontend Integration

The backend provides JSON APIs consumed by Nuxt 4 frontend:
- Whitelisted methods (`@frappe.whitelist()`)
- Response format matches frontend expectations (field name mapping)
- Backward compatibility maintained via multiple field names

---

## Configuration

### Website Context (hooks.py)
```python
website_context = {
    "favicon": "/assets/education/edu-logo.svg",
    "splash_image": "/assets/education/edu-logo.svg",
    "brand_html": '<img src="/assets/education/edu-logo.svg"/> Vidyaan',
}
```

### Role Home Pages
```python
role_home_page = {
    "Institute Admin": "vidyaan/dashboard",
    "System Manager": "vidyaan/dashboard",
    "Administrator": "vidyaan/dashboard",
}
```

---

## Error Handling

- Frappe permissions enforced on sensitive operations
- Workflow-based state validation for applications
- Proper error messages with `frappe.throw()` and `frappe.log_error()`
- Graceful degradation (non-critical failures logged, not thrown)

---

## Extensibility

### Override Whitelisted Methods
```python
override_whitelisted_methods = {
    "vidyaan.library_management.api.get_catalog": "vidyaan.library.api.get_catalog",
    # ... more overrides
}
```

### Document Events
Custom logic hooks on standard doctypes (Assessment Result, Assessment Plan, Program Enrollment)

---

## Database Schema Key Relationships

```
Student ←→ Program Enrollment ←→ Program ←→ Program Course ←→ Course
                ↓
        Student Group Student ←→ Student Group ←→ Student Group Instructor
                ↓
            Course Schedule ←→ Assessment Plan ←→ Assessment Result
                ↓
            Student Attendance

Instructor ←→ Employee ←→ User
    ↓
Instructor Course Mapping
```

---

## File Structure

```
vidyaan/
├── vidyaan/
│   ├── api.py                    # Entry point (proxies)
│   ├── api_folder/
│   │   ├── profile.py            # User resolution
│   │   ├── student.py            # Student dashboard
│   │   ├── schedule.py           # Timetable
│   │   ├── attendance.py         # Attendance
│   │   ├── exam.py               # Exams & results
│   │   ├── fees.py               # Fees
│   │   ├── notices.py            # Publications
│   │   ├── assignments.py        # Assignments (new + legacy)
│   │   ├── teachers_classes.py   # Teacher schedule & attendance
│   │   ├── teacher_grading.py    # Teacher grading
│   │   ├── teacher_data.py       # Teacher profile & tasks
│   │   ├── applications.py       # Student applications
│   │   ├── study_materials.py   # Articles
│   │   ├── subjects.py          # Program subjects
│   │   ├── faculty.py            # All faculty
│   │   └── event.py             # Events
│   ├── doctype/
│   │   ├── assignment/           # Assignment system
│   │   ├── assignment_submission/
│   │   ├── assignment_target_group/
│   │   ├── student_request/
│   │   ├── student_noc/
│   │   ├── publication/
│   │   ├── vidyaan_settings/
│   │   ├── period_timing/
│   │   ├── routine_generation_program/
│   │   └── instructor_course_mapping/
│   ├── setup/
│   │   ├── custom_fields.py      # Custom field injection
│   │   ├── roles.py              # Role & permission setup
│   │   ├── install.py            # Post-install
│   │   └── ... (workspace, onboarding, etc.)
│   ├── hooks.py                  # App hooks
│   ├── events.py                 # Document events
│   └── utils.py                  # Utility functions
└── README.md
```

---

## Version Info

- **App Name**: Vidyaan
- **Publisher**: Weloin
- **License**: MIT
- **Description**: School ERP system