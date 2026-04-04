# Implementation Plan: Unified Publication System

This plan describes the creation of a single, efficient `Publication` doctype that handles school notices, news, and general announcements. The implementation follows the "Single Doctype" architecture for minimal overhead and maximum scalability.

## User Review Required

> [!IMPORTANT]
> Since we are creating files directly without the `bench` command, you will need to run `bench migrate` once after the files are created to update the database schema and create the doctype in your Frappe site.

> [!NOTE]
> The "global" feature (`is_global`) is included as a checkbox for future inter-school filtering logic.

## Proposed Changes

### [Component] Core Publication Doctype

A unified doctype for all school communications.

#### [NEW] [publication.json](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/publication/publication.json)
- Define the `Publication` doctype with fields for `title`, `type`, `content`, `publish_date`, `is_global`, `target_type`, `target_student_group`, `featured_image`, `approval_type`, `approver_role`, `approver_user`, and `status`.
- Implement dynamic UI logic using `depends_on` for fields specific to `Notice` (targeting) and `News` (featured image).

#### [NEW] [publication.py](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/publication/publication.py)
- Implement `Publication` class with the following logic:
  - `validate()`: Calls type-specific validators (e.g., `validate_notice`).
  - `on_submit()`: Handles automatic assignment to the `approver_user` or `approver_role` if specified.

#### [NEW] [publication.js](file:///d:/frappe-bench/apps/vidyaan/vidyaan/vidyaan/doctype/publication/publication.js)
- Core client-side validations (if needed) and UI improvements.

### [Component] Automation & Hooks

#### [MODIFY] [hooks.py](file:///d:/frappe-bench/apps/vidyaan/vidyaan/hooks.py)
- Register the `on_submit` event for `Assessment Plan` to trigger the creation of a new `Publication`.

#### [NEW] [assessment_hooks.py](file:///d:/frappe-bench/apps/vidyaan/vidyaan/utils/assessment_hooks.py)
- Implement `create_assessment_publication(doc, method)` to automatically generate a `Notice`-type `Publication` whenever an `Assessment Plan` is submitted.

## Verification Plan

### Automated Tests
- `python -m unittest vidyaan.utils.test_assessment_hooks` (if we add tests).
- Manual code review of the generated JSON and Python files.

### Manual Verification
1. Create a `Publication` of type `Notice` and verify that targeting fields appear.
2. Create a `Publication` of type `News` and verify that the featured image field appears.
3. Submit an `Assessment Plan` and verify that a draft `Publication` is created.
4. Verify that assignments reach the correct users/roles.
