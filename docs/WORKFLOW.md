# Vidyaan School ERP — Complete Workflow

> This document defines the end-to-end workflow of the Vidyaan School ERP system,
> covering every role, every action, and every automation chain.
> Use this as the single source of truth for what the system does and how it flows.

---

## Table of Contents

1. [Roles & Responsibilities](#1-roles--responsibilities)
2. [Phase 1: System Onboarding](#2-phase-1-system-onboarding)
3. [Phase 2: Institute Setup](#3-phase-2-institute-setup)
4. [Phase 3: Academic Configuration](#4-phase-3-academic-configuration)
5. [Phase 4: Student Management](#5-phase-4-student-management)
6. [Phase 5: Timetable / Routine Generation](#6-phase-5-timetable--routine-generation)
7. [Phase 6: Day-to-Day Operations](#7-phase-6-day-to-day-operations)
8. [Phase 7: Examinations & Grading](#8-phase-7-examinations--grading)
9. [Phase 8: Assignments](#9-phase-8-assignments)
10. [Phase 9: Fee Management & Payments](#10-phase-9-fee-management--payments)
11. [Phase 10: Publications & Communication](#11-phase-10-publications--communication)
12. [Phase 11: Reports & Analytics](#12-phase-11-reports--analytics)
13. [Automation Summary](#13-automation-summary)
14. [Implementation Status](#14-implementation-status)

---

## 1. Roles & Responsibilities

### System-Level Roles

| Role | Who | Scope | Primary Actions |
|------|-----|-------|-----------------|
| **System Administrator** | Vidyaan platform owner | All institutes | Create institutes, manage the SaaS platform, monitor all data |
| **System Manager** | Frappe system admin | All institutes | Technical config, doctypes, reports, integrations |

### Institute-Level Roles

| Role | Who | Scope | Primary Actions |
|------|-----|-------|-----------------|
| **Institute Admin** | School principal / director | Own institute only | Full control: manage staff, students, academics, exams, fees, routines |
| **Instructor** | Teacher / Faculty | Own institute, own classes | Mark attendance, create assignments, grade exams, upload study materials |
| **Accountant** | Fee/finance officer | Own institute, fee records | Verify payments, manage fee structures, generate receipts |
| **Librarian** | Library manager | Own institute, library records | Manage book catalog, issue/return books, track requests |
| **Student** | Enrolled student | Own records only | View timetable, attendance, grades, submit assignments, request books (via frontend portal) |

### Role Scoping Rule

> All institute-level roles are scoped to a single Company (institute) via User Permission.
> An Instructor at School A cannot see data from School B.
> Institute Admin can create custom roles within their institute for specialized staff
> (e.g., Lab Assistant, Sports Coordinator), but these roles apply only to their institute.

---

## 2. Phase 1: System Onboarding

```
System Administrator logs in for the first time
    │
    ▼
┌─────────────────────────────────────┐
│  Setup Wizard (mandatory, modal)    │
│                                     │
│  1. Enter Institute Name            │
│  2. Enter Admin Email               │
│  3. Enter Admin First Name          │
│  4. Set Admin Password              │
│                                     │
│  [Complete Setup]                   │
└──────────────┬──────────────────────┘
               │
               ▼
         System auto-creates:
           ├── Company (institute) with abbreviation
           ├── User (admin) with roles: System Manager + Institute Admin
           ├── User Permission → Company (data isolation)
           └── Sets vidyaan_setup_complete = 1

         Redirects to → /app/vidyaan-dashboard
```

**Implementation:** DONE (`setup/wizard.py`, `public/js/vidyaan_setup.js`)

---

## 3. Phase 2: Institute Setup

Once the Institute Admin logs in, they set up the foundation.

### 2.1 Staff Management

```
Institute Admin
    │
    ├── Create Employee records (HR module)
    │     ├── Name, Email, Department, Designation
    │     ├── Link to Company (auto-filled)
    │     └── Create User account (optional, for desk login)
    │
    ├── Create Instructor records (Education module)
    │     ├── Link to Employee (mandatory)
    │     ├── Company field (auto-filled)
    │     └── Fill "Courses I Teach" mapping table:
    │           ├── Course (subject) + Program (class) + Preferred (checkbox)
    │           └── This tells the solver which teacher can teach what
    │
    └── Create Accountant / Other Staff
          ├── Create User with appropriate roles
          └── Assign User Permission for Company isolation
```

### 2.2 Institute-Specific Roles (Custom)

```
Institute Admin
    │
    └── Create Custom Roles (for their institute only)
          ├── Examples: "Lab Assistant", "Sports Coordinator", "HOD"
          ├── These roles get permissions only within this institute
          ├── Assigned to Users who belong to this Company
          └── User Permission on Company ensures data isolation
```

**Implementation:**
- Employee + Instructor creation: DONE (native doctypes + custom company field)
- Instructor Course Mapping: DONE (custom child table)
- Custom role creation per institute: NOT IMPLEMENTED (need UI + scoping logic)

---

## 4. Phase 3: Academic Configuration

### 3.1 Programs (Classes / Streams)

```
Institute Admin
    │
    ├── Create Academic Year (e.g., "2026-2027")
    ├── Create Academic Term (e.g., "First Term", "Second Term")
    │
    └── Create Programs (classes):
          ├── "Class 5" (no streams for lower classes)
          ├── "Class 11 - Science" (stream-based for higher classes)
          ├── "Class 11 - Arts"
          └── Each Program gets:
                ├── Company (auto-filled)
                └── Courses linked via Program Course child table
```

### 3.2 Courses (Subjects)

```
Institute Admin (or Instructor)
    │
    └── Create Courses:
          ├── "Mathematics", "Physics", "English", "History"
          ├── Company field (auto-filled)
          ├── Assessment Criteria (weightage):
          │     ├── "Assignments" → 20%
          │     ├── "Mid-Term" → 30%
          │     └── "Final Exam" → 50%
          └── Link courses to Programs via Program Course table
```

### 3.3 Topics & Study Materials

```
Institute Admin or Instructor
    │
    ├── Create Topics (chapters) under a Course:
    │     ├── "Thermodynamics" under Physics
    │     ├── "Algebra" under Mathematics
    │     └── Company field (auto-filled)
    │
    └── Create Articles (lessons / study materials) under Topics:
          ├── Title, HTML content, author
          ├── Attach files (PDFs, notes, videos)
          └── Company field (auto-filled)

    ┌──────────────────────────────────┐
    │  AUTOMATION: When an Article is  │
    │  published, students enrolled in │
    │  that Course's Program can see   │
    │  it via the frontend portal.     │
    └──────────────────────────────────┘
```

### 3.4 Rooms & Infrastructure

```
Institute Admin
    │
    └── Create Rooms:
          ├── Room Name, Seating Capacity
          └── Used in: Assessment Plans (exam room), Routine Generation (optional)
```

### 3.5 Grading Scales

```
Institute Admin
    │
    └── Create Grading Scale:
          ├── A+ (90-100), A (80-89), B+ (70-79), B (60-69), etc.
          └── Used in: Assessment Results for grade calculation
```

**Implementation:**
- Programs, Courses, Topics, Articles: DONE (native Education doctypes + company field)
- Assessment Criteria on Courses: DONE (native)
- Rooms, Academic Year/Term, Grading Scale: DONE (native)

---

## 5. Phase 4: Student Management

### 4.1 Student Registration

```
Institute Admin
    │
    └── Create Student record:
          ├── Name, DOB, Gender, Email, Photo
          ├── Guardian / Parent details
          ├── Company (auto-filled)
          └── Optionally create User account (for portal login)
```

### 4.2 Student Groups (Sections)

```
Institute Admin
    │
    └── Create Student Groups (sections):
          ├── "Class 11 Science - Section A"
          ├── "Class 11 Science - Section B"
          ├── Link to Program
          ├── Assign Instructors to the group
          └── Company (auto-filled)
```

### 4.3 Enrollment

```
Institute Admin
    │
    └── Create Program Enrollment:
          ├── Select Student
          ├── Select Program (e.g., "Class 11 - Science")
          ├── Select Academic Year
          └── Company (auto-filled)

    ┌───────────────────────────────────────┐
    │  AUTOMATION NEEDED:                   │
    │  On enrollment →                      │
    │    1. Auto-add student to the         │
    │       relevant Student Group          │
    │    2. Auto-create Course Enrollments  │
    │       for each course in the Program  │
    │    3. Notify instructor(s)            │
    └───────────────────────────────────────┘
```

**Implementation:**
- Student creation: DONE
- Student Groups: DONE
- Program Enrollment: DONE (native)
- Enrollment automation (auto-add to group): NOT IMPLEMENTED

---

## 6. Phase 5: Timetable / Routine Generation

```
Institute Admin
    │
    ├── Configure Vidyaan Settings:
    │     ├── Default periods per day (5)
    │     ├── Period timings (09:00-09:45, 09:45-10:30, ...)
    │     ├── Solver constraints (max subject/day, teacher load, etc.)
    │     └── Active school days (Mon-Fri)
    │
    └── Create Routine Generation document:
          │
          ├── Select Programs to generate for
          ├── Configure constraints (or use defaults)
          │
          ├── [Check Readiness] button:
          │     ├── Validates: programs belong to institute
          │     ├── Validates: every program has courses
          │     ├── Validates: every program has Student Groups (sections)
          │     ├── Validates: instructor-course mappings exist
          │     └── Validates: enough teachers for total slots
          │
          ├── [Generate Routine] button:
          │     ├── OR-Tools CP-SAT solver runs
          │     ├── Hard constraints enforced (no teacher conflicts, etc.)
          │     ├── Soft constraints optimized (teacher preferences)
          │     └── Routine Slots populated in child table
          │
          └── [Submit]:
                │
                ▼
          ┌──────────────────────────────────────┐
          │  AUTOMATION (exists):                │
          │  On Submit →                         │
          │    1. Creates Course Schedule         │
          │       entries for each routine slot   │
          │    2. Maps period numbers to actual   │
          │       times from Vidyaan Settings     │
          │    3. Students can see their          │
          │       timetable in the frontend       │
          └──────────────────────────────────────┘
```

**Implementation:** DONE (complete with OR-Tools solver)

---

## 7. Phase 6: Day-to-Day Operations

### 6.1 Attendance

```
Instructor (daily)
    │
    ├── Open Student Attendance Tool (or frontend attendance page)
    ├── Select Student Group (their section)
    ├── Select Date (defaults to today)
    │
    └── For each student:
          ├── Mark: Present / Absent / Leave
          └── Save creates Student Attendance records

    ┌───────────────────────────────────────┐
    │  AUTOMATION NEEDED:                   │
    │  On attendance marked →               │
    │    1. If student marked Absent,       │
    │       notify parent/guardian           │
    │    2. Update attendance summary cache  │
    │    3. Flag students below threshold    │
    └───────────────────────────────────────┘
```

### 6.2 Study Material Distribution

```
Instructor or Institute Admin
    │
    ├── Create/Edit Articles under Topics
    │     ├── Write lesson content (HTML editor)
    │     ├── Attach PDF notes, presentations, videos
    │     └── Company-scoped (only their institute's students see it)
    │
    └── Students access via:
          ├── Frontend portal → Academics → Study Materials
          └── Filter by Course / Topic
```

**Implementation:**
- Attendance: DONE (native doctype + instructor permissions)
- Attendance automation (notifications): NOT IMPLEMENTED
- Study materials: DONE (native Article doctype)

---

## 8. Phase 7: Examinations & Grading

### 7.1 Exam Scheduling

```
Institute Admin
    │
    └── Create Assessment Plan:
          ├── Select Student Group (section)
          ├── Select Assessment Group: "Exams" → "Final Exam" / "Mid-Term"
          ├── Select Course (subject)
          ├── Set Schedule Date, From Time, To Time
          ├── Set Room (exam hall)
          ├── Assign Examiner (instructor who grades)
          ├── Assign Supervisor (instructor who monitors)
          ├── Set Maximum Score
          │
          └── [Submit]:
                │
                ▼
          ┌──────────────────────────────────────┐
          │  AUTOMATION (exists):                │
          │  On Submit →                         │
          │    1. Auto-creates Publication        │
          │       (Notice) targeting the          │
          │       Student Group                   │
          │    2. Approver set to Institute Admin │
          │    3. Students auto-assigned          │
          │       (via Student Group membership)  │
          └──────────────────────────────────────┘
```

### 7.2 Admit Cards

```
Student (or Admin prints for them)
    │
    └── Open Student record → Print → Select "Admit Card"
          ├── Auto-fetches all upcoming Assessment Plans
          ├── Displays: Course, Date, Time, Room
          └── ID-card style layout
```

### 7.3 Grading

```
Instructor (Examiner)
    │
    ├── Open Assessment Result Tool
    ├── Select the Assessment Plan
    ├── System auto-loads all students in the Student Group
    │
    └── Enter marks for each student → Submit
          │
          ▼
    ┌──────────────────────────────────────┐
    │  SECURITY (exists):                  │
    │  Before Save / Submit →              │
    │    1. Validates logged-in user is    │
    │       the Examiner or Supervisor     │
    │    2. System Manager / Institute     │
    │       Admin can override             │
    │    3. Clear error if user chain      │
    │       (User→Employee→Instructor)     │
    │       is broken                      │
    └──────────────────────────────────────┘
```

### 7.4 Report Cards

```
Institute Admin (at term end)
    │
    └── Use Student Report Generation Tool:
          ├── Select Academic Year + Academic Term
          ├── Select Program / Student Group
          ├── System auto-calculates weighted scores:
          │     ├── Assignments × 20% (from Assessment Criteria)
          │     ├── Mid-Term × 30%
          │     └── Final Exam × 50%
          └── Generates report card per student
```

**Implementation:**
- Assessment Plan creation + auto-publication: DONE
- Admit Cards: DONE
- Grading with security hook: DONE
- Report card generation: DONE (native tool)

---

## 9. Phase 8: Assignments

### 8.1 Assignment Creation

```
Institute Admin or Instructor
    │
    └── Create Assessment Plan:
          ├── Select Student Group
          ├── Select Assessment Group: "Assignments" → "Homework" / "Project"
          ├── Select Course
          ├── Assign Examiner (instructor who grades)
          ├── Set Schedule Date (acts as DEADLINE)
          ├── Set Maximum Score
          │
          └── [Submit] → triggers same auto-publication as exams
```

### 8.2 Student Submission (Frontend Portal)

```
Student (via frontend)
    │
    ├── View assignments in Academics → Assignments
    ├── See deadline, course, instructions
    │
    └── Upload submission (file attachment)
          │
          ▼
    ┌───────────────────────────────────────┐
    │  AUTOMATION NEEDED:                   │
    │  On submission →                      │
    │    1. Notify the Examiner             │
    │    2. Record submission timestamp     │
    │    3. Flag late submissions           │
    │       (past schedule_date)            │
    └───────────────────────────────────────┘
```

### 8.3 Assignment Grading

```
Instructor (Examiner)
    │
    ├── Open Assessment Result Tool
    ├── Select the Assignment Assessment Plan
    ├── Review student submissions (attachments)
    └── Enter marks → Submit (same flow as exam grading)
```

**Implementation:**
- Assignment creation (via Assessment Plan + "Assignments" group): DONE
- Student submission from frontend: PARTIAL (frontend UI exists, backend file upload via Frappe)
- Assignment grading: DONE (same as exam grading)
- Submission notification: NOT IMPLEMENTED

---

## 10. Phase 9: Fee Management & Payments

### 9.1 Fee Structure Setup

```
Institute Admin
    │
    └── Create Fee Structure:
          ├── Select Program (e.g., "Class 11 - Science")
          ├── Add Fee Components:
          │     ├── Tuition Fee: 50,000
          │     ├── Lab Fee: 5,000
          │     ├── Library Fee: 2,000
          │     └── Transport Fee: 10,000
          ├── Total Amount: 67,000
          └── Company (auto-filled)
```

### 9.2 Fee Generation

```
Institute Admin
    │
    └── Generate Fees for students:
          ├── Select Fee Structure
          ├── Select Academic Year / Term
          ├── System creates individual Fee records per student
          │     ├── Links to: Student, Fee Structure, Program
          │     ├── Status: Unpaid
          │     └── Due Date
          │
          └── Students see fee status in frontend portal
```

### 9.3 Payment Verification

```
Parent/Student makes payment (offline or payment gateway)
    │
    ▼
Accountant
    │
    ├── Open Fee record for the student
    ├── Record payment details:
    │     ├── Payment method (Cash / Bank Transfer / Online)
    │     ├── Transaction reference
    │     ├── Amount paid
    │     └── Payment date
    │
    └── [Submit] → marks Fee as Paid
          │
          ▼
    ┌───────────────────────────────────────┐
    │  AUTOMATION NEEDED:                   │
    │  On payment verified →                │
    │    1. Generate payment receipt (PDF)   │
    │    2. Notify student/parent            │
    │    3. Update student fee dashboard     │
    │    4. Flag overdue fees               │
    └───────────────────────────────────────┘
```

**Implementation:**
- Fee Structure, Fees doctypes: AVAILABLE (native Education + company field)
- Accountant role: NOT IMPLEMENTED (role + permissions needed)
- Payment verification flow: NOT IMPLEMENTED (no automation/hooks)
- Receipt generation: NOT IMPLEMENTED
- Fee portal view: PARTIAL (frontend page exists, backend API missing)

---

## 11. Phase 10: Publications & Communication

### 10.1 Notices

```
Institute Admin or Instructor
    │
    └── Create Publication (type: Notice):
          ├── Title, Content (rich text)
          ├── Target: Global / Student Group / Specific Users
          ├── Select Approver (role or user)
          │
          └── [Submit]:
                │
                ▼
          ┌──────────────────────────────────────┐
          │  AUTOMATION (exists):                │
          │  On Submit →                         │
          │    1. Auto-assigns to approver(s)    │
          │    2. Status changes to "Pending"    │
          │                                      │
          │  On Approve →                        │
          │    1. Status changes to "Approved"   │
          │    2. Visible to target audience     │
          │       in frontend portal             │
          └──────────────────────────────────────┘
```

### 10.2 News

```
Institute Admin
    │
    └── Create Publication (type: News):
          ├── Title, Content, Featured Image
          ├── Publish Date
          └── Same approval workflow as Notices
```

### 10.3 Announcements

```
Institute Admin or Instructor
    │
    └── Create Publication (type: Announcement):
          ├── Title, Content (quick updates)
          └── Same approval workflow
```

### 10.4 Auto-Generated Notices

```
Assessment Plan submitted
    │
    ▼
System auto-creates Publication (Notice):
    ├── Title: "Assessment: {plan_name}"
    ├── Content: Course, Date, details
    ├── Target: Student Group from the plan
    ├── Approver: Institute Admin role
    └── Status: Draft (needs approval to be visible)
```

**Implementation:**
- Publication with 3 types: DONE
- Auto-assign on submit: DONE
- Approve/Reject buttons: DONE (client-side JS)
- Auto-publication from Assessment Plan: DONE
- Notification to students: NOT IMPLEMENTED

---

## 12. Phase 11: Reports & Analytics

### Expected Reports

| Report | Data Source | For Whom |
|--------|-----------|----------|
| Attendance Summary | Student Attendance | Admin, Instructor, Student |
| Student Report Card | Assessment Results + Criteria | Admin, Student |
| Fee Collection Report | Fees (paid/unpaid) | Admin, Accountant |
| Program-wise Enrollment | Program Enrollment | Admin |
| Instructor Workload | Course Schedule | Admin |
| Exam Performance Analysis | Assessment Results | Admin, Instructor |
| Library Usage | (future) | Admin, Librarian |

**Implementation:** NOT IMPLEMENTED (no custom reports — native Frappe Report Builder available)

---

## 13. Automation Summary

### Currently Working Automations

| Trigger | Auto-Action | File |
|---------|------------|------|
| Routine Generation submitted | Creates Course Schedule entries | `routine_generation.py` |
| Assessment Plan submitted | Creates Publication (Notice) | `utils.py` |
| Assessment Result saved/submitted | Validates examiner permission | `events.py` |
| Publication submitted | Auto-assigns to approvers | `publication.py` |
| Setup wizard completed | Creates Company + Admin User | `wizard.py` |

### Automations Needed (Not Yet Built)

| Trigger | Auto-Action | Priority |
|---------|------------|----------|
| Program Enrollment created | Auto-add student to Student Group | HIGH |
| Program Enrollment created | Auto-create Course Enrollments | HIGH |
| Student marked Absent | Notify parent/guardian | MEDIUM |
| Fee payment submitted | Generate receipt, notify student | MEDIUM |
| Assignment deadline passed | Flag late/missing submissions | LOW |
| Student submission uploaded | Notify examiner | LOW |
| Attendance below threshold | Alert Institute Admin | LOW |
| Overdue fees | Auto-reminder to parent | LOW |

---

## 14. Implementation Status

### Fully Implemented

| Feature | Backend | Frontend | Automation |
|---------|---------|----------|-----------|
| Setup Wizard | DONE | DONE | DONE |
| Multi-Tenant Isolation | DONE | N/A | DONE |
| Programs / Courses / Topics | DONE | DONE | N/A |
| Instructor Course Mapping | DONE | N/A | N/A |
| Student Registration | DONE | DONE | N/A |
| Student Groups | DONE | N/A | N/A |
| Program Enrollment | DONE | N/A | Manual only |
| Routine Generation (AI) | DONE | DONE (desk) | DONE (auto Course Schedule) |
| Period Timings Config | DONE | N/A | N/A |
| Assessment Plan (Exams) | DONE | DONE | DONE (auto Publication) |
| Assessment Plan (Assignments) | DONE | DONE | DONE (auto Publication) |
| Grading (Assessment Result) | DONE | DONE | DONE (security hook) |
| Weighted Report Cards | DONE | N/A | DONE (native tool) |
| Admit Cards | DONE | N/A | DONE (Jinja print) |
| Publication System | DONE | DONE | DONE (auto-assign) |
| Study Materials (Articles) | DONE | DONE | N/A |
| Attendance Marking | DONE | DONE | Manual only |
| Roles & Permissions | DONE | N/A | DONE |

### Partially Implemented

| Feature | What Exists | What's Missing |
|---------|-------------|----------------|
| Student Assignment Submission | Frontend UI + file upload | Backend tracking, notifications, late flagging |
| Fee Management | Native doctypes + permissions | Accountant role, payment workflow, receipts, notifications |
| Library Management | Frontend UI (full) | Backend APIs (some exist in maxedu namespace) |
| Notifications | Frappe built-in assignments | Custom notifications for attendance, fees, grades |

### Not Yet Implemented

| Feature | Description | Priority |
|---------|-------------|----------|
| Enrollment Automation | Auto-add to Student Group + Course Enrollment on enroll | HIGH |
| Accountant Role + Fee Workflow | New role, payment verification, receipt generation | HIGH |
| Custom Roles per Institute | UI for Institute Admin to create institute-scoped roles | MEDIUM |
| Attendance Notifications | Alert parent on absent, flag below threshold | MEDIUM |
| Routine Generation Frontend | Rich UI in portal (currently only in Desk) | MEDIUM |
| SMS/Email Notifications | Automated alerts for events, fees, grades | LOW |
| Parent Portal | Separate login for guardians | LOW |
| Custom Reports | Attendance summary, fee collection, performance | LOW |

---

## Complete Flow Diagram

```
                    ┌──────────────────┐
                    │ SYSTEM ADMIN     │
                    │ (Platform Owner) │
                    └────────┬─────────┘
                             │
                    Setup Wizard (first login)
                             │
                    Creates Institute + Admin
                             │
                             ▼
                    ┌──────────────────┐
                    │ INSTITUTE ADMIN  │
                    │ (School Head)    │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
      ┌──────────┐    ┌──────────┐    ┌──────────┐
      │  STAFF   │    │ ACADEMIC │    │ STUDENTS │
      │  SETUP   │    │  SETUP   │    │  SETUP   │
      └────┬─────┘    └────┬─────┘    └────┬─────┘
           │               │               │
   Create Employee    Create Programs   Create Students
   Create Instructor  Create Courses    Create Groups
   Create Accountant  Create Topics     Enroll Students
   Assign Roles       Set Grading       Assign Sections
           │               │               │
           └───────┬───────┘               │
                   │                       │
                   ▼                       │
           ┌──────────────┐                │
           │   ROUTINE    │                │
           │  GENERATION  │◄───────────────┘
           │  (AI Solver) │
           └──────┬───────┘
                  │
           Auto-creates Course Schedule
                  │
                  ▼
     ┌────────────────────────────┐
     │    DAY-TO-DAY OPERATIONS   │
     ├────────────────────────────┤
     │                            │
     │  ┌─────────┐ ┌──────────┐ │
     │  │ATTENDANCE│ │  STUDY   │ │
     │  │ Marking  │ │MATERIALS │ │
     │  │(Instruc.)│ │(Instruc.)│ │
     │  └─────────┘ └──────────┘ │
     │                            │
     │  ┌──────────────────────┐  │
     │  │  EXAMS & ASSIGNMENTS │  │
     │  ├──────────────────────┤  │
     │  │ Admin creates plan   │  │
     │  │ → Auto-notice sent   │  │
     │  │ → Students take exam │  │
     │  │ → Instructor grades  │  │
     │  │ → Report cards gen   │  │
     │  └──────────────────────┘  │
     │                            │
     │  ┌──────────────────────┐  │
     │  │   FEE MANAGEMENT     │  │
     │  ├──────────────────────┤  │
     │  │ Admin sets structure │  │
     │  │ → Fees generated     │  │
     │  │ → Student pays       │  │
     │  │ → Accountant verifies│  │
     │  │ → Receipt generated  │  │
     │  └──────────────────────┘  │
     │                            │
     │  ┌──────────────────────┐  │
     │  │  PUBLICATIONS        │  │
     │  ├──────────────────────┤  │
     │  │ Notices / News /     │  │
     │  │ Announcements        │  │
     │  │ → Approval workflow  │  │
     │  │ → Visible in portal  │  │
     │  └──────────────────────┘  │
     └────────────────────────────┘
```

---

*Last updated: 2026-04-01*
*This document should be updated as features are implemented or workflows change.*
