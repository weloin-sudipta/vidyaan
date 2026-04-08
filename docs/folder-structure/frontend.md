# Vidyaan Frontend Documentation

> **App Name:** Vidyaan School ERP
> **Framework:** Nuxt 4.3.1 + Vue 3.5.28 + Tailwind CSS
> **Backend:** Frappe Framework API
> **Location:** `apps/vidyaan/frontend/`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [Layouts & Navigation](#5-layouts--navigation)
6. [Feature Inventory — Implemented](#6-feature-inventory--implemented)
7. [Feature Inventory — Incomplete / Placeholder](#7-feature-inventory--incomplete--placeholder)
8. [Feature Inventory — Not Yet Built](#8-feature-inventory--not-yet-built)
9. [Composables Reference](#9-composables-reference)
10. [Components Reference](#10-components-reference)
11. [API Integration](#11-api-integration)
12. [Known Issues & Technical Debt](#12-known-issues--technical-debt)
13. [Roadmap & Priority Matrix](#13-roadmap--priority-matrix)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   NUXT 4 FRONTEND                        │
│                                                          │
│  Layouts ──► Pages ──► Components                        │
│                │                                         │
│          Middleware          Composables                  │
│      (auth + RBAC)      (state + API calls)              │
│                │                │                         │
│                └───── useFrappeFetch ─────┘               │
│                          │                               │
│                    POST /api/method/*                     │
│                    GET  /api/resource/*                   │
└──────────────────────────────────────────────────────────┘
                           │
                    Frappe Backend
                  (maxedu.api_folder.*)
```

**Key design decisions:**
- File-based routing (Nuxt convention)
- Composable-based state management (no Vuex/Pinia)
- `useState()` for SSR-safe global state (auth profile)
- `ref()` for local reactive state in composables
- Role-based route protection via two global middleware layers
- Cookie-based session auth (credentials: 'include')

---

## 2. Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Nuxt | 4.3.1 |
| UI | Vue | 3.5.28 |
| Styling | Tailwind CSS | 6.14.0 |
| Dark Mode | @nuxtjs/color-mode | 4.0.0 |
| Charts | ApexCharts | 5.10.0 |
| 3D Graphics | Three.js | 0.183.2 |
| Icons | Font Awesome | 7.0.1 |
| UI Components | Frappe-UI | 0.1.265 |
| PDF | jsPDF + html2canvas | dynamic import |
| Testing | Playwright | 1.58.2 |

---

## 3. Project Structure

```
frontend/
├── assets/              # Images, static assets
├── components/
│   ├── ui/              # Reusable UI primitives (19 components)
│   │   ├── AppModal.vue
│   │   ├── AppNavBar.vue
│   │   ├── AppSideBar.vue
│   │   ├── ConfirmDialog.vue   # Global confirmation dialog (paired with useConfirm)
│   │   ├── HeroHeader.vue
│   │   ├── StatCard.vue
│   │   ├── UiAvatar.vue
│   │   ├── UiBadge.vue
│   │   ├── UiButton.vue
│   │   ├── UiCard.vue
│   │   ├── UiEmptyState.vue
│   │   ├── UiInput.vue
│   │   ├── UiSearchFilterBar.vue
│   │   ├── UiSelect.vue
│   │   ├── UiSkeleton.vue
│   │   └── UiTextarea.vue
│   ├── applications/    # Application request modals
│   ├── dashboard/
│   │   ├── AdminDashboardView.vue
│   │   ├── StudentDashboardView.vue
│   │   ├── TeacherDashboardView.vue
│   │   ├── student/             # Student dashboard widgets (PascalCase)
│   │   │   ├── AcademicCalendar.vue
│   │   │   ├── Assignment.vue
│   │   │   ├── Attendance.vue
│   │   │   ├── BookRecommendation.vue
│   │   │   ├── CampusNotice.vue
│   │   │   ├── CurrentProgram.vue
│   │   │   ├── Event.vue
│   │   │   ├── PaymentHistory.vue
│   │   │   ├── StopWatch.vue
│   │   │   ├── TodayClass.vue
│   │   │   └── UpcomingExams.vue
│   │   └── teacher/             # Teacher dashboard widgets
│   │       ├── Announcements.vue
│   │       ├── AttendanceCard.vue
│   │       ├── DailyRoutine.vue
│   │       ├── GradingQueue.vue
│   │       └── TeacherDashboardPendingTasks.vue
│   ├── profile/         # Profile components (role-aware)
│   │   ├── ProfileForm.vue
│   │   ├── StudentProfileView.vue
│   │   └── TeacherProfileView.vue
│   ├── MaterialDetailsModal.vue
│   ├── StudyMaterialModal.vue
│   ├── ToastContainer.vue
│   └── TopicMaterialsModal.vue
├── composables/         # 29 composables organised into 7 subfolders
│   ├── api/
│   │   ├── parseFrappeError.ts  # Error extraction from _server_messages
│   │   ├── types.ts             # Shared API types
│   │   └── useFrappeFetch.ts   # Core API wrapper
│   ├── auth/
│   │   └── useAuth.ts
│   ├── academics/
│   │   ├── useAssignments.ts
│   │   ├── useAttendance.ts
│   │   ├── useCourseTopics.ts
│   │   ├── useEvents.ts
│   │   ├── useExaminations.ts
│   │   ├── useHolidays.ts
│   │   ├── useNotices.ts
│   │   ├── useStudyMaterials.ts
│   │   └── useTimetable.ts
│   ├── library/
│   │   ├── useBookRequest.ts
│   │   ├── useLibraryAdmin.ts
│   │   └── useLibraryBooks.ts
│   ├── student/
│   │   ├── useProfile.ts
│   │   ├── useStudent.ts
│   │   ├── useStudentDashboard.ts
│   │   └── useUserProfile.ts
│   ├── teacher/
│   │   ├── useFacultyMember.ts
│   │   ├── useGrading.ts
│   │   ├── useTeacherAssignments.ts
│   │   ├── useTeacherClasses.ts
│   │   ├── useTeacherDashboard.ts
│   │   └── useTeacherExams.ts
│   └── ui/
│       ├── useConfirm.ts        # Global confirm dialog
│       ├── usePdf.ts
│       └── useToast.ts
├── layouts/
│   ├── default.vue      # Main app (sidebar + navbar)
│   └── auth.vue         # Auth pages (centered, minimal)
├── middleware/
│   ├── auth.global.ts        # Login enforcement
│   └── role-based.global.ts  # RBAC enforcement
├── pages/               # 50+ route pages
│   ├── index.vue            # Redirects to /dashboard
│   ├── auth/
│   │   ├── login.vue
│   │   └── forgot-password.vue
│   ├── dashboard/
│   │   └── index.vue        # Role-aware unified dashboard (student/teacher/admin)
│   ├── academics/
│   │   ├── index.vue
│   │   ├── assignments.vue
│   │   ├── attendance.vue   # Unified: student view + teacher marking by role
│   │   ├── study-materials.vue
│   │   ├── subjects.vue
│   │   └── timetable.vue
│   ├── exam/
│   │   ├── schedule.vue
│   │   └── result.vue
│   ├── library/             # Student library pages
│   ├── teacher/             # Teacher-specific pages
│   │   ├── academics/
│   │   │   ├── assignments.vue
│   │   │   ├── attendance.vue
│   │   │   ├── lesson-planning.vue
│   │   │   └── my-classes.vue
│   │   ├── grading/
│   │   │   ├── mark-entry.vue
│   │   │   ├── performance.vue
│   │   │   └── report-cards.vue
│   │   ├── students/index.vue
│   │   └── applications.vue
│   ├── admin/               # Admin pages
│   │   ├── library/
│   │   └── students/
│   ├── profile/
│   │   ├── index.vue        # Role-aware profile (student/teacher)
│   │   ├── edit.vue
│   │   └── tabs/
│   ├── documents/           # Personal docs, fees, ID card
│   ├── applications/        # Leave/resource applications
│   ├── notices/             # Notice board + detail
│   ├── events.vue           # Event calendar
│   ├── faculty.vue          # Faculty directory
│   └── error/               # 404, 500, maintenance (Three.js)
├── utils/
│   └── pdf-templates/
│       └── certificate.html  # PDF certificate template
├── public/
├── app.vue              # Root — mounts <ConfirmDialog> globally
├── nuxt.config.ts
├── tailwind.config.ts
└── package.json
```

---

## 4. Authentication & Authorization

### Login Flow
1. User enters email + password at `/auth/login`
2. POST `/api/method/login` with credentials
3. Frappe sets session cookie
4. Frontend calls `loadProfile()` → fetches user info + role
5. Role normalized to lowercase → redirects to role dashboard

### Middleware Stack
| Middleware | File | Purpose |
|-----------|------|---------|
| `auth.global.ts` | `/middleware/` | Blocks unauthenticated access to all routes except `/auth/*` |
| `role-based.global.ts` | `/middleware/` | Enforces role-specific route access after auth |

### Role-Route Mapping
| Role | Allowed Routes |
|------|---------------|
| **Student** | `/academics/*`, `/exam/*`, `/applications`, `/library`, `/faculty`, `/profile`, `/notices/*`, `/events`, `/dashboard` |
| **Teacher** | `/teacher/*`, `/academics/attendance`, `/notices/*`, `/events`, `/library`, `/profile`, `/dashboard` |
| **Admin** | `/admin/*`, `/dashboard` |
| **Shared** | `/dashboard`, `/notices/*`, `/events` |

### Current Issues
- No `Institute Admin` or `System Administrator` route groups exist beyond basic `/admin/*`

---

## 5. Layouts & Navigation

### Layouts
- **`default.vue`** — Sidebar + Navbar + scrollable content area (used for all authenticated pages)
- **`auth.vue`** — Minimal centered layout for login/forgot-password

### Sidebar Navigation (`AppSideBar.vue`)
- Collapsible with icon-only mode
- Role-based menu items (auto-filtered)
- Active route highlighting with parent expansion
- ~374 lines

### Navbar (`AppNavBar.vue`)
- Global search (Ctrl+/) — **placeholder only, not functional**
- Notification bell — **hardcoded sample data**
- Dark mode toggle (Light/System/Dark)
- User avatar + profile dropdown

---

## 6. Feature Inventory — Implemented

Features that exist in the frontend with functional UI and API integration.

### Student Features

| Feature | Page | Composable | Status |
|---------|------|-----------|--------|
| Student Dashboard | `/dashboard/index.vue` (role-aware) | `student/useStudentDashboard.ts` | Working — welcome hero, stats |
| Subjects List | `/academics/subjects.vue` | — | Working |
| Study Materials | `/academics/study-materials.vue` | `academics/useStudyMaterials.ts` | Working — view/download |
| Assignments | `/academics/assignments.vue` | `academics/useAssignments.ts` | Working — view + submit with file upload |
| Timetable | `/academics/timetable.vue` | `academics/useTimetable.ts` | Working — weekly calendar view |
| Attendance Calendar | `/academics/attendance.vue` | `academics/useAttendance.ts` | Working — monthly view, stats, progress ring |
| Exam Schedule | `/exam/schedule.vue` | `academics/useExaminations.ts` | Working |
| Exam Results | `/exam/result.vue` | `academics/useExaminations.ts` | Working |
| Library Browse | `/library/tabs/allBooks.vue` | `library/useLibraryBooks.ts` | Working — search + filter |
| Library Issued Books | `/library/tabs/issuedBooks.vue` | `library/useLibraryBooks.ts` | Working |
| Library Requests | `/library/tabs/requestTracking.vue` | `library/useBookRequest.ts` | Working — request + cancel |
| Library Recommendations | `/library/tabs/recommendations.vue` | `library/useLibraryBooks.ts` | Working |
| Applications | `/applications/index.vue` | — | Working — submit + workflow tracking |
| Notices Board | `/notices/index.vue` | `academics/useNotices.ts` | Working — pinned carousel, filtering |
| Notice Detail | `/notices/[slug].vue` | `academics/useNotices.ts` | Working — dynamic slug route |
| Events Calendar | `/events.vue` | `academics/useEvents.ts` | Working — category filter, status tags |
| Faculty Directory | `/faculty.vue` | `teacher/useFacultyMember.ts` | Working |
| Profile View | `/profile/index.vue` | `student/useProfile.ts`, `student/useUserProfile.ts` | Working — role-aware tabbed interface |
| Profile Edit | `/profile/edit.vue` | `student/useProfile.ts` | Working — photo upload |
| Documents / ID Card | `/documents/*.vue` | — | Working |

### Teacher Features

| Feature | Page | Composable | Status |
|---------|------|-----------|--------|
| Teacher Dashboard | `/dashboard/index.vue` (role-aware) | `teacher/useTeacherDashboard.ts` | Working — schedule, tasks, calendar |
| Attendance Marking | `/academics/attendance.vue` (role-aware) | `academics/useAttendance.ts` | Working — calendar-based |
| Assignment Management | `/teacher/academics/assignments.vue` | `teacher/useTeacherAssignments.ts` | Working |
| Lesson Planning | `/teacher/academics/lesson-planning.vue` | — | Working |
| My Classes | `/teacher/academics/my-classes.vue` | `teacher/useTeacherClasses.ts` | Working |
| Mark Entry (Speed Grader) | `/teacher/grading/mark-entry.vue` | `teacher/useGrading.ts` | Working — exam selector + bulk save |
| Performance View | `/teacher/grading/performance.vue` | — | Working |
| Report Cards | `/teacher/grading/report-cards.vue` | — | Working |
| Student List | `/teacher/students/` | — | Working |
| Profile View | `/profile/index.vue` (role-aware) | `teacher/useFacultyMember.ts` | Working |

### Admin Features

| Feature | Page | Status |
|---------|------|--------|
| Library Inventory | `/admin/library/inventory.vue` | Working |
| Library Issuance | `/admin/library/issuance.vue` | Working |
| Student List | `/admin/students/student_list.vue` | Working |

### Shared/UI Features

| Feature | Location | Status |
|---------|----------|--------|
| Dark Mode (3-way) | AppNavBar | Working — Light/System/Dark |
| Toast Notifications | ToastContainer.vue | Working |
| Loading Skeletons | UiSkeleton.vue | Working |
| Responsive Layout | All pages | Working |
| 404 Error Page (Three.js Solar System) | `/error/404.vue` | Working |
| 500 Error Page (Three.js Animation) | `/error/500.vue` | Working |
| Maintenance Page | `/error/maintenance.vue` | Working |

---

## 7. Feature Inventory — Incomplete / Placeholder

Features that have UI elements but are NOT fully functional.

| Feature | Location | What Exists | What's Missing |
|---------|----------|-------------|----------------|
| **Global Search** | `AppNavBar.vue` | Search bar with Ctrl+/ shortcut | No search logic, no results, purely cosmetic |
| **Notifications** | `AppNavBar.vue` | Bell icon, badge, dropdown with items | Hardcoded sample data, no backend integration |
| **Forgot Password** | `/auth/forgot-password.vue` | Email + OTP form fields | OTP flow likely incomplete, needs backend verification |
| **Teacher Announcements** | `dashboard/Announcements.vue` | Textarea for posting announcements | No submit handler, no backend call |
| **Social Login (Google/Microsoft)** | `/auth/login.vue` | Buttons exist in code | Commented out, not connected |
| **Admin Dashboard** | `/dashboard/index.vue` (admin role) | Role-aware page renders admin view | Minimal implementation, no stats or widgets |
| **PDF Resume Download** | `/profile/index.vue` | jsPDF + html2canvas logic | May have edge cases, dynamic import complexity |
| **Event Filtering** | `/events.vue` | activeFilter ref, filter buttons | Filter may not be fully wired to API |
| **404 Page Navigation** | `/error/404.vue` | goBack() function | Commented out |

---

## 8. Feature Inventory — Not Yet Built

Features that the backend supports or the project requires, but have NO frontend implementation.

### Critical — Must Build (from BACKLOG.md FE-001 to FE-004)

| Feature | Priority | Description |
|---------|----------|-------------|
| **Rebrand MaxEdu → Vidyaan** | P0 | All references to "MaxEdu ERP" must become "Vidyaan". Includes page titles, sidebar header, login page, favicon, meta tags |
| **API Endpoint Migration** | P0 | Composables use `maxedu.api_folder.*` endpoints — must migrate to native Frappe API patterns (`/api/resource/*`, `/api/method/vidyaan.*`) |
| **Role Name Migration** | P0 | Middleware uses `student`/`teacher` — must update to `Student`, `Instructor`, `Institute Admin`, `System Administrator` |
| **Institute Admin Dashboard** | P1 | Full admin dashboard with institute stats, quick actions, exam management, publication management |

### High Priority — Backend Ready, Frontend Needed

| Feature | Backend Status | Frontend Needed |
|---------|---------------|----------------|
| **Routine/Timetable Generation UI** | OR-Tools solver fully working | Program selector, constraint sliders, readiness checker, generated timetable viewer, publish button |
| **Vidyaan Settings Manager** | `Vidyaan Settings` doctype exists | Admin UI to configure period timings, routine defaults |
| **Instructor-Course Mapping UI** | Child table on Instructor doctype | Admin UI to assign courses/programs to instructors |
| **Publication Management (Admin)** | Publication doctype with workflow | Admin CRUD for notices/news/announcements, approval queue |
| **Admit Card Viewing** | Jinja print format exists | Student page to view/download admit cards for upcoming exams |
| **System Administrator Dashboard** | Multi-tenant SaaS ready | Global metrics, institute list, impersonation |

### Medium Priority — Enhancements

| Feature | Description |
|---------|-------------|
| **Real Notification System** | Replace hardcoded data with backend push/poll notifications |
| **Global Search** | Implement actual search across pages/content |
| **Fee Management** | Fee structure display, payment status, receipts |
| **Quick Attendance Grid** | Teacher-facing bulk attendance marking (grid, not calendar) |
| **Student Report Card PDF** | Generate weighted report cards as PDF |
| **Programs & Courses CRUD** | Admin pages for managing academic programs/courses |
| **Student Group Manager** | Manage sections and student groupings |
| **Admissions/Enrollment Wizard** | Program enrollment flow for new students |

### Low Priority — Future Features

| Feature | Description |
|---------|-------------|
| Inter-school Material Sharing | Share study materials across institutes |
| Room Assignment in Timetable | Room solver integration in routine generation |
| SMS/Email Notifications | Automated notification delivery |
| Parent Portal | Separate login and dashboard for parents |
| LMS Integration | Topic/Article-based learning content |

---

## 9. Composables Reference

All composables live under `frontend/composables/` (plural) and are auto-imported
by Nuxt 4. They are organised into 7 subfolders.

### api/ — Core API layer
| Composable | File | Purpose |
|-----------|------|---------|
| `useFrappeFetch` | `api/useFrappeFetch.ts` | API wrapper — `createResource()`, `createListResource()`, `call()`, `callMultipart()`, `auth.*`. Surfaces real Frappe errors from `_server_messages`. |
| `parseFrappeError` | `api/parseFrappeError.ts` | Extracts human-readable message from Frappe error envelopes |
| _(types)_ | `api/types.ts` | Shared API type definitions (`FrappeFetchError`, envelopes, etc.) |

### auth/ — Authentication
| Composable | File | Purpose |
|-----------|------|---------|
| `useAuth` | `auth/useAuth.ts` | `login()`, `logout()` — wraps Frappe auth endpoints |

### academics/ — Academic features
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useAssignments` | `academics/useAssignments.ts` | `vidyaan.api_folder.assignments.*` |
| `useAttendance` | `academics/useAttendance.ts` | `vidyaan.api_folder.attendance.*` |
| `useCourseTopics` | `academics/useCourseTopics.ts` | `vidyaan.api_folder.subjects.*` |
| `useEvents` | `academics/useEvents.ts` | `vidyaan.api_folder.event.get_all_events` |
| `useExaminations` | `academics/useExaminations.ts` | `vidyaan.api_folder.exam.*` |
| `useHolidays` | `academics/useHolidays.ts` | — |
| `useNotices` | `academics/useNotices.ts` | `vidyaan.api_folder.notices.*` |
| `useStudyMaterials` | `academics/useStudyMaterials.ts` | `vidyaan.api_folder.study_materials.*` |
| `useTimetable` | `academics/useTimetable.ts` | `vidyaan.api_folder.schedule.*` |

### library/ — Library management
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useBookRequest` | `library/useBookRequest.ts` | `vidyaan.library.api.request_book/cancel_request` |
| `useLibraryAdmin` | `library/useLibraryAdmin.ts` | `vidyaan.library.api.*` (admin ops) |
| `useLibraryBooks` | `library/useLibraryBooks.ts` | `vidyaan.library.api.get_catalog/get_my_issues/get_my_requests` |

### student/ — Student-specific
| Composable | File | Purpose |
|-----------|------|---------|
| `useProfile` | `student/useProfile.ts` | Student profile data and photo upload |
| `useStudent` | `student/useStudent.ts` | Student record helpers |
| `useStudentDashboard` | `student/useStudentDashboard.ts` | Student dashboard stats |
| `useUserProfile` | `student/useUserProfile.ts` | Global SSR-safe auth state — profile, role, isAuthenticated |

### teacher/ — Teacher-specific
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useFacultyMember` | `teacher/useFacultyMember.ts` | `vidyaan.api_folder.faculty.*` |
| `useGrading` | `teacher/useGrading.ts` | `vidyaan.api_folder.teacher_grading.*` |
| `useTeacherAssignments` | `teacher/useTeacherAssignments.ts` | `vidyaan.api_folder.assignments.*` (instructor ops) |
| `useTeacherClasses` | `teacher/useTeacherClasses.ts` | `vidyaan.api_folder.teachers_classes.*` |
| `useTeacherDashboard` | `teacher/useTeacherDashboard.ts` | `vidyaan.api_folder.teacher_data.*` |
| `useTeacherExams` | `teacher/useTeacherExams.ts` | `vidyaan.api_folder.teacher_grading.*` |

### ui/ — UI utilities
| Composable | File | Purpose |
|-----------|------|---------|
| `useConfirm` | `ui/useConfirm.ts` | Global confirmation dialog — `confirm(message, options)` resolves a Promise; paired with `<ConfirmDialog>` in `app.vue` |
| `usePdf` | `ui/usePdf.ts` | PDF generation (jsPDF + html2canvas) |
| `useToast` | `ui/useToast.ts` | Toast notification queue |

---

## 10. Components Reference

### UI Primitives (`/components/ui/`)
| Component | Purpose |
|-----------|---------|
| `AppSideBar.vue` | Collapsible sidebar with role-based nav |
| `AppNavBar.vue` | Top bar — search, notifications, dark mode, profile |
| `AppModal.vue` | Modal dialog |
| `ConfirmDialog.vue` | Global confirmation modal — mounted once in `app.vue`, driven by `useConfirm()` |
| `HeroHeader.vue` | Page header with icon + search |
| `StatCard.vue` | Statistics display card |
| `UiAvatar.vue` | User avatar with fallback initials |
| `UiBadge.vue` | Status/label badge |
| `UiButton.vue` | Styled button with variants (primary, secondary, danger, ghost) |
| `UiCard.vue` | Generic card wrapper |
| `UiEmptyState.vue` | Empty state illustration + message |
| `UiInput.vue` | Styled text input with label and error slot |
| `UiSearchFilterBar.vue` | Combined search + filter bar |
| `UiSelect.vue` | Styled select dropdown |
| `UiSkeleton.vue` | Loading skeleton placeholder |
| `UiTextarea.vue` | Styled multi-line text input |

### Dashboard Components (`/components/dashboard/`)
| Component | Purpose |
|-----------|---------|
| `StudentDashboardView.vue` | Student dashboard shell |
| `TeacherDashboardView.vue` | Teacher dashboard shell |
| `AdminDashboardView.vue` | Admin dashboard shell |
| `student/AcademicCalendar.vue` | Academic calendar widget |
| `student/Assignment.vue` | Assignment summary widget |
| `student/Attendance.vue` | Attendance ring + stats widget |
| `student/BookRecommendation.vue` | Book recommendation widget |
| `student/CampusNotice.vue` | Latest notices widget |
| `student/CurrentProgram.vue` | Enrolled program display |
| `student/Event.vue` | Upcoming events widget |
| `student/PaymentHistory.vue` | Fee payment history widget |
| `student/StopWatch.vue` | Study timer widget |
| `student/TodayClass.vue` | Today's class schedule widget |
| `student/UpcomingExams.vue` | Upcoming exams widget |
| `teacher/Announcements.vue` | Announcement post box (incomplete) |
| `teacher/AttendanceCard.vue` | Attendance summary card |
| `teacher/DailyRoutine.vue` | Teacher daily schedule widget |
| `teacher/GradingQueue.vue` | Assignments pending grading |
| `teacher/TeacherDashboardPendingTasks.vue` | Pending task list |

### Profile Components (`/components/profile/`)
| Component | Purpose |
|-----------|---------|
| `ProfileForm.vue` | Shared profile edit form |
| `StudentProfileView.vue` | Student profile layout with tabs |
| `TeacherProfileView.vue` | Teacher profile layout |

### Feature Components
| Component | Purpose |
|-----------|---------|
| `StudyMaterialModal.vue` | Add/edit study material |
| `MaterialDetailsModal.vue` | View material details |
| `TopicMaterialsModal.vue` | Materials list under a topic |
| `ToastContainer.vue` | Toast notification renderer |
| `applications/NewRequestModal.vue` | Create application/leave request |

---

## 11. API Integration

### API Wrapper (`composables/api/useFrappeFetch.ts`)

```
createResource(options)         → POST /api/method/{method} with params
createListResource(doctype)     → GET /api/resource/{doctype} with filters
createDocumentResource(dt, n)   → GET /api/resource/{doctype}/{name}
call<T>(method, params)         → POST /api/method/{method}
callMultipart<T>(method, file)  → POST /api/method/{method} (multipart/form-data)
auth.login(email, password)     → POST /api/method/login
auth.logout()                   → POST /api/method/logout
auth.getLoggedUser()            → GET /api/method/frappe.auth.get_logged_user
```

**Error extraction:** `parseFrappeError.ts` pulls real messages out of Frappe's
`_server_messages` JSON envelope so the UI shows the actual validation message
instead of a generic HTTP error.

### All Backend Endpoints Currently Used

| Endpoint | Called From | Purpose |
|----------|-----------|---------|
| `vidyaan.api_folder.profile.get_user_info` | useUserProfile | Load auth profile |
| `vidyaan.api_folder.assignments.get_student_assignments` | useAssignments | Student assignments |
| `vidyaan.api_folder.assignments.submit_student_assignment` | useAssignments | Submit with file |
| `vidyaan.api_folder.attendance.get_attendance` | useAttendance | Calendar data |
| `vidyaan.api_folder.attendance.get_attendance_summary` | useAttendance | Stats |
| `vidyaan.api_folder.exam.get_exams` | useExaminations | Exam schedule |
| `vidyaan.api_folder.exam.get_results` | useExaminations | Results |
| `vidyaan.api_folder.teacher_grading.get_my_exams` | useTeacherExams | Teacher exams |
| `vidyaan.api_folder.teacher_data.get_my_profile` | useTeacherDashboard | Teacher info |
| `vidyaan.api_folder.teacher_data.get_teacher_pending_tasks` | useTeacherDashboard | Pending tasks |
| `vidyaan.api_folder.teachers_classes.get_my_classes` | useTeacherClasses | Schedule |
| `vidyaan.api_folder.teacher_grading.get_exam_students` | useGrading | Grading plan |
| `vidyaan.api_folder.teacher_grading.submit_exam_results` | useGrading | Save marks |
| `vidyaan.api_folder.event.get_all_events` | useEvents | Events |
| `vidyaan.library.api.get_catalog` | useLibraryBooks | All books |
| `vidyaan.library.api.get_my_issues` | useLibraryBooks | Borrowed books |
| `vidyaan.library.api.get_my_requests` | useLibraryBooks | Requests |
| `vidyaan.library.api.get_book_recommendations` | useLibraryBooks | Recommendations |
| `vidyaan.library.api.request_book` | useBookRequest | Request book |
| `vidyaan.library.api.cancel_request` | useBookRequest | Cancel request |
| `vidyaan.api_folder.notices.get_approved_notices` | useNotices | Notices |
| `vidyaan.api_folder.notices.get_notice` | useNotices | Notice detail |
| `/api/method/upload_file` | useAssignments | File upload (Frappe core multipart) |

---

## 12. Known Issues & Technical Debt

### Critical
| Issue | Description |
|-------|-------------|
| **Wrong branding** | Some UI text still says "MaxEdu ERP" — should be "Vidyaan" |
| **No Institute Admin routes** | No dedicated pages or dashboard for Institute Admin role |
| **No System Admin routes** | No SaaS admin dashboard |

### Medium
| Issue | Description |
|-------|-------------|
| **Hardcoded notification data** | Navbar notifications are fake/sample data |
| **Global search not functional** | Search bar is cosmetic only |
| **Announcements can't be posted** | No submit handler in Announcements component |
| **Social login commented out** | Google/Microsoft buttons disabled |
| **StudyMaterialModal is large** | Should be broken into sub-components |

### Low
| Issue | Description |
|-------|-------------|
| Playwright in dependencies not devDependencies | Move to devDependencies |
| Some commented-out code | Error page navigation, social login |
| 404 goBack() disabled | Commented out in error page |

---

## 13. Roadmap & Priority Matrix

### Phase 1 — Critical Fixes (Must do first)

| # | Task | Effort | Files Affected |
|---|------|--------|---------------|
| 1.1 | Complete Vidyaan branding (remaining UI text) | Low | login.vue, AppSideBar.vue, page titles |
| 1.2 | Implement Institute Admin dashboard | High | New pages under `/admin/` |
| 1.3 | Implement System Administrator dashboard | High | New pages + role route group |

### Phase 2 — Missing Dashboards & Admin

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 2.1 | Institute Admin Dashboard | Medium | Stats, quick actions, publications queue, exam oversight |
| 2.2 | System Administrator Dashboard | Medium | Global SaaS metrics, institute list, impersonation |
| 2.3 | Vidyaan Settings page | Low | Period timings config, routine defaults |
| 2.4 | Instructor-Course Mapping UI | Low | Admin assigns courses/programs to teachers |

### Phase 3 — Backend-Ready Features Needing Frontend

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 3.1 | Routine Generation Control Panel | High | Program selector, constraints, readiness check, solver trigger, timetable viewer |
| 3.2 | Publication Management (CRUD) | Medium | Create/edit/delete notices + news + announcements, approval queue |
| 3.3 | Admit Card Viewer | Low | Student page to view/print admit cards |
| 3.4 | Real Notification System | Medium | Backend notifications replacing hardcoded data |
| 3.5 | Working Global Search | Medium | Search across students, courses, notices, events |

### Phase 4 — Feature Enhancements

| # | Task | Effort | Description |
|---|------|--------|-------------|
| 4.1 | Fee Management Pages | Medium | Fee structure, payment status, receipts, history |
| 4.2 | Quick Attendance Grid | Low | Teacher bulk attendance (grid, not calendar) |
| 4.3 | Programs & Courses CRUD | Medium | Admin management pages |
| 4.4 | Student Group Manager | Low | Section management UI |
| 4.5 | Enrollment Wizard | Medium | Admissions + program enrollment flow |
| 4.6 | Report Card PDF Generation | Medium | Weighted report cards as downloadable PDF |

### Phase 5 — Future Features

| # | Task | Effort |
|---|------|--------|
| 5.1 | Parent Portal (separate role + dashboard) | High |
| 5.2 | LMS Content (Topics/Articles) | High |
| 5.3 | Inter-school Material Sharing | Medium |
| 5.4 | Room Assignment in Timetable | Low |
| 5.5 | SMS/Email Notification Delivery | Medium |
| 5.6 | Google/Microsoft Social Login | Low |

---

## Summary Counts

| Category | Count |
|----------|-------|
| Implemented features (functional) | **33** |
| Incomplete / placeholder features | **8** |
| Not yet built (backend ready) | **6** |
| Not yet built (needs backend + frontend) | **12** |
| Composables | **29** |
| Components | **~41** |
| Pages/Routes | **~50** |
| Known issues / tech debt items | **8** |

---

*Last updated: 2026-04-08*