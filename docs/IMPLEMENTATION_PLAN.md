# Vidyaan - Consolidated Implementation Plan

## Review of Past Plans & Problems Found

### Plan 1: Foundation (Doctype Mapping) — `implementation/plan1.md`
**Status:** Completed
**Verdict:** Sound. The native-doctype-first approach was the right call.
**Issues Found:** None

### Plan 2: Routine Generation — `implementation/plan2.md`
**Status:** Completed
**Verdict:** Well implemented. OR-Tools solver works correctly.
**Issues Found:**
- Period timings question was resolved (stored in Vidyaan Settings as child table)
- No issue with the solver itself

### Plan 3: Exams & Assignments — `implementation/plan3.md`
**Status:** Completed
**Verdict:** Zero-new-doctype approach is elegant.
**Issues Found:**
- The examiner validation hook works but the lookup chain (User → Employee → Instructor) is fragile — if an Instructor doesn't have an Employee link, the check silently fails
- The `create_assessment_publication` sets approver role to "Academic Manager" which doesn't exist by default in Vidyaan's role setup (only System Admin, Institute Admin, Instructor exist)

### Plan 4: Publication System — `implementation/plan4.md`
**Status:** Completed
**Verdict:** Clean implementation.
**Issues Found:**
- Publication permissions only grant to System Manager — Institute Admin should also have submit access
- The approval workflow uses manual Approve/Reject buttons on JS side — should ideally use native Frappe Workflow for robustness
- `allow_guest_to_view: true` may be a security concern if publications contain sensitive content

### Plan 5: Dynamic Application System — `implementation/plan5.md`
**Status:** Incomplete (design only)
**Verdict:** Has fundamental open questions that block implementation.
**Issues Found:**
- No decision on Frappe Workflow vs custom approval logic
- Key-Value child table approach for dynamic fields is non-standard and hard to query/report on
- Multi-level approval complexity may not justify the effort for v1

### Installation Bug
**Critical Issue:** The `after_install` hook fails during `create_vidyaan_custom_fields()` with error:
```
Student: Options must be a valid DocType for field Institute in row 1
```
This happens because a previous install left an orphan `institute` custom field on Student with a Link type but no `options` value. The cleanup script doesn't remove old custom fields before creating new ones.

**Fix needed:** Add cleanup logic at the start of `create_vidyaan_custom_fields()` to remove any stale custom fields from previous installs.

---

## Consolidated Implementation Plan (Improved)

### Phase 1: Bug Fixes & Stability (Priority: Critical)

#### 1.1 Fix Installation Bug
**Problem:** Orphan `institute` custom field blocks reinstall.
**Solution:**
```python
# In custom_fields.py, before creating fields:
def cleanup_stale_fields():
    """Remove custom fields from previous Vidyaan installs."""
    stale_fields = frappe.db.get_all("Custom Field",
        filters={"dt": ["in", education_doctypes], "module": "Vidyaan"},
        pluck="name"
    )
    for field in stale_fields:
        frappe.delete_doc("Custom Field", field, ignore_permissions=True)
    frappe.db.commit()
```

#### 1.2 Fix Publication Permissions
**Problem:** Only System Manager can manage Publications — Institute Admin cannot.
**Solution:** Add Institute Admin to Publication doctype permissions with full CRUD + submit.

#### 1.3 Fix Assessment Publication Approver Role
**Problem:** Auto-created publications set approver_role = "Academic Manager" which doesn't exist.
**Solution:** Change to "Institute Admin" or create the "Academic Manager" role in `roles.py`.

#### 1.4 Strengthen Examiner Validation
**Problem:** User → Employee → Instructor chain fails if links are missing.
**Solution:** Add fallback to check Instructor records directly by `user_id` field (if available), and provide clear error messages when the chain is broken.

---

### Phase 2: Frontend Migration (Priority: High)

#### 2.1 Rebrand MaxEdu → Vidyaan
- Rename all "MaxEdu" references in frontend code
- Update `nuxt.config.ts` app title
- Replace logos and branding assets

#### 2.2 Migrate API Endpoints
- Change from custom `maxedu.api_folder` paths to native Frappe API endpoints
- Pattern: `/api/resource/{doctype}` and `/api/method/{app}.{module}.{method}`

#### 2.3 Update Role Detection
- Update middleware to use new roles: System Administrator, Institute Admin, Instructor
- Map roles to correct dashboards and page access

#### 2.4 Add Institute Admin Dashboard
- Stats: Total students, teachers, programs, courses (Company-scoped)
- Quick actions: Generate Routine, Admit Student, Add Faculty
- Upcoming exams, recent publications

---

### Phase 3: Feature Enhancements (Priority: Medium)

#### 3.1 Routine Generation UI (Frontend)
Build a rich frontend interface for routine generation:
- **Configuration panel**: Multi-select programs, day toggles, constraint sliders
- **Live readiness check**: Visual indicators (checkmarks/crosses) for each validation
- **Solver execution**: "Generate" button with loading state and timeout display
- **Timetable viewer**: Grid-based calendar view (days × periods) with color-coded entries
- **Submit action**: Confirm dialog before creating Course Schedules

#### 3.2 Attendance UI
- Grid-based quick attendance marking for Instructors
- Student Group selector → list of students → Present/Absent/Leave toggles
- Bulk save action

#### 3.3 Fee Management Integration
- Institute-scoped fee structures
- Student-level fee generation from Fee Schedule
- Payment tracking via ERPNext accounting

#### 3.4 Instructor Dashboard (Frontend)
- Today's classes from Course Schedule
- Grading queue (pending Assessment Results)
- Announcement feed from Publications

#### 3.5 Student Dashboard (Frontend)
- Personal timetable from Course Schedule
- Attendance summary
- Exam schedule from Assessment Plans
- Grade view from Assessment Results
- Notices from Publications

---

### Phase 4: New Features (Priority: Low)

#### 4.1 Inter-School Material Sharing
- Use `is_global` flag on Articles/Topics
- Allow System Admin to mark content as shared across all institutes
- Query: `company = current OR is_global = 1`

#### 4.2 Room Assignment in Solver
- Add Room as a constraint in the OR-Tools model
- Hard constraint: no two sections in the same room at the same time
- Requires Room records with capacity information

#### 4.3 Application/Leave System (Plan 5 Redesign)
**Recommended approach:** Use native Frappe Workflow instead of custom approval logic.
- Create a simple `Student Application` doctype with:
  - application_type (Leave, Permission, TC Request, etc.)
  - from_date, to_date
  - reason (Text)
  - status (Draft → Pending → Approved/Rejected)
- Attach a Frappe Workflow with states and transitions
- Use Workflow Actions for role-based approvals
- This is simpler, more maintainable, and leverages Frappe's built-in notification/assignment system

#### 4.4 SMS/Email Notifications
- Notify parents on attendance (absent alerts)
- Notify students on new publications
- Notify instructors on grading deadlines

---

## Implementation Order & Dependencies

```
Phase 1 (Critical) ─── No dependencies, do first
  ├── 1.1 Installation bug fix
  ├── 1.2 Publication permissions
  ├── 1.3 Approver role fix
  └── 1.4 Examiner validation

Phase 2 (High) ─── Can start in parallel with Phase 1
  ├── 2.1 Rebrand (no deps)
  ├── 2.2 API migration (after 2.1)
  ├── 2.3 Role detection (after 2.2)
  └── 2.4 Admin dashboard (after 2.3)

Phase 3 (Medium) ─── Depends on Phase 1 completion
  ├── 3.1 Routine UI (after Phase 2)
  ├── 3.2 Attendance UI (after Phase 2)
  ├── 3.3 Fee management (independent)
  ├── 3.4 Instructor dashboard (after 3.2)
  └── 3.5 Student dashboard (after 3.4)

Phase 4 (Low) ─── Depends on Phase 3 completion
  ├── 4.1 Material sharing (independent)
  ├── 4.2 Room solver (after 3.1)
  ├── 4.3 Application system (independent)
  └── 4.4 Notifications (after 4.3)
```

---

## Files That Need Changes (Phase 1)

| File | Change |
|------|--------|
| `setup/custom_fields.py` | Add `cleanup_stale_fields()` before creating fields |
| `setup/roles.py` | Add "Academic Manager" role OR change publication approver |
| `doctype/publication/publication.json` | Add Institute Admin permissions |
| `utils.py` | Change `approver_role` from "Academic Manager" to "Institute Admin" |
| `events.py` | Add fallback Instructor lookup and better error messages |
