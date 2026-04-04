# Publication System

The **Publication** system is a unified feature for creating and managing all school-related communications, including Notices, News updates, and General Announcements.

## Features

- **Notice**: Formal school announcements (e.g., Exam Schedule, Sports Meet).
  - Supports targeting specific **Student Groups** or all students.
- **News**: One-time publications for school achievements, blogs, or newsletters. 
  - Supports **Featured Images**.
- **Announcement**: Quick, general updates with minimal overhead.
- **Approval Workflow**: Integrated multi-role approval system (By User or By Role).
- **Automation**: Automated Notice generation for newly submitted **Assessment Plans**.

## Workflow

1. **Creation**: A `Publication` is created as a **Draft**.
2. **Approval Assignment**: Upon submission, the publication is automatically assigned to the designated **Approver Role** or **Approver User**.
3. **Review**: Approvers see an assignment on their dashboard.
4. **Finalization**: Once approved, the status is updated, and the publication becomes active/visible.

## Technical Details

- **Doctype**: `Publication` (Submittable)
- **Module**: Vidyaan
- **Key Fields**:
  - `type`: Select (Notice, News, Announcement)
  - `is_global`: Future-proof flag for inter-school visibility.
  - `target_student_group`: Link to a specific group of students.
- **Hooks**:
  - `Assessment Plan (on_submit)` -> `vidyaan.utils.create_assessment_publication`: Triggers an automated notice.

## How to use

### Manually create a Notice
1. Navigate to **Publication List**.
2. Click **New**.
3. Set **Type** to `Notice`.
4. Enter the **Title** and **Content**.
5. Select a **Target Student Group**.
6. Set the **Approver Role** (e.g., Principal).
7. Save and Submit.

### Automated Notice
When an **Assessment Plan** is submitted, a new `Publication` of type `Notice` is automatically generated in **Draft** state, pre-targeted to the student group associated with the assessment.
