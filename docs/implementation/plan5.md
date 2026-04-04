# Implementation Plan: Dynamic Application System

This plan outlines the implementation of a flexible, unified system for various school applications (Leave, Requests, etc.) with support for multi-level, multi-role approvals.

## User Review Required

> [!IMPORTANT]
> To support dynamic fields without creating separate doctypes, we will use a **Key-Value child table** approach. This allows admins to define what data is needed for each application type without changing the database schema.

> [!NOTE]
> The approval logic will leverage Frappe's native **Workflow** system where possible, but use a custom "Next Step" logic to handle dynamic roles defined in the application configuration.

## Proposed Changes

### [Component] Metadata & Configuration

#### [NEW] [application_config.json](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application_config/application_config.json)
- **Fields**:
  - `name` (Data): Unique identifier (e.g., "Student Leave").
  - `fields` (Table: `Application Field Config`): Defines the inputs needed (Label, Type, Required).
  - `workflow_steps` (Table: `Application Step Config`): Defines approval levels and which roles can approve at each level.

#### [NEW] [application_field_config.json](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application_field_config/application_field_config.json)
- Child table to store field definitions for an `Application Config`.

#### [NEW] [application_step_config.json](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application_step_config/application_step_config.json)
- Child table to store approval steps (e.g., Step 1: HOD, Step 2: Principal).

### [Component] Application Entry

#### [NEW] [application.json](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application/application.json)
- **Fields**:
  - `application_config` (Link: `Application Config`): The template to use.
  - `applicant` (Link: `User`): Automatically set to current user.
  - `application_data` (Table: `Application Data`): Stores the user's inputs.
  - `current_step` (Int): Tracks the current approval level.
  - `status` (Select): `Draft`, `Pending Approval`, `Approved`, `Rejected`.

#### [NEW] [application_data.json](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application_data/application_data.json)
- Child table to store `label` and `value` (as Small Text).

### [Component] Logic & UI

#### [NEW] [application.js](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application/application.js)
- When `application_config` is selected:
  - Fetch field definitions from metadata.
  - Auto-populate the `application_data` table with the required labels.
  - (Optional) Render a cleaner UI using `frappe.ui.FieldGroup` overlay.

#### [NEW] [application.py](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/application/application.py)
- `validate()`: Check that all required fields (defined in config) have values in the data table.
- `on_submit()`: Logic to initiate the first approval level.
- `approve()`: Custom method to move to the next step based on the `Application Config`.

## Open Questions

> [!IMPORTANT]
> 1. Should we use the standard **Workflow** doctype (which requires defining a state machine per application) or a **Custom Sequential Approval** system built into the `Application` doctype itself?
> 2. For the "multiple roles" at one level (e.g., HOD and Asst. HOD), is it sufficient that **any one** of them approves to move to the next level?

## Verification Plan

### Manual Verification
1. Create an `Application Config` for "Late Entry" with fields: "Reason", "Arrival Time" and Steps: "HOD", "Security".
2. Log in as a Student and create an `Application` for "Late Entry".
3. Verify that the "Targeting" section correctly contains the "Reason" field.
4. Verify that an HOD can see and approve the request, moving it to the "Security" step.
