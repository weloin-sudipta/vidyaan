# Dynamic Application & Approval Engine

> **Status:** Future Scope  
> **Priority:** HIGH  
> **Module Name:** Applications  
> **Estimated Doctypes:** 6 (2 master + 1 transaction + 3 child tables)

---

## Problem Statement

Students need to submit various applications (NOC, Leave, Certificate Requests, Transfer Certificates) that require multi-level approvals from different departments. Currently there is no unified system — Education's Student Leave Application is hardcoded with fixed fields and no approval chain, HRMS uses single-approver patterns, and Frappe's native Workflow engine only supports 1 role per transition with no dynamic form capability.

### What's Needed

1. **Dynamic form creation** — Institute admin defines fields per application type (no developer needed)
2. **Multi-level approval chains** — step-by-step approval through different departments
3. **Multiple roles per level (OR logic)** — if HoD is unavailable, Asst. HoD can approve at that level
4. **One engine for all types** — NOC, Leave, Certificate, Transfer — all from the same system
5. **Student-facing UI** — clean frontend for submission and tracking
6. **Librarian/Admin dashboard** — pending approvals, bulk actions, SLA tracking

---

## Why Not Use Frappe's Native Workflow?

| Factor | Frappe Workflow | Custom Application Engine |
|--------|----------------|--------------------------|
| Dynamic form fields | No (hardcoded doctype) | Yes (admin configures) |
| Multi-role per level | No (1 role per transition) | Yes (OR logic) |
| Admin creates new types | No (needs developer) | Yes (from Desk) |
| Parallel approvals | No | Yes (is_parallel flag) |
| Approval log | No built-in | Yes (who/when/remarks) |
| Student-facing UI | No | Yes (Nuxt frontend) |
| Complexity | Low | Medium |
| Maintenance | Frappe handles | We maintain |

**Verdict**: Frappe's Workflow is great for simple A→B→C flows on existing doctypes. But our requirements (dynamic forms, multi-role levels, student-facing UI, various application types from one engine) need a custom solution.

---

## Architecture: 6-Doctype Design

```
Application Type (Master - defines the form + approval chain)
  ├── Application Field (child) - dynamic form fields
  └── Approval Step (child) - approval chain with multi-role per level

Student Application (Transaction - actual submissions)
  ├── Application Value (child) - student's filled form data
  └── Approval Log (child) - who approved/rejected at each level
```

---

## Detailed Data Model

### 1. Application Type (Master)

| Field | Type | Description |
|-------|------|-------------|
| `application_type_name` | Data (required, title) | e.g., "No Objection Certificate" |
| `category` | Select | NOC / Leave / Request / Certificate / General |
| `description` | Text | What this application is for |
| `is_active` | Check (default 1) | Can students submit this type? |
| `allow_multiple` | Check | Can student have more than one active application? |
| `requires_attachment` | Check | Must student upload a document? |
| `max_processing_days` | Int | SLA — expected completion days (0 = no limit) |
| `auto_reject_after_days` | Int | Auto-reject if idle (0 = disabled) |
| `notify_on_submission` | Check | Email student on submit |
| `notify_on_completion` | Check | Email student on final approve/reject |
| `notify_approvers` | Check | Email next approver when their turn comes |
| `allow_withdrawal` | Check | Student can withdraw before completion |
| `result_document` | Select | None / Generate PDF / Generate Print |
| `fields` | Table → Application Field | Dynamic form fields |
| `approval_steps` | Table → Approval Step | Approval chain |

### 2. Application Field (Child Table)

| Field | Type | Description |
|-------|------|-------------|
| `field_label` | Data (required) | e.g., "Reason for Leaving" |
| `field_key` | Data | Auto-generated slug from label |
| `field_type` | Select | Data / Text / Date / Select / Check / Attach / Int / Currency |
| `options` | Small Text | Newline-separated for Select type |
| `is_required` | Check | Must be filled? |
| `description` | Small Text | Help text shown below field |
| `display_order` | Int | Display sequence |

### 3. Approval Step (Child Table)

**Key design: Multiple rows with the same `level` number = OR logic (any of those roles can approve)**

| Field | Type | Description |
|-------|------|-------------|
| `level` | Int (required) | Same level = OR between roles |
| `step_name` | Data (required) | e.g., "Library Clearance" |
| `role` | Link → Role (required) | Who can approve at this level |
| `can_reject` | Check (default 1) | Can this level reject? |
| `can_return` | Check (default 0) | Can send back to student for correction? |
| `is_parallel` | Check (default 0) | See parallel approvals section |
| `instruction` | Small Text | Guidance for approver at this level |

**Example for NOC:**

| Level | Step Name | Role |
|-------|-----------|------|
| 1 | Library Clearance | Librarian |
| 2 | Department Approval | HoD |
| 2 | Department Approval | Asst. HoD |
| 3 | Accounts Clearance | Accounts Manager |
| 3 | Accounts Clearance | Accountant |
| 4 | Final Approval | Institute Admin |

Level 2: Either HoD **OR** Asst. HoD can approve. No need for both.
Level 3: Either Accounts Manager **OR** Accountant can approve.

### 4. Student Application (Transaction, Submittable)

| Field | Type | Description |
|-------|------|-------------|
| naming | — | `APP-.YYYY.-.#####` |
| `application_type` | Link → Application Type (required) | Which form to fill |
| `student` | Link → Student (required) | Auto-set from logged-in user |
| `student_name` | Data (fetched) | Snapshot |
| `program` | Data (fetched) | From student enrollment |
| `submission_date` | Date (auto) | When submitted |
| `status` | Select | Draft / Pending / In Progress / Approved / Rejected / Returned / Withdrawn |
| `current_level` | Int | Which approval level we're at (starts at 1) |
| `total_levels` | Int | Snapshot from Application Type at submission |
| `remarks` | Text | Student's note |
| `admin_remarks` | Text | Final remarks from last approver |
| `completed_date` | Datetime | When finally approved/rejected |
| `values` | Table → Application Value | Student's filled form data |
| `approval_log` | Table → Approval Log | Full audit trail |

### 5. Application Value (Child Table)

| Field | Type | Description |
|-------|------|-------------|
| `field_label` | Data | Field name |
| `field_key` | Data | Slug key |
| `field_type` | Data | Original field type |
| `value` | Long Text | All types stored as string |

### 6. Approval Log (Child Table)

| Field | Type | Description |
|-------|------|-------------|
| `level` | Int | Which level |
| `step_name` | Data | Level name |
| `action` | Select | Approved / Rejected / Returned / Skipped |
| `action_by` | Link → User | Who took action |
| `action_by_name` | Data | Name snapshot |
| `role_used` | Data | Which role this user used to approve |
| `action_date` | Datetime | When |
| `remarks` | Text | Approver's comment |

---

## Approval Flow

```
Student fills form → Status: Pending, current_level = 1
       │
       ▼
Level 1 (Librarian) sees it in their queue
       │── Approve → current_level = 2, log entry
       │── Reject  → Status: Rejected, done
       │── Return  → Status: Returned, student can edit & resubmit
       │
       ▼
Level 2 (HoD OR Asst. HoD) — whoever acts first
       │── Approve → current_level = 3
       │── Reject  → Status: Rejected
       │
       ▼
Level 3 (Accounts) ...
       │
       ▼
Level N (last level) → Approve → Status: Approved, completed_date set
```

### Core Controller Logic

```python
def approve_application(application, remarks=""):
    # 1. Verify user has a role matching current level
    # 2. Check level not already approved in log
    # 3. Log the approval in Approval Log
    # 4. If current_level == total_levels → Status = "Approved"
    # 5. Else → current_level += 1, notify next level approvers

def reject_application(application, remarks=""):
    # 1. Verify user has role for current level + can_reject is True
    # 2. Log rejection in Approval Log
    # 3. Status = "Rejected", notify student

def return_application(application, remarks=""):
    # 1. Verify can_return is True for current level
    # 2. Log return in Approval Log
    # 3. Status = "Returned", student can edit and resubmit
    # 4. On resubmit, resume from current_level (not level 1)

def withdraw_application(application):
    # 1. Verify student owns the application
    # 2. Verify allow_withdrawal is True on Application Type
    # 3. Verify status is not already Approved/Rejected
    # 4. Status = "Withdrawn"
```

### Parallel Approvals

When `is_parallel = True` on approval steps:
- All parallel levels activate simultaneously
- ALL must approve before moving to next non-parallel level
- Any single rejection at parallel levels rejects the whole application

Example: Library (parallel) + Accounts (parallel) + Lab (parallel) → all three must approve → then HoD (sequential)

---

## Edge Cases & Solutions

| Edge Case | Solution |
|-----------|----------|
| **Approver on leave** | Multi-role per level — another person with same/different role at that level can approve |
| **Approval chain changes after submission** | `total_levels` is snapshotted at submission. Steps are read from Application Type at action time but level count is frozen |
| **Student wants to edit after submit** | Not allowed unless an approver "Returns" it. Student can only "Withdraw" |
| **Approver tries to approve twice** | Check Approval Log — if level already has an "Approved" entry, block |
| **Student submits duplicate** | `allow_multiple` check on Application Type. If false, block if active application exists |
| **Time-based auto-reject** | Scheduler job checks `auto_reject_after_days`. If last action date + days < now, auto-reject |
| **Self-approval** | If student also has an approver role, block them from approving their own application |
| **Approval chain is empty** | Validate on Application Type save — must have at least 1 step |
| **Role doesn't exist or no users have it** | Show warning on Application Type, but don't block (role might be assigned later) |
| **Student leaves / gets expelled mid-application** | Check student status on each approval action |
| **Approver doesn't have permission to view student data** | Application shows only the form values + student name, not full student record |

---

## Real-World Examples

### NOC (No Objection Certificate)
- **Application Type**: "No Objection Certificate"
- **Fields**: Reason, Last Day, Forwarding Address, Library Card Number
- **Steps**: Library (1) → HoD + Asst.HoD (2) → Accounts (3) → Admin (4)
- **Config**: `allow_multiple = false`, `result_document = Generate PDF`

### Student Leave
- **Application Type**: "Student Leave"
- **Fields**: From Date, To Date, Reason, Attach Medical Certificate
- **Steps**: Class Teacher (1) → HoD (2)
- **Config**: `allow_multiple = true`, integrates with attendance on approval

### Bonafide Certificate
- **Application Type**: "Bonafide Certificate Request"
- **Fields**: Purpose, Number of Copies
- **Steps**: Admin Office (1)
- **Config**: Simple 1-step, `result_document = Generate PDF`

### Transfer Certificate
- **Application Type**: "Transfer Certificate"
- **Fields**: Reason for Transfer, Destination School, Parent Contact
- **Steps**: Library (1) → Lab (2) → Accounts (3) → HoD (4) → Principal (5)
- **Config**: `allow_multiple = false`, `requires_attachment = true`

### Hostel Leave
- **Application Type**: "Hostel Leave Pass"
- **Fields**: From Date, To Date, Destination, Emergency Contact
- **Steps**: Warden (1) → Chief Warden (2)
- **Config**: `allow_multiple = true`, `auto_reject_after_days = 3`

---

## Feature Roadmap

### Phase 1 — Core (Must Have)

- [ ] Application Type master with dynamic fields and approval steps
- [ ] Student Application submission and tracking
- [ ] Multi-level approval with OR logic for roles
- [ ] Approve / Reject / Return actions
- [ ] Student dashboard — submit forms + track progress (visual progress bar)
- [ ] Approver dashboard — pending queue with action buttons
- [ ] Email notifications (configurable per type)
- [ ] Approval Log audit trail

### Phase 2 — Enhanced (Should Have)

- [ ] Parallel approvals (`is_parallel` flag)
- [ ] Auto-reject scheduler (based on `auto_reject_after_days`)
- [ ] SLA tracking — time taken at each level, flag overdue
- [ ] Bulk approval for approvers
- [ ] Withdrawal by student
- [ ] Print format with approval stamps at each level
- [ ] Admin analytics — processing times, approval/rejection rates, bottleneck levels

### Phase 3 — Advanced (Nice to Have)

- [ ] Conditional routing — skip/add levels based on field values (e.g., if "International Student" = Yes, add Immigration Office level)
- [ ] Delegation management — approver delegates to another user while on vacation
- [ ] Digital signature capture at each approval level
- [ ] QR code verification for printed documents
- [ ] Comment thread between approver and student within application
- [ ] Webhook integration — trigger external actions on approval
- [ ] Escalation matrix — if Level N doesn't act in X days, auto-notify their superior
- [ ] Application templates — pre-fill common fields for repeated types
- [ ] Mobile push notifications via Firebase

---

## API Endpoints (Planned)

### Student APIs

| Endpoint | Purpose |
|----------|---------|
| `get_application_types()` | List available application types for student |
| `get_application_form(type)` | Get fields + metadata for a specific type |
| `submit_application(type, values)` | Submit a new application |
| `get_my_applications(status)` | List student's applications with progress |
| `get_application_detail(name)` | Full detail with approval log |
| `withdraw_application(name)` | Withdraw a pending application |
| `resubmit_application(name, values)` | Resubmit after "Returned" |

### Approver APIs

| Endpoint | Purpose |
|----------|---------|
| `get_pending_approvals()` | Applications waiting for current user's action |
| `approve(name, remarks)` | Approve at current level |
| `reject(name, remarks)` | Reject at current level |
| `return_to_student(name, remarks)` | Send back for correction |
| `get_approval_history(name)` | Full audit trail |
| `bulk_approve(names, remarks)` | Approve multiple at once |

### Admin APIs

| Endpoint | Purpose |
|----------|---------|
| `get_application_stats()` | Dashboard metrics |
| `get_all_applications(filters)` | All applications with filters |
| `get_sla_report()` | Processing time analytics |

---

## Frontend Pages (Planned)

### Student Side

| Page | Description |
|------|-------------|
| `/applications` | List of available application types + my submissions |
| `/applications/new/:type` | Dynamic form rendered from Application Type fields |
| `/applications/:name` | Application detail + visual progress tracker |

### Approver Side

| Page | Description |
|------|-------------|
| `/admin/applications` | Pending approval queue with filters |
| `/admin/applications/:name` | Review + approve/reject with remarks |

### Admin Side

| Page | Description |
|------|-------------|
| Frappe Desk → Application Type | Create/edit application types with form builder |
| Frappe Desk → Student Application | View all submissions, analytics |

---

## Technical Notes

- **No nested child tables** — Frappe doesn't support them. Multi-role per level is achieved by multiple rows with the same `level` number in the flat Approval Step child table.
- **Value storage** — All field values stored as strings in Application Value. Frontend handles type rendering (dates, checkboxes, etc.) based on `field_type`.
- **Snapshot principle** — `total_levels` and `student_name` are frozen at submission time. Approval steps are read live from Application Type (allows admin to fix chain without breaking in-flight apps, but level count stays fixed).
- **Integration with Education** — Student link provides auto-fetch of name, program, enrollment. No modification to Education doctypes needed.
- **Existing Student Leave Application** — Can coexist. The dynamic engine handles new leave types; the existing Education doctype continues working for backward compatibility.

---

*Created: 2026-04-03*
