# Vidyaan Complete Architecture & Workflow Specification

This document details the Multi-Tenant architecture, Core Educational feature mappings, Routine Generation engine, and all workflows implemented within the Vidyaan application.

---

## 🏗️ 1. True Multi-Tenant SaaS Architecture

### 1.1 The Isolation Mechanism
- **Custom Field Injection**: During installation, `custom_fields.py` injects a mandatory `company` link into 10 core Education doctypes (`Student`, `Instructor`, `Program`, `Course`, `Topic`, `Article`, `Student Group`, `Student Attendance`, `Program Enrollment`, `Course Schedule`).
- **User Permissions**: When an Institute Admin logs in, Frappe User Permissions lock queries to their designated Company. They cannot read, filter, or API-query records from another school.
- **Triple-Layer Protection in Routine Generation**: (1) Form-level UI filtering, (2) Readiness validation ownership checks, (3) Explicit `company` filters on every backend query.

---

## 📚 2. Structural Doctype Map

| Feature | Native Doctype | Purpose |
|---|---|---|
| Institute | `Company` | Top-level SaaS isolation node |
| Administrator | `User` + Role `Institute Admin` | Super-manager of a school |
| Teaching Staff | `User` → `Employee` → `Instructor` | Teacher profiles with course mapping |
| Other Staff | `User` → `Employee` | Clerks, accountants, etc. |
| Classes / Streams | `Program` | e.g., "Class 11 Science", "Class 5" |
| Subjects | `Course` | e.g., "Physics", "English" |
| Chapters | `Topic` | Module clusters within a Course |
| Lessons | `Article` | Text/HTML instructional content |
| Study Materials | Native `File` attachments | PDFs, videos on Articles/Topics |
| Student Records | `Student` | Student profiles |
| Enrollment | `Program Enrollment` | Links Student → Program |
| Sections | `Student Group` | e.g., "Class 11 Sci - Section A" |
| Attendance | `Student Attendance` | Per-student per-day tracking |
| Calendar Slots | `Course Schedule` | Individual class schedule entries |

### Vidyaan-Specific Doctypes

| Doctype | Type | Purpose |
|---|---|---|
| `Vidyaan Settings` | Single | Global config: period timings, routine defaults |
| `Period Timing` | Child Table | Period number → start/end time mapping |
| `Instructor Course Mapping` | Child Table | Teacher → Course → Program capability mapping |
| `Routine Generation` | Parent (Submittable) | Main routine generation control panel |
| `Routine Generation Program` | Child Table | MultiSelect of Programs for generation |
| `Routine Slot` | Child Table | Generated output: section + day + period + teacher + course |

---

## ⚙️ 3. Routine Generation Engine

### 3.1 How It Works

The engine uses **Google OR-Tools CP-SAT Solver** to produce conflict-free timetables.

```
Institute Admin Flow:
1. Create Programs (Classes) → Link Courses to them
2. Create Courses (Subjects) 
3. Create Instructors → Fill "Courses I Teach" mapping table
4. Create Student Groups (Sections) for each Program
5. Open Routine Generation → Select Programs → Click Generate
6. Review generated routine → Submit to publish
7. Course Schedule entries auto-created for calendar view
```

### 3.2 Solver Constraints

| Constraint | Type | Default |
|---|---|---|
| Teacher can't teach 2 sections simultaneously | Hard | Always enforced |
| Max same subject per day per section | Hard | 2 |
| Max teacher periods per day | Hard | 4 |
| Teacher weekly load (min/max) | Hard | 8-18 |
| Teacher class preference | Soft (Objective) | Via `is_preferred` checkbox |

### 3.3 Section Handling

The solver operates at **Student Group** (section) level, NOT Program level:
- Admin selects Programs → System discovers all Student Groups under them
- Each section gets its own independent routine
- Teacher conflict constraint prevents double-booking

### 3.4 Readiness Validation

Before generation, a live check verifies:
1. **Ownership**: All programs belong to the admin's Institute
2. **Courses**: Every program has courses assigned
3. **Sections**: Every program has active Student Groups
4. **Instructors**: Every program has mapped instructors
5. **Capacity**: Enough teachers exist for total slots

### 3.5 On Submit

Publishing a routine auto-creates native `Course Schedule` entries using period timings from `Vidyaan Settings`.

---

## 🔒 4. Roles & Permissions

| Role | Purpose | Access Level |
|---|---|---|
| `System Administrator` | Vidyaan superadmin | Full CRUD on all doctypes + desk UI |
| `Institute Admin` | School-level admin | Full CRUD on education + routine doctypes |
| `Instructor` | Teacher (future) | Currently minimal — will get attendance access |
| `System User` | Basic desk access | Required for all desk users |

---

## 📦 5. Installation Sequence

```
bench install-app vidyaan
    → after_install()
        → install()
            → create_roles()           # System Admin, Institute Admin, Instructor
            → create_default_user()    # vidyaan@weloin.com
            → create_custom_fields()   # Company injection + Instructor Course Mapping
            → create_onboarding()      # Module Onboarding steps
            → setup_vidyaan_settings() # Default period timings (9:00-13:00)
            → create_workspace()       # Vidyaan Dashboard with all shortcuts
        → bypass ERPNext wizard
        → set vidyaan_setup_complete = 0 (triggers setup wizard)
```

---

## 🚀 6. Future Roadmap

- [ ] Inter-school material sharing (`is_global_material` flag)
- [ ] Instructor dashboard (attendance, schedule view)  
- [ ] Student portal (LMS access to courses & materials)
- [ ] Room assignment as solver constraint
- [ ] Assessment & grading integration
- [ ] Fee management per institute
