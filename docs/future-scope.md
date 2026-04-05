# Vidyaan - Future Scope & Roadmap

## How to Read This Document

Each item includes:
- **Priority**: Critical / High / Medium / Low
- **Effort**: S (hours) / M (1-2 days) / L (3-5 days) / XL (1+ week)
- **Status**: Bug / Todo / In Progress / Done / Blocked / Idea
- **Approach**: How it should be implemented

---

## Critical: Bugs & Blockers

### BUG-001: Installation fails on reinstall (orphan `institute` field)
- **Priority:** Critical | **Effort:** S
- **Status:** Done (Plan 6)
- **Fix:** Added `cleanup_stale_fields()` in `custom_fields.py` that removes orphan `institute` fields before creating correct `company` fields.

### BUG-002: Publication approver role doesn't exist
- **Priority:** Critical | **Effort:** S
- **Status:** Done (Plan 6)
- **Fix:** Changed `approver_role` from "Academic Manager" to "Institute Admin" in `utils.py`.

### BUG-003: Institute Admin can't manage Publications
- **Priority:** Critical | **Effort:** S
- **Status:** Done (Plan 6)
- **Fix:** Added Institute Admin role with full CRUD + submit/cancel to `publication.json`. Also added read-only access for Instructor role.

### BUG-004: Fragile examiner validation chain
- **Priority:** High | **Effort:** S
- **Status:** Done (Plan 6)
- **Fix:** Added fallback SQL join lookup (Instructor → Employee → User) and clear error messages in `events.py`.

---

## High Priority: Frontend Migration

### FE-001: Rebrand MaxEdu → Vidyaan
- **Priority:** High | **Effort:** M
- **Status:** Todo
- **Problem:** Frontend still uses "MaxEdu" branding everywhere.
- **Approach:** Global search-replace across all frontend files. Update `nuxt.config.ts`, logos, page titles.
- **Files:** All files under `frontend/`

### FE-002: Migrate API endpoints
- **Priority:** High | **Effort:** M
- **Status:** Todo
- **Problem:** Composables reference old `maxedu.api_folder` endpoints that don't exist.
- **Approach:** Refactor all composables to use native Frappe API patterns (`/api/resource/`, `/api/method/`).
- **Files:** All files under `frontend/composable/`

### FE-003: Update role detection in middleware
- **Priority:** High | **Effort:** S
- **Status:** Todo
- **Problem:** Middleware checks for old role names.
- **Approach:** Update `auth.global.js` and `role-based.global.js` to use: System Administrator, Institute Admin, Instructor, Student.
- **Files:** `frontend/middleware/`

### FE-004: Build Institute Admin dashboard
- **Priority:** High | **Effort:** L
- **Status:** Todo
- **Problem:** No admin dashboard in frontend — only Desk workspace exists.
- **Approach:** Create `/dashboard/admin.vue` with stat cards (students, teachers, programs), quick actions (generate routine, admit student), upcoming exams, recent publications. All API calls Company-scoped.
- **Files:** `frontend/pages/dashboard/admin.vue`, new composable `useAdminDashboard.js`

---

## Medium Priority: Feature Enhancements

### ENH-001: Routine Generation frontend UI
- **Priority:** Medium | **Effort:** XL
- **Status:** Todo
- **Approach:** Build a rich page at `/admin/routine/` with:
  - Program multi-select with Company filter
  - Day toggles (Mon-Sat checkboxes)
  - Constraint sliders (max subject/day, teacher load, timeout)
  - "Check Readiness" button → color-coded validation report
  - "Generate" button → loading state with timeout countdown
  - Grid-based timetable viewer (days × periods, color-coded by subject)
  - "Submit" confirmation dialog → creates Course Schedules
- **API calls:** Existing whitelisted methods `check_readiness()` and `generate_routine()`

### ENH-002: Quick attendance marking UI
- **Priority:** Medium | **Effort:** L
- **Status:** Todo
- **Approach:** Page at `/teacher/academics/attendance.vue`:
  - Select Student Group → load students
  - Date picker (defaults to today)
  - Grid: Student Name | Present | Absent | Leave (radio buttons)
  - "Save All" bulk action via `/api/method/` or batch resource creation
- **Doctype:** Student Attendance (native)

### ENH-003: Instructor dashboard
- **Priority:** Medium | **Effort:** L
- **Status:** Todo
- **Approach:** Page at `/dashboard/teacher.vue`:
  - Today's schedule from Course Schedule (filtered by instructor + today's date)
  - Grading queue: Assessment Plans where instructor is examiner, results not yet submitted
  - Recent publications/announcements

### ENH-004: Student dashboard
- **Priority:** Medium | **Effort:** L
- **Status:** Todo
- **Approach:** Page at `/dashboard/student.vue`:
  - Personal timetable from Course Schedule (via Student Group membership)
  - Attendance summary (present/absent/leave counts)
  - Upcoming exams from Assessment Plans
  - Recent grades from Assessment Results
  - Notices from Publications (filtered by student's Student Group)

### ENH-005: Fee management integration
- **Priority:** Medium | **Effort:** L
- **Status:** Todo
- **Approach:**
  - Use native Fee Structure + Fees doctypes
  - Add Company field filtering (already injected)
  - Frontend page for students to view fee status
  - Admin page to generate fees from Fee Schedule

---

## Low Priority: New Features

### NEW-001: Inter-school material sharing
- **Priority:** Low | **Effort:** M
- **Status:** Idea
- **Approach:** Add `is_global_material` check field to Article/Topic. Query: `WHERE company = :user_company OR is_global_material = 1`. Only System Admin can set global flag.

### NEW-002: Room assignment in solver
- **Priority:** Low | **Effort:** M
- **Status:** Idea
- **Approach:** Add hard constraint to OR-Tools model: no two sections in same Room at same time/day. Requires Room records to exist. Add `room` to Routine Slot output.

### NEW-003: Dynamic Application & Approval Engine
- **Priority:** Low | **Effort:** L
- **Status:** Idea (Plan 5 redesign)
- **Recommended approach:** Custom solution instead of Frappe Workflow for dynamic forms and multi-role approvals.
- **Architecture:** 6 doctypes (Application Type, Application Field, Approval Step, Student Application, Application Value, Approval Log)
- **Why not Frappe Workflow:** Needs dynamic form fields, multi-role per level (OR logic), student-facing UI, various application types from one engine.

### NEW-004: SMS/Email notifications
- **Priority:** Low | **Effort:** M
- **Status:** Idea
- **Approach:** Use Frappe's Notification doctype:
  - Absent alert: Trigger on Student Attendance where status=Absent, send to parent email
  - New publication: Trigger on Publication where status=Approved
  - Grading deadline: Scheduled notification for Assessment Plans approaching date

### NEW-005: Student/Parent portal login
- **Priority:** Low | **Effort:** L
- **Status:** Idea
- **Approach:** Use Frappe's Website User system. Student doctype already has `user` field. Create Website Users for students with limited portal access. Parents via Guardian → User link.

### NEW-006: Report cards / Transcripts
- **Priority:** Low | **Effort:** M
- **Status:** Idea
- **Approach:** Custom Print Format on Student or Assessment Result using:
  - Native Student Report Generation Tool for weighted calculation
  - Jinja template pulling all Assessment Results for an Academic Term
  - PDF generation via Frappe's built-in print

---

## Roadmap Summary

```
NOW (Sprint 1)
  ├── BUG-001: Fix installation bug
  ├── BUG-002: Fix approver role
  ├── BUG-003: Fix publication permissions
  └── BUG-004: Fix examiner validation

NEXT (Sprint 2)
  ├── FE-001: Rebrand to Vidyaan
  ├── FE-002: Migrate API endpoints
  ├── FE-003: Update role detection
  └── FE-004: Admin dashboard

LATER (Sprint 3-4)
  ├── ENH-001: Routine generation UI
  ├── ENH-002: Attendance UI
  ├── ENH-003: Instructor dashboard
  ├── ENH-004: Student dashboard
  └── ENH-005: Fee management

FUTURE (Sprint 5+)
  ├── NEW-001: Material sharing
  ├── NEW-002: Room solver
  ├── NEW-003: Application system
  ├── NEW-004: Notifications
  ├── NEW-005: Portal login
  └── NEW-006: Report cards
```