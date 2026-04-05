# Automated Routine Generation — Implementation Plan

## Background

The goal is to build an automated timetable/routine generation engine powered by Google OR-Tools CP-SAT solver. The Institute Admin selects Programs (classes), and the system auto-generates a conflict-free weekly routine respecting configurable hard & soft constraints. **All input data is pulled dynamically from existing Frappe Doctypes.**

---

## Research Findings (Native Doctype Analysis)

After scanning the Education module source code:

| Native Doctype | What it has | What it's missing |
|---|---|---|
| `Instructor` | Name, Employee, Status, Instructor Log (diary) | **No subject/course mapping** — there's no way to say "this teacher can teach Physics" |
| `Program` | Name, Courses (child table `Program Course`) | ✅ Already links Courses to Programs natively |
| `Course` | Name, Topics, Assessment | Works as-is (subjects) |
| `Student Group` | Program, Course, Instructors (child table) | This is the **output** — we assign teachers here after routine is generated |
| `Course Schedule` | Student Group, Instructor, Course, Date, Time, Room | This is where **individual class slots** live — our generated routine creates these |

### Key Gap
> The `Instructor` doctype has **zero** native ability to declare *"I can teach Physics and Mathematics for Class 11 Science and Class 12 Science"*. This mapping is critical for the solver to know which teacher-subject pairs are valid.

---

## Proposed Doctype Architecture

We need exactly **3 new Doctypes** (2 child tables + 1 parent). Everything else uses existing doctypes.

### New Doctype 1: `Instructor Course Mapping` (Child Table)

> [!IMPORTANT]
> This is injected as a **Custom Field** (child table) on the existing `Instructor` doctype. It is NOT a standalone doctype in the sidebar — it appears as a table section when creating/editing an Instructor.

| Field | Type | Options | Purpose |
|---|---|---|---|
| `course` | Link | Course | The subject this teacher can teach |
| `program` | Link | Program | For which class/stream |
| `is_preferred` | Check | — | Soft preference (solver will try to honor it) |

**When the admin creates an Instructor record**, they fill in this table: *"T1 teaches Math for Class 11 Science ✓ preferred, Math for Class 12 Arts"*.

---

### New Doctype 2: `Routine Slot` (Child Table)

The generated output — each row is one period in the final timetable.

| Field | Type | Options | Purpose |
|---|---|---|---|
| `student_group` | Link | Student Group | The specific section (e.g., "Class 11 Sci - A") |
| `program` | Link | Program | Which class (auto-fetched from Student Group) |
| `day` | Select | Mon/Tue/Wed/Thu/Fri/Sat/Sun | Day of week |
| `period` | Int | — | Period number (1-8) |
| `instructor` | Link | Instructor | Assigned teacher |
| `course` | Link | Course | Assigned subject |
| `room` | Link | Room | (Optional) Assigned room |

---

### New Doctype 3: `Routine Generation` (Parent — Submittable)

The main control panel where the admin triggers generation.

| Field | Type | Options | Purpose |
|---|---|---|---|
| `company` | Link | Company | Institute isolation (SaaS) — **auto-set from user default, read-only** |
| `academic_year` | Link | Academic Year | Filter context |
| `academic_term` | Link | Academic Term | Filter context |
| **Configuration Section** | | | |
| `programs` | Table MultiSelect | Program | Which classes to generate for — **filtered by `company`** |
| `days` | MultiCheck | Mon-Sun | Active school days — **default: Mon-Fri checked** |
| `periods_per_day` | Int | default: **5** | How many periods per day |
| **Constraints Section** | | | |
| `max_subject_per_day` | Int | default: 2 | Same subject can't exceed N periods/day in a section |
| `max_teacher_periods_per_day` | Int | default: 4 | Teacher can't teach more than N periods/day |
| `min_teacher_weekly_load` | Int | default: 8 | Minimum weekly periods for a teacher |
| `max_teacher_weekly_load` | Int | default: 18 | Maximum weekly periods for a teacher |
| `solver_timeout` | Int | default: 30 | Max seconds for solver |
| **Output Section** | | | |
| `routine_slots` | Table | Routine Slot | The generated timetable |
| `status` | Select | Draft/Generating/Generated/Published | Workflow state |
| **Readiness Section** | | | |
| `readiness_html` | HTML | — | Shows live validation: enough teachers? enough courses? |
| **Discovered Sections** | | | |
| `discovered_sections_html` | HTML | — | Shows all Student Groups found under selected Programs |

> [!WARNING]
> **SaaS Isolation on the Form**: The `company` field auto-defaults to the logged-in user's Company and is set to **read-only**. The `programs` multiselect is filtered client-side via `routine_generation.js` using `set_query` so that only Programs belonging to the admin's Company appear. This prevents any cross-institute data leakage at the UI level.

---

## Section Handling Strategy (Critical)

> [!IMPORTANT]
> The solver does **NOT** operate at the `Program` level. It operates at the **`Student Group`** (section) level. Programs are merely the admin's selection input.

### How It Works

```
Admin selects Programs: ["Class 11 Science", "Class 11 Arts"]
    ↓
System auto-discovers Student Groups (WHERE program IN selected, company = mine):
    → "Class 11 Science - Section A"    (Student Group)
    → "Class 11 Science - Section B"    (Student Group)
    → "Class 11 Arts - Section A"       (Student Group)
    ↓
Solver treats EACH Student Group as an independent "class" in the model.
Total classes for solver = 3 (not 2)
```

### Why This Solves Multi-Section

| Scenario | How Solver Handles It |
|---|---|
| Same teacher, same period, different sections | ❌ **Blocked** — teacher conflict constraint prevents it |
| Same teacher, different period, different sections | ✅ Allowed — no conflict |
| Different teachers, same period, same course, different sections | ✅ Allowed — T1 teaches Physics to Section A in P1, T2 teaches Physics to Section B in P1 |

### On Submit: Auto-Create Course Schedule
When the admin clicks **Submit**, the system loops through all `routine_slots` and creates native `Course Schedule` records in the Education module. Each Course Schedule entry will have:
- `student_group` → the section
- `instructor` → assigned teacher
- `course` → assigned subject  
- `schedule_date` → mapped from day + academic term dates
- `from_time` / `to_time` → derived from period number
- `room` → optional, if provided

---

## Readiness Validation Formula (Company-Scoped)

Before the solver runs, **every query is filtered by `company`** to guarantee SaaS isolation:

```
company = self.company  # From the form (auto-set, read-only)

# ━━━ STEP 0: OWNERSHIP VERIFICATION ━━━
For each selected Program P:
  IF P.company != company:
    ❌ "Program 'P' does not belong to your Institute. Remove it."
    (BLOCK generation entirely)

# ━━━ STEP 1: COURSE CHECK ━━━
For each selected Program P (WHERE P.company == company):
  courses_in_P = count of courses linked in Program.courses
    WHERE course.company == company
  
  IF courses_in_P == 0:
    ❌ "Program 'P' has no courses assigned"

# ━━━ STEP 2: INSTRUCTOR CHECK ━━━
  instructors_for_P = count of Instructors WHERE company == company
    AND has at least one Instructor Course Mapping row
    WHERE program == P AND course IN courses_in_P
  
  IF instructors_for_P == 0:
    ❌ "No instructors mapped to Program 'P'"

# ━━━ STEP 3: CAPACITY CHECK ━━━
Total slots = len(programs) × periods_per_day × days
total_active_instructors = count of Instructors WHERE company == company
Min teachers needed = ceil(total_slots / max_teacher_weekly_load)

IF total_active_instructors < Min teachers needed:
  ⚠️ "You have X teachers but need at least Y to fill Z total slots"
```

This validation runs **live** on the form and displays in the `readiness_html` field as a checklist with ✅/❌ indicators.

---

## OR-Tools Solver Adaptation (Company-Isolated)

The user's prototype model is adapted. **Every query enforces `company` filtering.**

| Static (Prototype) | Dynamic (Production) | SaaS Filter |
|---|---|---|
| `classes = ["class6", "class10"]` | `programs = frappe.get_all("Program", ...)` | `{"company": self.company}` |
| `teachers = ["T1","T2"]` | `instructors = frappe.get_all("Instructor", ...)` | `{"company": self.company, "status": "Active"}` |
| `subjects = ["Math","Physics"]` | `courses = unique courses from selected programs` | `{"company": self.company}` |
| `teacher_subject_map = {...}` | Built from `Instructor Course Mapping` child rows | Only rows where mapping's `program.company == self.company` |
| `teacher_week_limit = {...}` | `(min_teacher_weekly_load, max_teacher_weekly_load)` from form | N/A (form-level) |
| `teacher_class_preference = {...}` | Built from `is_preferred` checkboxes in mapping | Already scoped by instructor filter |

> [!NOTE]
> **Triple-layer isolation**: (1) `User Permission` on Company prevents Frappe from even returning cross-institute records. (2) Explicit `{"company": self.company}` filters in every `get_all` call as a safety net. (3) Step 0 ownership verification in readiness check catches any edge case.

---

## Workflow (Institute Admin Onboarding Demo)

### Step 1: Create Programs (Classes)
Admin creates: "Class 5", "Class 11 Science", "Class 11 Arts"
Each Program has Courses linked natively via the `courses` child table.

### Step 2: Create Courses (Subjects)
Admin creates: "Mathematics", "Physics", "English", "Bengali", "History"
- "Class 11 Science" gets: Math, Physics, English, Bengali
- "Class 11 Arts" gets: History, English, Bengali

### Step 3: Create Instructors with Subject Mapping
Admin creates Instructor T1:
| Course | Program | Preferred? |
|---|---|---|
| Mathematics | Class 11 Science | ✅ |
| Mathematics | Class 11 Arts | |

Admin creates Instructor T2:
| Course | Program | Preferred? |
|---|---|---|
| Physics | Class 11 Science | ✅ |
| English | Class 11 Arts | |

### Step 4: Generate Routine
Admin opens **Routine Generation** → selects Programs → clicks **Generate**.
- Readiness check runs first (shows ✅/❌ for each program)
- If all green → OR-Tools solver fires
- Generated slots fill the `routine_slots` table
- Admin reviews → clicks **Submit** to publish

### Step 5: Published Routine
On Submit, the system can optionally create `Course Schedule` records in the Education module for calendar integration.

---

## File Structure

```
vidyaan/
├── vidyaan/
│   ├── doctype/
│   │   ├── instructor_course_mapping/    # [NEW] Child table
│   │   ├── routine_slot/                 # [NEW] Child table  
│   │   └── routine_generation/           # [NEW] Parent doctype
│   │       ├── routine_generation.json
│   │       ├── routine_generation.py     # Solver logic + validation
│   │       └── routine_generation.js     # Readiness UI + Generate button
│   ├── setup/
│   │   └── custom_fields.py              # [MODIFY] Add Instructor Course Mapping table
│   └── docs/
```

---

## User Review Required

> [!CAUTION]
> **New Doctypes**: We need exactly 3 new Doctypes. There is no way around this — the native Education module has no concept of "teacher capability mapping" or "auto-generated timetable storage". These are the absolute minimum.

> [!IMPORTANT]
> **OR-Tools Dependency**: The `ortools` Python package must be installed in the bench environment (`pip install ortools`). Should I add this to the app's `requirements.txt`?

### Resolved Questions
1. ✅ **Days**: Mon-Fri default, Mon-Sun selectable
2. ✅ **Periods**: 5 per day default
3. ✅ **On Submit**: Auto-create Course Schedule entries
4. ✅ **Room**: Optional field, not a solver constraint
5. ✅ **Sections**: Solver discovers Student Groups under selected Programs and treats each as independent class

### Remaining Question
1. **Period Timings**: Should we store default period start/end times somewhere (e.g., Period 1 = 9:00-9:45, Period 2 = 9:45-10:30) so that Course Schedule entries get proper timestamps? If yes, should this be a settings table or fields on the Routine Generation form?

---

## Verification Plan

### Automated Tests
- Unit test: Create 3 Programs, 4 Courses, 5 Instructors with mappings → trigger generate → assert no conflicts
- Validation test: Try generating with insufficient teachers → assert proper error message

### Manual Verification
- Full demo walkthrough: Create data → Generate → Review output → Submit