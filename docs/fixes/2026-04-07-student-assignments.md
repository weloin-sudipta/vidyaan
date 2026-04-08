# Fix Log — Student-Side Assignments Visibility & Submission

**Date:** 2026-04-07
**Scope:** Student portal assignment listing + submission flow
**Severity:** High (students could not see or submit assignments)
**Files touched:** 2 backend, 1 frontend

---

## 1. Reported Symptoms

1. **Students see no assignments** on `/academics/assignments`, even after the
   instructor created and (sometimes) published them.
2. **Submissions silently fail** — modal closes, page refreshes, but no file
   ends up attached to the submission row.

## 2. Root Causes

### Cause A — Visibility tied to row existence
`get_student_assignments()` only returned assignments where an
`Assignment Submission` child row already existed for the student.
Submission rows are created exclusively at publish time inside
`publish_assignment()`, which iterates `Student Group Student` with
`active=1`.

Failure modes that left a published assignment invisible to a real student:

| # | Scenario | Why it broke |
|---|----------|--------------|
| 1 | Student joined the target group **after** the instructor published | No row was ever generated for them |
| 2 | Student Group Student row had `active != 1` | Filtered out at publish time |
| 3 | Instructor created the assignment but never clicked "Publish" | Status stays `Draft` (this is by design, but the empty UI gave no hint) |

### Cause B — Submission fire-and-forget
Frontend `performSubmit` did:

```js
const uploaded = await uploadFile(selectedFile.value)
if (uploaded?.error) { ... }
const res = await submitAssignment(activeTask.value.name, uploaded.file_url)
```

Two latent bugs:
1. If the upload returned a non-error but malformed shape (no `file_url`),
   `submitAssignment` was called with `submission_file: undefined`.
2. The backend `submit_student_assignment` code path
   `if submission_file: target_row.submission_file = submission_file`
   silently skipped storage and still flipped `status = "Submitted"`.
   Result: success response, no file, no error visible to the user.

### Cause C — Submission rejected for "late joiners"
`submit_student_assignment` raised `"You are not enrolled in this assignment"`
whenever the student lacked a row, even if they were a legitimate member of
one of the assignment's target groups (Cause A scenario 1).

---

## 3. Fixes

### 3.1 Backend — `vidyaan/api_folder/assignments.py`

#### `get_student_assignments()` — union with target-group membership
The query now collects assignment names from **two** sources and unions them:

1. Direct `Assignment Submission` rows for the student (legacy path).
2. `Assignment Target Group` rows whose `student_group` the student belongs
   to (via `Student Group Student`).

Both sets are then filtered by `Assignment.status == "Published"`.
Students whose row hasn't materialised yet still see the assignment with a
placeholder `my_submission.status = "Pending"`.

#### `submit_student_assignment()` — auto-heal + payload guard
- New helper `_student_in_target_groups(doc, student_name)` resolves
  membership without loading every group.
- If no submission row exists but the student IS in a target group, a fresh
  `Pending` row is appended on the fly, then updated with the submission.
- Hard guard added at the top: throws `"Submission must include a file or
  text. Nothing was uploaded."` when both `submission_file` and
  `submission_text` are blank — kills the silent-success path described in
  Cause B.

### 3.2 Frontend — `frontend/pages/academics/assignments.vue`

`performSubmit` rewritten:
- Pre-check that a file is selected.
- Use `'error' in uploaded` discrimination instead of optional chaining.
- Explicitly assert `uploaded.file_url` is non-empty before submitting.
- Wrap the whole flow in a `try/catch` so unexpected exceptions surface
  in the modal instead of leaving `submitting` stuck.

Empty-state hint added: when the entire list is empty, the user is told
"If you expect to see an assignment, ask your teacher to publish it from the
teacher portal."

---

## 4. Edge Cases Covered After Fix

| Scenario | Before | After |
|----------|--------|-------|
| Student joins group post-publish | Invisible | Visible, status `Pending`, can submit (row auto-created) |
| Instructor never publishes | Invisible | Still invisible (correct — Draft is private) |
| Upload silently returns no `file_url` | Modal closes, no file | Inline error: "Upload succeeded but no file URL was returned." |
| User clicks Submit with no file selected | Network call fired | Inline error, no network call |
| Backend called with empty payload (e.g. legacy client) | Stamped as Submitted with no file | Throws clear validation error |
| Late submission | Marked `Late` ✅ | Unchanged ✅ |
| Closed assignment | Throws ✅ | Unchanged ✅ |
| Already-graded submission | Score preserved ✅ | Unchanged ✅ |
| Assignment with zero target groups | Empty list | Empty list (still correct) |

---

## 5. Deploy Steps

```bash
cd /home/weloin/Projects/frappe-bench
bench --site dev.localhost clear-cache
bench restart            # or: bench --site dev.localhost reload
```

No DocType or schema changes — `bench migrate` is **not** required.

## 6. Manual Smoke Test Plan

1. As instructor: create + publish an assignment for a course with at least
   one student in a target group.
2. As that student: open `/academics/assignments` — assignment should appear
   under **Active**.
3. Add a brand-new student to the same `Student Group` (via Frappe Desk).
4. Log in as the new student — assignment should still appear (was the
   broken case).
5. Try to submit without picking a file → inline error.
6. Pick a file → submit → expect success, page refreshes, status flips to
   **Submitted**.
7. As instructor: open the assignment in the teacher portal → the new
   student's row should exist with the uploaded file attached.

---

## 7. Files Changed

| File | Change |
|------|--------|
| `vidyaan/api_folder/assignments.py` | Refactored `get_student_assignments` (union query); added `_student_in_target_groups` helper; `submit_student_assignment` now auto-heals missing rows and validates payload |
| `frontend/pages/academics/assignments.vue` | Hardened `performSubmit`; added empty-state hint |
| `docs/fixes/2026-04-07-student-assignments.md` | This document |

## 8. Follow-ups (not in this fix)

- Consider making `publish_assignment` re-runnable so instructors can
  "refresh" the submission list when new students join. The current
  auto-heal in `submit_student_assignment` handles the read path; only
  re-publishing would handle proactive grading-table population.
- Notification/email when an assignment is published to a group.
- Backend permission check on `Assignment` for the student role (currently
  relies on `_require_student()` plus internal filters).
