# Vidyaan Frontend Feature Backlog & Migration Plan

Based on the recent backend overhaul (transitioning to a Multi-Tenant SaaS architecture with `Company` routing and the OR-Tools Routine Generation engine), the current Nuxt 3 frontend needs significant updates. It still relies on the old "MaxEdu" naming and lacks the Institute Admin interfaces.

Here is the complete list of features and refactors needed to finalize the frontend.

## 1. Brand & API Migration (Urgent)
The frontend is currently pointing to old custom endpoints and uses old branding.
- [ ] **Rename Branding**: Replace all instances of `MaxEdu ERP` with `Vidyaan` (e.g., in `login.vue` SEO tags, text, and footers).
- [ ] **API Endpoint Migration**: Audit composables (e.g., `useUserProfile.js` pointing to `maxedu.api_folder.profile.get_user_info`). Rewrite these to use native Frappe endpoints (`/api/resource/` or `/api/method/frappe.auth.get_logged_user`) or create new `vidyaan` whitelisted methods.
- [ ] **Role Normalization**: Update `useUserProfile.js` to properly detect the new specific roles: `System Administrator`, `Institute Admin`, `Instructor`, and `Student`.

## 2. Multi-Tenant SaaS Alignment
Because the backend now uses strict `Company`-based isolation, the frontend must adapt.
- [ ] **User Context**: The profile state must expose the user's `Company` (Institute Name) to display in the header/navbar (e.g., *"Welcome back to Springfield High"*).
- [ ] **Institute Selection (Superadmin)**: If a `System Administrator` logs in, they need a UI dropdown to "Impersonate" or select a specific Institute (`Company`) to view.

## 3. Role-Based Dashboards
Currently, `index.vue` only routes to `StudentDashboard` or `TeacherDashboard`. We must build specific homepages for the new roles.
- [ ] **Institute Admin Dashboard**: 
  - Real-time stat cards (Total Students, Faculty, Courses, Programs) specific to their Institute.
  - Quick action widgets: "Generate Routine", "Admit Student", "Add Faculty".
- [ ] **System Admin Dashboard**: Global SaaS metrics (Total Institutes, Global Users, System Health).
- [ ] **Instructor Dashboard (Refactor)**: Adapt to pull upcoming classes from natively generated `Course Schedule` elements instead of old custom timetable endpoints.
- [ ] **Student Dashboard (Refactor)**: Display the student's personal schedule and LMS course access.

## 4. Academic Setup & Routine Generation UI (Institute Admin)
If the Institute Admin manages the school via the Nuxt frontend instead of Frappe Desk, we need forms for the new Doctypes.
- [ ] **Vidyaan Settings Manager**: A UI to set up default school days, constraint limits, and configure `Period Timings` (e.g., Period 1 = 09:00 - 09:45).
- [ ] **Instructor Capability Mapper**: When creating an Instructor, include a dynamic form to map which courses/programs they can teach (populates the `Instructor Course Mapping` child table).
- [ ] **Routine Generation Control Panel**:
  - **Configuration**: Multi-select for `Programs`, day toggles, constraint sliders.
  - **Live Readiness Check**: A button that calls the backend `check_readiness` method and displays the ✅/❌ validation HTML inside a Nuxt component.
  - **Solver Execution**: "Generate Routine" button with a loading state (which can take 10-30 seconds).
  - **Timetable Viewer**: A visual, grid-based calendar view of the `routine_slots` returned by the solver, with a "Submit/Publish" button to finalize it.

## 5. Core Education Module Management
- [ ] **Programs & Courses UI**: CRUD pages to define Classes (Programs), Subjects (Courses), and syllabus data (Topics/Articles).
- [ ] **Section / Student Group Manager**: UI to divide a Program (e.g., "Class 11 Science") into specific Sections (Student Groups) and assign students to them.
- [ ] **Admissions Flow**: A simplified wizard to create a `Student` profile and automatically generate their `Program Enrollment`.
- [ ] **Instructor Attendance UI**: A grid UI for teachers to quickly mark presence/absence for the students in their assigned `Student Group` during a scheduled period. 

## Summary 
The biggest missing pieces in the frontend are the **Institute Admin persona**, the **Routine Generation UX**, and the **MaxEdu -> Vidyaan nomenclature swap**. By implementing the above items, the frontend will fully match the new robust SaaS backend.
