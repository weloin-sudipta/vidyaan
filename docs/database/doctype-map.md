# Vidyaan - Database Doctype Map

> **Database:** MariaDB/MySQL (via Frappe ORM)
> **Architecture:** Multi-tenant SaaS with Company-based isolation
> **Tables:** 20+ native Education doctypes + 7 custom Vidyaan doctypes

---

## Table of Contents

1. [Database Architecture](#1-database-architecture)
2. [School Concept → Doctype Mapping](#2-school-concept--doctype-mapping)
3. [Custom Doctypes (Vidyaan)](#3-custom-doctypes-vidyaan)
4. [Native Doctypes (Education/ERPNext)](#4-native-doctypes-educationerpnext)
5. [Database Relationships](#5-database-relationships)
6. [Multi-Tenant Isolation](#6-multi-tenant-isolation)
7. [Key Constraints & Indexes](#7-key-constraints--indexes)

---

## 1. Database Architecture

```
MariaDB Database
├── tabCompany (Institutes)
├── tabUser (Authentication)
├── tabEmployee (HR Records)
├── tabStudent (Student Records)
├── tabInstructor (Teacher Records)
├── tabProgram (Classes/Streams)
├── tabCourse (Subjects)
├── tabStudent_Group (Sections)
├── tabCourse_Schedule (Timetable Slots)
├── tabAssessment_Plan (Exams/Assignments)
├── tabAssessment_Result (Grades)
├── tabPublication (Notices/News)
├── tabRoutine_Generation (Timetable Generator)
├── tabVidyaan_Settings (Global Config)
└── ... (20+ additional tables)
```

**Key Design Patterns:**
- All tables prefixed with `tab` (Frappe convention)
- JSON fields for flexible metadata storage
- Automatic audit trails (`creation`, `modified`, `owner`)
- Soft deletes via `docstatus` field (0=Draft, 1=Submitted, 2=Cancelled)

---

## 2. School Concept → Doctype Mapping

| School Concept | Doctype | Table | Purpose |
|---------------|---------|-------|---------|
| Institute / School | `Company` | `tabCompany` | Multi-tenant root entity |
| Administrator | `User` + Role | `tabUser` | Authentication + permissions |
| Teacher | `Instructor` | `tabInstructor` | Teaching staff records |
| Class / Stream | `Program` | `tabProgram` | Academic program (e.g., "Class 10 Science") |
| Subject | `Course` | `tabCourse` | Curriculum subjects |
| Chapter | `Topic` | `tabTopic` | Course content organization |
| Lesson / Material | `Article` | `tabArticle` | Learning content |
| Student | `Student` | `tabStudent` | Student profiles |
| Enrollment | `Program Enrollment` | `tabProgram Enrollment` | Student-program links |
| Section / Division | `Student Group` | `tabStudent_Group` | Class sections (e.g., "10A", "10B") |
| Attendance | `Student Attendance` | `tabStudent_Attendance` | Daily attendance records |
| Class Calendar Slot | `Course Schedule` | `tabCourse_Schedule` | Timetable entries |
| Academic Year | `Academic Year` | `tabAcademic_Year` | Year boundaries |
| Academic Term | `Academic Term` | `tabAcademic_Term` | Semester/term periods |
| Exam / Test | `Assessment Plan` | `tabAssessment_Plan` | Scheduled assessments |
| Marks / Grade | `Assessment Result` | `tabAssessment_Result` | Student scores |
| Exam Category | `Assessment Group` | `tabAssessment_Group` | Tree: Exams vs Assignments |
| Grading Scale | `Grading Scale` | `tabGrading_Scale` | A+, A, B+ scales |
| Fee Template | `Fee Structure` | `tabFee_Structure` | Fee components per program |
| Fee Invoice | `Fees` | `tabFees` | Student fee records |
| Classroom | `Room` | `tabRoom` | Physical spaces |
| Guardian / Parent | `Guardian` | `tabGuardian` | Parent records |
| School House | `School House` | `tabSchool_House` | Inter-house grouping |
| Timetable Config | `Vidyaan Settings` | `tabVidyaan_Settings` | Global settings |
| Period Time Slot | `Period Timing` | `tabPeriod_Timing` | Time slots (child table) |
| Teacher-Subject Map | `Instructor Course Mapping` | `tabInstructor_Course_Mapping` | Teacher capabilities (child table) |
| Timetable Generator | `Routine Generation` | `tabRoutine_Generation` | AI solver orchestration |
| Timetable Entry | `Routine Slot` | `tabRoutine_Slot` | Generated schedule (child table) |
| Programs for Routine | `Routine Generation Program` | `tabRoutine_Generation_Program` | Batch processing (child table) |
| Notice / News | `Publication` | `tabPublication` | Communications with approval |

---

## 3. Custom Doctypes (Vidyaan)

### 3.1 Vidyaan Settings (`tabVidyaan_Settings`)

**Purpose:** Global configuration singleton (one record per site)

**Key Fields:**
- `name` (Primary Key)
- `company` (Link to Company)
- `default_academic_year` (Link)
- `default_periods_per_day` (Int, default: 5)
- `default_days` (Data, default: "Monday,Tuesday,Wednesday,Thursday,Friday")
- `max_subject_per_day` (Int, default: 2)
- `max_teacher_periods_per_day` (Int, default: 4)
- `min_teacher_weekly_load` (Int, default: 8)
- `max_teacher_weekly_load` (Int, default: 18)
- `solver_timeout` (Int, default: 30)

**Relationships:**
- Parent to `tabPeriod_Timing` (child table)

### 3.2 Period Timing (`tabPeriod_Timing`)

**Purpose:** Time slots for school periods

**Key Fields:**
- `name` (Primary Key)
- `parent` (Link to Vidyaan Settings)
- `parentfield` (Always "period_timings")
- `parenttype` (Always "Vidyaan Settings")
- `period_number` (Int)
- `start_time` (Time)
- `end_time` (Time)

### 3.3 Instructor Course Mapping (`tabInstructor_Course_Mapping`)

**Purpose:** Maps teachers to subjects they can teach

**Key Fields:**
- `name` (Primary Key)
- `parent` (Link to Instructor)
- `parentfield` (Always "course_mappings")
- `parenttype` (Always "Instructor")
- `course` (Link to Course)
- `course_name` (Data, read-only)
- `program` (Link to Program)
- `is_preferred` (Check)

### 3.4 Routine Generation (`tabRoutine_Generation`)

**Purpose:** AI-powered timetable generation orchestration

**Key Fields:**
- `name` (VDY-RTN-.YYYY.-)
- `status` (Select: Draft/Generated/Failed)
- `company` (Link to Company) - **CRITICAL for SaaS isolation**
- `academic_year` (Link)
- `academic_term` (Link)
- `monday` to `sunday` (Check fields)
- `periods_per_day` (Int)
- `max_subject_per_day` (Int)
- `max_teacher_periods_per_day` (Int)
- `min_teacher_weekly_load` (Int)
- `max_teacher_weekly_load` (Int)
- `solver_timeout` (Int)
- `readiness_html` (HTML)

**Relationships:**
- Parent to `tabRoutine_Generation_Program` (programs in batch)
- Parent to `tabRoutine_Slot` (generated output)

### 3.5 Routine Slot (`tabRoutine_Slot`)

**Purpose:** Individual generated timetable entries

**Key Fields:**
- `name` (Primary Key)
- `parent` (Link to Routine Generation)
- `parentfield` (Always "routine_slots")
- `parenttype` (Always "Routine Generation")
- `student_group` (Link to Student Group)
- `program` (Link to Program, read-only)
- `day` (Select: Mon-Sun)
- `period` (Int)
- `instructor` (Link to Instructor)
- `instructor_name` (Data, read-only)
- `course` (Link to Course)
- `room` (Link to Room, optional)

### 3.6 Routine Generation Program (`tabRoutine_Generation_Program`)

**Purpose:** Links programs to generation batches

**Key Fields:**
- `name` (Primary Key)
- `parent` (Link to Routine Generation)
- `parentfield` (Always "programs")
- `parenttype` (Always "Routine Generation")
- `program` (Link to Program)

### 3.7 Publication (`tabPublication`)

**Purpose:** School communications with approval workflow

**Key Fields:**
- `name` (PUB-{YYYY}-{MM}-#####)
- `title` (Data)
- `type` (Select: Notice/News/Announcement)
- `publish_date` (Date)
- `is_global` (Check)
- `content` (Text Editor)
- `target_type` (Select: Global/Student Group/Specific Users)
- `target_student_group` (Link to Student Group)
- `featured_image` (Attach Image)
- `approval_type` (Select: By Role/By User)
- `approver_role` (Link to Role)
- `approver_user` (Link to User)
- `status` (Select: Draft/Pending/Approved/Rejected)

---

## 4. Native Doctypes (Education/ERPNext)

### Core Academic Tables

| Table | Key Fields | Relationships |
|-------|------------|---------------|
| `tabStudent` | `first_name`, `email`, `date_of_birth`, `gender` | → `tabGuardian`, → `tabStudent_Group` |
| `tabInstructor` | `instructor_name`, `employee` | → `tabEmployee`, → `tabUser` |
| `tabProgram` | `program_name` | → `tabProgram_Course` (child) |
| `tabCourse` | `course_name` | → `tabTopic`, → `tabCourse_Assessment_Criteria` |
| `tabTopic` | `topic_name` | → `tabArticle` |
| `tabArticle` | `title`, `content` | → `tabTopic` |
| `tabStudent_Group` | `student_group_name`, `program` | → `tabStudent_Group_Student`, → `tabStudent_Group_Instructor` |
| `tabProgram_Enrollment` | `student`, `program`, `academic_year` | → `tabStudent`, → `tabProgram` |
| `tabCourse_Schedule` | `student_group`, `instructor`, `course`, `date`, `from_time`, `to_time` | → `tabStudent_Group`, → `tabInstructor`, → `tabCourse` |
| `tabStudent_Attendance` | `student`, `date`, `status` | → `tabStudent` |

### Assessment Tables

| Table | Key Fields | Relationships |
|-------|------------|---------------|
| `tabAssessment_Plan` | `student_group`, `course`, `examiner`, `date`, `max_score` | → `tabStudent_Group`, → `tabCourse`, → `tabInstructor` |
| `tabAssessment_Result` | `assessment_plan`, `student`, `total_score` | → `tabAssessment_Plan`, → `tabStudent` |
| `tabAssessment_Group` | `assessment_group_name`, `parent_assessment_group` | Tree structure |

### Administrative Tables

| Table | Key Fields | Relationships |
|-------|------------|---------------|
| `tabFee_Structure` | `program`, `total_amount` | → `tabProgram`, → `tabFee_Structure_Component` |
| `tabFees` | `student`, `fee_structure`, `grand_total` | → `tabStudent`, → `tabFee_Structure` |
| `tabRoom` | `room_name`, `seating_capacity` | Used by `tabCourse_Schedule` |
| `tabGrading_Scale` | — | → `tabGrading_Scale_Interval` |
| `tabAcademic_Year` | `year_start_date`, `year_end_date` | Container for terms |
| `tabAcademic_Term` | `term_start_date`, `term_end_date` | Container for schedules |

---

## 5. Database Relationships

### Entity Relationship Diagram

```
Company (Institute)
├── User (Admin) → Role Permissions
├── Employee → Instructor
├── Program (Class)
│   ├── Program Course → Course (Subject)
│   │   ├── Topic → Article (Content)
│   │   └── Course Assessment Criteria
│   ├── Student Group (Section)
│   │   ├── Student Group Student → Student → Guardian
│   │   ├── Student Group Instructor → Instructor
│   │   ├── Assessment Plan → Assessment Result
│   │   └── Course Schedule
│   ├── Program Enrollment → Student
│   └── Fee Structure → Fees
├── Instructor Course Mapping (custom child)
├── Routine Generation
│   ├── Routine Generation Program → Program
│   └── Routine Slot → Student Group, Instructor, Course
├── Vidyaan Settings → Period Timing
└── Publication
```

### Foreign Key Patterns

**Company Isolation (SaaS):**
- All major entities link to `Company` for multi-tenant filtering
- User Permissions enforce: `User → Company` access control
- API queries automatically filter by user's default Company

**Academic Hierarchy:**
- `Program` → `Student Group` → `Course Schedule`
- `Course` → `Topic` → `Article`
- `Assessment Plan` → `Assessment Result`

**Teacher-Student Links:**
- `Instructor` → `Student Group` (via Student Group Instructor)
- `Student` → `Student Group` (via Student Group Student)
- `Instructor` → `Course` (via Instructor Course Mapping)

---

## 6. Multi-Tenant Isolation

### Company Field Injection

**10 doctypes receive automatic `company` field:**
- `Student`, `Instructor`, `Program`, `Course`, `Topic`, `Article`
- `Program Enrollment`, `Course Schedule`, `Student Group`, `Student Attendance`

**Implementation:**
```python
# vidyaan/setup/custom_fields.py
{
    "fieldname": "company",
    "label": "Institute / Company",
    "fieldtype": "Link",
    "options": "Company",
    "reqd": 1,
    "in_list_view": 1,
    "in_standard_filter": 1,
    "default": "frappe.defaults.get_user_default('Company')"
}
```

### Data Access Control

**User Permission Layer:**
- Institute Admin gets `User Permission` record: `User → Company`
- Frappe ORM automatically filters all queries by permitted Companies

**Application Layer:**
- All whitelisted APIs include `{"company": frappe.session.user_company}` filters
- Routine Generation validates ownership before processing

**Database Layer:**
- No cross-company data leakage possible
- Audit trails track all data modifications

---

## 7. Key Constraints & Indexes

### Unique Constraints

| Table | Fields | Purpose |
|-------|--------|---------|
| `tabStudent` | `email` | Prevent duplicate student emails |
| `tabInstructor` | `employee` | One employee = one instructor |
| `tabProgram_Enrollment` | `student`, `program`, `academic_year` | Student enrolls once per program per year |
| `tabStudent_Attendance` | `student`, `date` | One attendance record per student per day |
| `tabCourse_Schedule` | `student_group`, `date`, `from_time` | No double-booking of rooms/times |
| `tabAssessment_Result` | `assessment_plan`, `student` | One grade per student per assessment |

### Performance Indexes

**High-Traffic Queries:**
- `tabStudent_Attendance`: (`student`, `date`)
- `tabCourse_Schedule`: (`student_group`, `date`)
- `tabAssessment_Result`: (`assessment_plan`, `student`)

**Company-Filtered Queries:**
- All tables with `company` field: (`company`, `creation`) for list views
- `tabStudent_Group`: (`company`, `program`) for section filtering

### Data Integrity

**Referential Integrity:**
- All Link fields enforce foreign key relationships
- Cascade delete protection prevents orphaned records
- Soft deletes (docstatus) maintain audit trails

**Business Rules:**
- Assessment Results require valid Assessment Plan
- Course Schedules require valid Student Group + Instructor + Course
- Routine Slots validate teacher availability and room capacity

---

*Last updated: 2026-04-01*