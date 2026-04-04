# Plan 7: Student Applications (NOC, Leave, Request)

> **Status:** Implemented  
> **Priority:** HIGH  
> **Module:** Vidyaan (core)  
> **Depends on:** Education module (Student Leave Application)

---

## Problem Statement

Students need to submit various applications (NOC, Leave, Requests) that go through multi-level approval workflows. The system must be:

1. **Dynamic** — students only see application types that the admin has enabled via Frappe Workflow
2. **Workflow-driven** — approval steps, roles, and transitions are configured by Institute Admin in Frappe Desk
3. **Unified** — all application types (NOC, Leave, Request) tracked in one frontend page
4. **Trackable** — visual workflow timeline showing progress through approval steps

---

## Architecture Decision

**Use Frappe's native Workflow engine** — no custom approval logic.

| Component | Responsibility |
|-----------|---------------|
| **Frappe Workflow** | State machine, transitions, role-based approvals, email alerts |
| **Our Doctypes** | Student NOC, Student Request (submittable, with `workflow_state` field) |
| **Education Doctype** | Student Leave Application (already exists) |
| **Our API** | Dynamic type discovery, unified listing, submission helpers |
| **Our Frontend** | Dynamic form selection, submission modals, workflow timeline |

The admin creates Workflows in Frappe Desk → students automatically see the application type in their frontend. No code changes needed to add/remove application types.

---

## Doctypes Created

### Student NOC (`vidyaan/vidyaan/doctype/student_noc/`)

**Purpose:** No Objection Certificates — leaving, transfer, bonafide, no-dues, character certificates.

| Field | Type | Notes |
|-------|------|-------|
| `student` | Link → Student | Required, auto-set from logged-in user |
| `student_name` | Data | Fetched from student |
| `program` | Link → Program | Fetched from student |
| `noc_type` | Select | 6 types: Leaving/Transfer/Bonafide/No Dues/Character/Other |
| `purpose` | Text | Required — reason for NOC |
| `effective_date` | Date | When NOC takes effect |
| `destination` | Data | Target institution (if transfer) |
| `status` | Select | Draft/Pending/In Progress/Approved/Rejected/Cancelled |
| `workflow_state` | Link → Workflow State | For Frappe Workflow engine |
| **Clearance Section** | | Filled by departments during approval |
| `library_clearance` | Select | Cleared/Pending Dues/Not Applicable |
| `accounts_clearance` | Select | Same options |
| `lab_clearance` | Select | Same options |
| `hostel_clearance` | Select | Same options |
| `*_remarks` | Small Text | Remarks per department |
| `approved_by` | Link → User | Final approver |
| `supporting_document` | Attach | Optional attachment |

- **Submittable** (`is_submittable: 1`) — works with Frappe Workflow
- **All clearance + approval fields** have `allow_on_submit: 1` so approvers can fill them after submission
- **Duplicate prevention** — blocks if student has active NOC of same type
- **Naming:** `EDU-NOC-.YYYY.-.#####`

### Student Request (`vidyaan/vidyaan/doctype/student_request/`)

**Purpose:** General requests to administration — academic, facilities, complaints, permissions.

| Field | Type | Notes |
|-------|------|-------|
| `student` | Link → Student | Required |
| `category` | Select | 7 types: General/Academic/Administrative/Facility/Complaint/Permission/Other |
| `priority` | Select | Low/Medium/High/Urgent |
| `subject` | Data | Required — brief title |
| `description` | Text Editor | Required — detailed description |
| `status` | Select | Draft/Open/In Review/Approved/Rejected/Resolved/Closed |
| `workflow_state` | Link → Workflow State | For Frappe Workflow |
| **Response Section** | | Filled by authority |
| `assigned_to` | Link → User | Who's handling it |
| `response` | Text Editor | Official response |
| `resolved_by` | Link → User | Auto-set on resolution |
| `resolution_date` | Datetime | Auto-set on resolution |
| `attachment` | Attach | Supporting document |

- **Submittable** (`is_submittable: 1`)
- **Auto-timestamps** — resolution_date and resolved_by auto-set when status changes to Resolved/Closed
- **Naming:** `EDU-REQ-.YYYY.-.#####`

### Permissions (both doctypes)

| Role | Create | Read | Write | Submit | Cancel |
|------|--------|------|-------|--------|--------|
| Student | Yes | Yes | — | — | — |
| Instructor | — | Yes | Yes | Yes | — |
| Librarian | — | Yes | Yes (after submit) | — | — |
| Institute Admin | Yes | Yes | Yes | Yes | Yes |
| System Manager | Yes | Yes | Yes | Yes | Yes |

---

## API Design (`api_folder/applications.py`)

### Dynamic Type Discovery

```
GET get_available_application_types()
```

Returns only application types that have an active Frappe Workflow configured (or Student Leave Application which is always available). Each type includes:
- `key` — identifier (leave/noc/request)
- `label`, `icon`, `color`, `description` — for UI rendering
- `workflow_steps` — ordered list of workflow states for timeline

**How it works:**
1. Iterates over supported doctypes
2. Calls `frappe.model.workflow.get_workflow_name(doctype)`
3. If active workflow exists → include in response with workflow steps
4. Student Leave Application always included (core Education doctype)

### Unified Application Listing

```
GET get_my_applications()
```

Aggregates Student NOC + Student Request + Student Leave Application for the logged-in student. Each application includes:
- Standard fields (name, type, subject, status, date)
- `workflow_steps` — for timeline rendering
- Current `status` resolved from `workflow_state` (if workflow exists) or `status` field

### Application Detail

```
GET get_application_detail(doctype, name)
```

Full detail including clearances (NOC), response (Request), and workflow action history from Frappe's Comment system.

### Submission APIs

| Endpoint | Purpose |
|----------|---------|
| `submit_noc(noc_type, purpose, ...)` | Create + submit Student NOC |
| `submit_request(subject, description, ...)` | Create + submit Student Request |
| `submit_leave(from_date, to_date, reason)` | Create + submit Student Leave Application |

All submission APIs:
1. Resolve student from logged-in user
2. Create the document
3. Call `doc.submit()` — triggers Frappe Workflow if configured

---

## Frontend Implementation

### Page: `/applications/index.vue`

**Dynamic type selection:**
- On mount, calls `get_available_application_types()` to get enabled types
- "New Application" button opens TypeSelector modal showing only available types
- If admin hasn't created a workflow for NOC → NOC option doesn't appear

**Application cards:**
- Type badge (color-coded: NOC=purple, Leave=blue, Request=indigo)
- Priority badge (for requests)
- Status badge (color-coded: Pending=amber, Approved=green, Rejected=red)
- Description preview (HTML stripped, 150 chars)

**Workflow timeline** (per card):
- Horizontal step indicator below each application card
- Steps pulled from `workflow_steps` in API response
- Progress line fills based on current state position
- Step dots: completed (green check), current (pulsing indigo), future (gray number)
- Terminal states: Approved (all green), Rejected (red on last step)

**Filter tabs:** All | NOC | Leave | Requests

**Sidebar:** Summary cards (Total, Pending, Approved, Rejected)

### Components

| Component | Purpose |
|-----------|---------|
| `TypeSelector.vue` | Modal showing available application types as cards. Empty state if no workflows configured. |
| `NocModal.vue` | NOC submission form — type, purpose, effective date, destination |
| `RequestModal.vue` | Request submission form — category, priority, subject, description |
| `LeaveModal.vue` | Leave submission form — from/to date with day calculator, reason |

---

## How the Admin Configures Workflows

### Step 1: Create Workflow States (one-time)

In Frappe Desk → Workflow State, create states like:
- `Pending Approval` (style: Warning)
- `Library Review` (style: Info)
- `HOD Review` (style: Info)
- `Approved` (style: Success)
- `Rejected` (style: Danger)

### Step 2: Create Workflow

In Frappe Desk → Workflow → New:

**Example: "Student NOC Approval"**
- Document Type: `Student NOC`
- Is Active: Yes

**States:**
| State | Doc Status | Allow Edit |
|-------|-----------|------------|
| Pending Approval | Submitted | Student |
| Library Review | Submitted | Librarian |
| HOD Review | Submitted | Instructor |
| Approved | Submitted | Institute Admin |
| Rejected | Cancelled | Institute Admin |

**Transitions:**
| From State | Action | To State | Allowed Role |
|-----------|--------|----------|-------------|
| Pending Approval | Send for Library Review | Library Review | Student |
| Library Review | Approve | HOD Review | Librarian |
| Library Review | Reject | Rejected | Librarian |
| HOD Review | Approve | Approved | Instructor |
| HOD Review | Reject | Rejected | Instructor |

Once this workflow is active, students immediately see "NOC Application" in their available types.

---

## Files

### New Files
```
vidyaan/vidyaan/doctype/student_noc/__init__.py
vidyaan/vidyaan/doctype/student_noc/student_noc.json
vidyaan/vidyaan/doctype/student_noc/student_noc.py
vidyaan/vidyaan/doctype/student_request/__init__.py
vidyaan/vidyaan/doctype/student_request/student_request.json
vidyaan/vidyaan/doctype/student_request/student_request.py
vidyaan/api_folder/applications.py
frontend/pages/applications/index.vue        (rewritten)
frontend/pages/applications/TypeSelector.vue  (new)
frontend/pages/applications/NocModal.vue      (new)
frontend/pages/applications/RequestModal.vue  (new)
frontend/pages/applications/LeaveModal.vue    (new)
```

---

*Created: 2026-04-03*
