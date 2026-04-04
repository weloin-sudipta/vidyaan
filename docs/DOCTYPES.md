# Vidyaan - Doctype Reference

This document maps every school concept to its underlying Frappe doctype, explains each custom doctype's purpose and fields, and shows how native doctypes are reused.

---

## School Concept → Doctype Mapping

| School Concept | Doctype | Source | Notes |
|---------------|---------|--------|-------|
| Institute / School | `Company` | ERPNext | Each school = one Company record |
| Administrator | `User` + Role | Frappe | "Institute Admin" role + User Permission on Company |
| Teacher | `User` → `Employee` → `Instructor` | Education | Chain: login → HR record → teaching record |
| Class / Stream | `Program` | Education | e.g., "Class 10 Science", "Class 12 Arts" |
| Subject | `Course` | Education | e.g., "Mathematics", "Physics" |
| Chapter | `Topic` | Education | Under a Course |
| Lesson / Material | `Article` | Education | Content pages under Topics |
| Student | `Student` | Education | Core student record |
| Enrollment | `Program Enrollment` | Education | Links Student to Program for an Academic Year |
| Section / Division | `Student Group` | Education | e.g., "Class 10A", "Class 10B" |
| Attendance | `Student Attendance` | Education | Per-student, per-date status |
| Class Calendar Slot | `Course Schedule` | Education | Instructor + Student Group + Course + Time |
| Academic Year | `Academic Year` | Education | e.g., "2025-2026" |
| Academic Term | `Academic Term` | Education | e.g., "First Term", "Second Term" |
| Exam / Test | `Assessment Plan` | Education | Scheduled assessment event |
| Marks / Grade | `Assessment Result` | Education | Per-student score for an Assessment Plan |
| Exam Category | `Assessment Group` | Education | Tree: Exams, Assignments |
| Grading Scale | `Grading Scale` | Education | A+, A, B+, etc. with ranges |
| Fee Template | `Fee Structure` | Education | Per-program fee components |
| Fee Invoice | `Fees` | Education | Per-student fee record |
| Classroom | `Room` | Education | Physical room/lab |
| Guardian / Parent | `Guardian` | Education | Parent/guardian record |
| School House | `School House` | Education | Inter-house grouping |
| Timetable Config | `Vidyaan Settings` | **Vidyaan** | Period timings + solver defaults |
| Period Time Slot | `Period Timing` | **Vidyaan** | Child table: period start/end times |
| Teacher-Subject Map | `Instructor Course Mapping` | **Vidyaan** | Child table: which teacher teaches what |
| Timetable Generator | `Routine Generation` | **Vidyaan** | AI-powered timetable creation |
| Timetable Entry | `Routine Slot` | **Vidyaan** | Child table: generated schedule entry |
| Programs for Routine | `Routine Generation Program` | **Vidyaan** | Child table: programs in a batch |
| Notice / News | `Publication` | **Vidyaan** | School communications with approval |

---

## Custom Doctypes (Created by Vidyaan)

### 1. Vidyaan Settings (Single DocType)

> Global configuration singleton. One record per site.

**Section: General Settings**

| Field | Type | Options | Default | Required |
|-------|------|---------|---------|----------|
| `company` | Link | Company | — | No |
| `default_academic_year` | Link | Academic Year | — | No |
| `default_academic_term` | Link | Academic Term | — | No |

**Section: Routine Generation Defaults**

| Field | Type | Options | Default | Required |
|-------|------|---------|---------|----------|
| `default_periods_per_day` | Int | — | 5 | No |
| `default_days` | Data | — | "Monday,Tuesday,Wednesday,Thursday,Friday" | No |
| `max_subject_per_day` | Int | — | 2 | No |
| `max_teacher_periods_per_day` | Int | — | 4 | No |
| `min_teacher_weekly_load` | Int | — | 8 | No |
| `max_teacher_weekly_load` | Int | — | 18 | No |
| `solver_timeout` | Int | — | 30 | No |

**Section: Period Timings**

| Field | Type | Options |
|-------|------|---------|
| `period_timings` | Table | Period Timing |

**Permissions:** System Administrator, System Manager, Institute Admin (Read + Write)

---

### 2. Period Timing (Child Table)

> Time slots for each period in a school day. Used by Vidyaan Settings.

| Field | Type | Default | Required |
|-------|------|---------|----------|
| `period_number` | Int | — | Yes |
| `start_time` | Time | — | Yes |
| `end_time` | Time | — | Yes |

**Parent:** Vidyaan Settings (`period_timings` field)

---

### 3. Instructor Course Mapping (Child Table)

> Maps which courses an instructor can teach in which programs.

| Field | Type | Options | Required | Notes |
|-------|------|---------|----------|-------|
| `course` | Link | Course | Yes | Subject |
| `course_name` | Data | — | No | Read-only, fetched from Course |
| `program` | Link | Program | Yes | Class/stream |
| `is_preferred` | Check | — | No | Soft preference for solver |

**Parent:** Instructor doctype (`course_mappings` custom field)

---

### 4. Routine Generation (Main DocType - Submittable)

> Orchestrates AI timetable generation. Naming: `VDY-RTN-.YYYY.-`

**Section: Configuration**

| Field | Type | Options | Default | Required |
|-------|------|---------|---------|----------|
| `naming_series` | Select | VDY-RTN-.YYYY.- | — | Yes |
| `status` | Select | Draft/Generated/Failed | Draft | Read-only |
| `company` | Link | Company | — | Yes |
| `academic_year` | Link | Academic Year | — | Yes |
| `academic_term` | Link | Academic Term | — | No |
| `programs` | Table | Routine Generation Program | — | Yes |

**Section: Schedule Days**

| Field | Type | Default |
|-------|------|---------|
| `monday` | Check | 1 |
| `tuesday` | Check | 1 |
| `wednesday` | Check | 1 |
| `thursday` | Check | 1 |
| `friday` | Check | 1 |
| `saturday` | Check | 0 |
| `sunday` | Check | 0 |
| `periods_per_day` | Int | 5 |

**Section: Constraints**

| Field | Type | Default |
|-------|------|---------|
| `max_subject_per_day` | Int | 2 |
| `max_teacher_periods_per_day` | Int | 4 |
| `min_teacher_weekly_load` | Int | 8 |
| `max_teacher_weekly_load` | Int | 18 |
| `solver_timeout` | Int | 30 |

**Section: Output**

| Field | Type | Options |
|-------|------|---------|
| `routine_slots` | Table | Routine Slot (read-only) |
| `readiness_html` | HTML | — |

**Key Methods:**
- `check_readiness()` — whitelisted, validates data completeness
- `generate_routine()` — whitelisted, runs OR-Tools solver
- `create_course_schedules()` — on_submit, creates Course Schedule entries

**Permissions:** System Administrator, Institute Admin, System Manager (full CRUD + submit)

---

### 5. Routine Slot (Child Table)

> Individual timetable entry produced by the solver.

| Field | Type | Options | Required | Notes |
|-------|------|---------|----------|-------|
| `student_group` | Link | Student Group | Yes | Section |
| `program` | Link | Program | No | Read-only, fetched |
| `day` | Select | Mon-Sun | Yes | Day of week |
| `period` | Int | — | Yes | Period number |
| `instructor` | Link | Instructor | Yes | Assigned teacher |
| `instructor_name` | Data | — | No | Read-only, fetched |
| `course` | Link | Course | Yes | Subject |
| `room` | Link | Room | No | Classroom |

**Parent:** Routine Generation (`routine_slots` field)

---

### 6. Routine Generation Program (Child Table)

> Links programs to a routine generation batch.

| Field | Type | Options | Required |
|-------|------|---------|----------|
| `program` | Link | Program | Yes |

**Parent:** Routine Generation (`programs` field)

---

### 7. Publication (Main DocType - Submittable, Amendable)

> School communications with approval workflow. Naming: `PUB-{YYYY}-{MM}-#####`

**Section: Details**

| Field | Type | Options | Required | Notes |
|-------|------|---------|----------|-------|
| `title` | Data | — | Yes | in_list_view |
| `type` | Select | Notice/News/Announcement | Yes | |
| `publish_date` | Date | — | No | |
| `is_global` | Check | — | No | Future: inter-school visibility |
| `content` | Text Editor | — | Yes | HTML content |

**Section: Targeting (visible when type = Notice)**

| Field | Type | Options | Required |
|-------|------|---------|----------|
| `target_type` | Select | Global/Student Group/Specific Users | Conditional |
| `target_student_group` | Link | Student Group | Conditional |

**Section: Media (visible when type = News)**

| Field | Type | Required |
|-------|------|----------|
| `featured_image` | Attach Image | Conditional |

**Section: Approval**

| Field | Type | Options | Required |
|-------|------|---------|----------|
| `approval_type` | Select | By Role/By User | No |
| `approver_role` | Link | Role | Conditional |
| `approver_user` | Link | User | Conditional |
| `status` | Select | Draft/Pending/Approved/Rejected | Read-only |

**Key Methods:**
- `validate_by_type()` — type-specific field validation
- `validate_approval()` — ensures approval config matches type
- `on_submit()` — auto-assigns to approver(s)

**Permissions:** System Manager (full CRUD + submit)
**Guest Access:** `allow_guest_to_view: true`

---

## Native Doctypes Used (from Education App)

These are NOT created by Vidyaan but are core to its functionality:

| Doctype | Naming Series | Key Fields | Used For |
|---------|--------------|------------|----------|
| Student | EDU-STU-.YYYY.- | first_name, email, DOB, gender, guardians | Student records |
| Instructor | EDU-INS-.YYYY.- | instructor_name, employee (link) | Teacher records |
| Program | (name = program_name) | program_name, courses (child table) | Classes/streams |
| Course | (name = course_name) | course_name, topics, assessment_criteria | Subjects |
| Topic | — | topic_name, content (child table) | Chapters |
| Article | — | title, content, author | Lessons/materials |
| Student Group | Auto | student_group_name, program, students, instructors | Sections |
| Program Enrollment | Auto | student, program, academic_year | Student-class link |
| Course Schedule | EDU-CSH-.YYYY.- | student_group, instructor, course, date, time | Calendar slots |
| Student Attendance | EDU-ATT-.YYYY.- | student, date, status (Present/Absent/Leave) | Daily attendance |
| Assessment Plan | EDU-ASP-.YYYY.- | student_group, course, examiner, date, max_score | Exam scheduling |
| Assessment Result | EDU-RES-.YYYY.- | assessment_plan, student, details, total_score | Marks/grades |
| Assessment Group | Tree | assessment_group_name, parent | Exam vs Assignment |
| Fee Structure | EDU-FST-.YYYY.- | program, components, total_amount | Fee templates |
| Fees | EDU-FEE-.YYYY.- | student, fee_structure, components, grand_total | Fee invoices |
| Room | — | room_name, seating_capacity | Classrooms |
| Grading Scale | — | intervals (child table with grade, threshold) | A+/A/B grading |
| Academic Year | — | year_start_date, year_end_date | Year container |
| Academic Term | — | term_start_date, term_end_date | Semester/term |

---

## Doctype Relationships Diagram

```
Company (Institute)
  │
  ├── Program (Class)
  │     ├── Program Course → Course (Subject)
  │     │                      ├── Course Topic → Topic → Article
  │     │                      └── Course Assessment Criteria (weightage)
  │     ├── Student Group (Section)
  │     │     ├── Student Group Student → Student
  │     │     ├── Student Group Instructor → Instructor
  │     │     ├── Assessment Plan (Exam/Assignment)
  │     │     │     └── Assessment Result (per student)
  │     │     └── Course Schedule (timetable slot)
  │     ├── Program Enrollment → Student
  │     └── Fee Structure → Fees (per student)
  │
  ├── Instructor
  │     └── Instructor Course Mapping (custom child table)
  │           ├── → Course
  │           └── → Program
  │
  ├── Routine Generation
  │     ├── Routine Generation Program → Program
  │     └── Routine Slot (generated)
  │           ├── → Student Group
  │           ├── → Instructor
  │           └── → Course
  │
  ├── Vidyaan Settings
  │     └── Period Timing (child table)
  │
  └── Publication (Notice/News/Announcement)
        └── → Student Group (target)
```
