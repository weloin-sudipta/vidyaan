# Vidyaan Frontend Documentation

> **App Name:** MaxEdu | Student ERM (needs rebranding to Vidyaan)
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
│   ├── ui/              # Reusable UI primitives (11 components)
│   ├── applications/    # Application request modals
│   ├── dashboard/       # Dashboard widgets (teacher)
│   ├── profile/         # Profile edit form
│   ├── BookCard.vue
│   ├── BookRecommendation.vue
│   ├── StudyMaterialModal.vue
│   └── ToastContainer.vue
├── composable/          # 31 composables (state + API)
├── layouts/
│   ├── default.vue      # Main app (sidebar + navbar)
│   └── authLayout.vue   # Auth pages (centered, minimal)
├── middleware/
│   ├── auth.global.js        # Login enforcement
│   └── role-based.global.js  # RBAC enforcement
├── pages/               # ~31 route pages
│   ├── auth/            # Login, forgot password
│   ├── dashboard/       # Student, teacher, admin dashboards
│   ├── academics/       # Subjects, materials, assignments, timetable
│   ├── exam/            # Schedule, results
│   ├── library/         # Books, requests, recommendations
│   ├── teacher/         # Teacher-specific pages
│   ├── admin/           # Admin pages
│   ├── profile/         # Profile with tabs
│   ├── documents/       # Personal docs, fees, ID card
│   ├── applications/    # Leave/resource applications
│   ├── notices/         # Notice board + detail
│   ├── events.vue       # Event calendar
│   ├── faculty.vue      # Faculty directory
│   └── error/           # 404, 500, maintenance (Three.js)
├── public/
├── templates/
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
| `auth.global.js` | `/middleware/` | Blocks unauthenticated access to all routes except `/auth/*` |
| `role-based.global.js` | `/middleware/` | Enforces role-specific route access after auth |

### Role-Route Mapping
| Role | Allowed Routes |
|------|---------------|
| **Student** | `/academics/*`, `/attendance`, `/exam/*`, `/applications`, `/library`, `/faculty`, `/profile`, `/notices/*`, `/events` |
| **Teacher** | `/teacher/*`, `/notices/*`, `/events`, `/library` |
| **Admin** | `/admin/*` (minimal) |
| **Shared** | `/`, `/notices/*`, `/events` |

### Current Issues
- Roles use old names (student/teacher) — need migration to Vidyaan roles: `Student`, `Instructor`, `Institute Admin`, `System Administrator`
- No `Institute Admin` or `System Administrator` route groups exist

---

## 5. Layouts & Navigation

### Layouts
- **`default.vue`** — Sidebar + Navbar + scrollable content area (used for all authenticated pages)
- **`authLayout.vue`** — Minimal centered layout for login/forgot-password

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
| Student Dashboard | `/dashboard/student.vue` | `userDashboard.ts` | Working — welcome hero, stats |
| Subjects List | `/academics/subjects.vue` | — | Working |
| Study Materials | `/academics/study-materials.vue` | `useStudyMaterials.js` | Working — view/download |
| Assignments | `/academics/assignments.vue` | `useAssignments.js` | Working — view + submit with file upload |
| Timetable | `/academics/timetable.vue` | `useTimetable.js` | Working — weekly calendar view |
| Attendance Calendar | `/attendance.vue` | `useAttendance.js`, `useAttendanceSummary.js` | Working — monthly view, stats, progress ring |
| Exam Schedule | `/exam/schedule.vue` | `useExaminations.js` | Working |
| Exam Results | `/exam/result.vue` | `useExaminations.js` | Working |
| Library Browse | `/library/tabs/allBooks.vue` | `useLibraryBooks.js` | Working — search + filter |
| Library Issued Books | `/library/tabs/issuedBooks.vue` | `useBorrowedBooks.js` | Working |
| Library Requests | `/library/tabs/requestTracking.vue` | `useBookRequest.js` | Working — request + cancel |
| Library Recommendations | `/library/tabs/recommendations.vue` | `useLibraryBooks.js` | Working |
| Applications | `/applications/index.vue` | `useAllWorkFlow.js`, `useLeaveApplication.js` | Working — submit + workflow tracking |
| Notices Board | `/notices/index.vue` | `useNotices.js` | Working — pinned carousel, filtering |
| Notice Detail | `/notices/[slug].vue` | `useNotices.js` | Working — dynamic slug route |
| Events Calendar | `/events.vue` | `useEvents.js` | Working — category filter, status tags |
| Faculty Directory | `/faculty.vue` | `useFacultyMember.js` | Working |
| Profile View | `/profile/index.vue` | `useProfile.js`, `useUserProfile.js` | Working — tabbed interface |
| Profile Edit | `/profile/edit.vue` | `useProfile.js` | Working — photo upload |
| Documents / ID Card | `/documents/*.vue` | — | Working |

### Teacher Features

| Feature | Page | Composable | Status |
|---------|------|-----------|--------|
| Teacher Dashboard | `/dashboard/teacher.vue` | `useTeacherDashboard.js` | Working — schedule, tasks, calendar |
| Attendance Marking | `/teacher/academics/attendance.vue` | — | Working — calendar-based |
| Assignment Management | `/teacher/academics/assignments.vue` | `useTeacherAssignments.js` | Working |
| Lesson Planning | `/teacher/academics/lesson-planning.vue` | — | Working |
| My Classes | `/teacher/academics/my-classes.vue` | `useTeacherClasses.js` | Working |
| Mark Entry (Speed Grader) | `/teacher/grading/mark-entry.vue` | `useGreading.js` | Working — exam selector + bulk save |
| Performance View | `/teacher/grading/performance.vue` | — | Working |
| Report Cards | `/teacher/grading/report-cards.vue` | — | Working |
| Student List | `/teacher/students/` | — | Working |
| Teacher Profile | `/teacher/profile.vue` | — | Working |

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
| **Forgot Password** | `/auth/forget-password.vue` | Email + OTP form fields | OTP flow likely incomplete, needs backend verification |
| **Teacher Announcements** | `dashboard/Announcements.vue` | Textarea for posting announcements | No submit handler, no backend call |
| **Social Login (Google/Microsoft)** | `/auth/login.vue` | Buttons exist in code | Commented out, not connected |
| **Admin Dashboard** | `/dashboard/admin.vue` | Page exists | Minimal implementation, no stats or widgets |
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
| **Quick Attendance Grid** | Teacher-facing bulk attendance marking (not calendar) |
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

### Core / Auth
| Composable | File | Purpose |
|-----------|------|---------|
| `useFrappeFetch` | `useFrappeFetch.ts` | API wrapper — `createResource()`, `createListResource()`, `call()`, `auth.*` |
| `useAuth` | `useAuth.js` | `login()`, `logout()` functions |
| `useUserProfile` | `useUserProfile.js` | Global SSR-safe auth state — profile, role, isAuthenticated |

### Student
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useAssignments` | `useAssignments.js` | `maxedu.api_folder.assignments.*` |
| `useAttendance` | `useAttendance.js` | `maxedu.api_folder.attendance.get_attendance` |
| `useAttendanceSummary` | `useAttendanceSummary.js` | `maxedu.api_folder.attendance.get_attendance_summary` |
| `useExaminations` | `useExaminations.js` | `maxedu.api_folder.exam.*` |
| `useAdmitCard` | `useAdmitCard.js` | — |
| `useCourseTopics` | `useCourseTopics.js` | — |
| `useStudent` | `useStudent.js` | — |
| `useStudyMaterials` | `useStudyMaterials.js` | — |
| `useTimetable` | `useTimetable.js` | — |
| `useProfile` | `useProfile.js` | — |
| `userDashboard` | `userDashboard.ts` | — |

### Teacher
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useTeacherDashboard` | `useTeacherDashboard.js` | `maxedu.api_folder.teacher_data.*` |
| `useTeacherAssignments` | `useTeacherAssignments.js` | — |
| `useTeacherClasses` | `useTeacherClasses.js` | `maxedu.api_folder.classes.get_my_schedule` |
| `useTeacherExams` | `useTeacherExams.js` | `maxedu.api_folder.exam.get_teacher_exams` |
| `useGreading` | `useGreading.js` | `maxedu.api_folder.grading.*` |

### Library
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useLibraryBooks` | `useLibraryBooks.js` | `maxedu.library_management.api.*` |
| `useBorrowedBooks` | `useBorrowedBooks.js` | `maxedu.library_management.api.get_my_issues` |
| `useBookRequest` | `useBookRequest.js` | `maxedu.library_management.api.request_book/cancel_request` |
| `useLibraryMember` | `useLibraryMember.js` | — |

### Shared
| Composable | File | API Endpoint |
|-----------|------|-------------|
| `useNotices` | `useNotices.js` | `maxedu.desk_approval.doctype.application.application.*` |
| `useEvents` | `useEvents.js` | `maxedu.api_folder.event.get_all_events` |
| `useFacultyMember` | `useFacultyMember.js` | — |
| `useHolidays` | `useHolidays.js` | — |
| `useAllWorkFlow` | `useAllWorkFlow.js` | — |
| `useLeaveApplication` | `useLeaveApplication.js` | — |

### Utilities
| Composable | File | Purpose |
|-----------|------|---------|
| `useToast` | `useToast.js` | Toast notification queue |
| `usePdf` | `usePdf.js` | PDF generation (jsPDF + html2canvas) |

---

## 10. Components Reference

### UI Primitives (`/components/ui/`)
| Component | Purpose | Lines |
|-----------|---------|-------|
| `AppSideBar.vue` | Collapsible sidebar with role-based nav | ~374 |
| `AppNavBar.vue` | Top bar — search, notifications, dark mode, profile | ~137 |
| `DataTable.vue` | Reusable table with sort/filter | — |
| `AppModal.vue` | Modal dialog v1 | — |
| `AppModal2.vue` | Modal dialog v2 | — |
| `HeroHeader.vue` | Page header with icon + search | — |
| `StatCard.vue` | Statistics display card | — |
| `UiCard.vue` | Generic card wrapper | — |
| `UiSkeleton.vue` | Loading skeleton placeholder | — |
| `UiStatusBadge.vue` | Status indicator badge | — |
| `AppLoader.vue` | Loading spinner | — |

### Feature Components
| Component | Purpose |
|-----------|---------|
| `BookCard.vue` | Library book display card |
| `BookRecommendation.vue` | Recommendation item |
| `StudyMaterialModal.vue` | Add/edit study material (large — 13K+ lines) |
| `ToastContainer.vue` | Toast notification renderer |
| `applications/NewRequestModal.vue` | Create application/leave request |
| `dashboard/DailyRoutine.vue` | Teacher daily schedule widget |
| `dashboard/TeacherDashboardPendingTasks.vue` | Pending task list |
| `dashboard/Announcements.vue` | Announcement post box (incomplete) |
| `dashboard/academicCalendar.vue` | Calendar widget |
| `dashboard/campusNotice.vue` | Notice sidebar widget |
| `profile/ProfileForm.vue` | Profile edit form |

---

## 11. API Integration

### API Wrapper (`useFrappeFetch.ts`)

```
createResource(options)       → POST /api/method/{method} with params
createListResource(doctype)   → GET /api/resource/{doctype} with filters
createDocumentResource(dt, n) → GET /api/resource/{doctype}/{name}
call(method, params)          → POST /api/method/{method}
auth.login(email, password)   → POST /api/method/login
auth.logout()                 → POST /api/method/logout
auth.getLoggedUser()          → GET /api/method/frappe.auth.get_logged_user
```

### All Backend Endpoints Currently Used

| Endpoint | Called From | Purpose |
|----------|-----------|---------|
| `maxedu.api_folder.profile.get_user_info` | useUserProfile | Load auth profile |
| `maxedu.api_folder.assignments.get_assignments` | useAssignments | Student assignments |
| `maxedu.api_folder.assignments.submit_assignment` | useAssignments | Submit with file |
| `maxedu.api_folder.attendance.get_attendance` | useAttendance | Calendar data |
| `maxedu.api_folder.attendance.get_attendance_summary` | useAttendanceSummary | Stats |
| `maxedu.api_folder.exam.get_exams` | useExaminations | Exam schedule |
| `maxedu.api_folder.exam.get_results` | useExaminations | Results |
| `maxedu.api_folder.exam.get_teacher_exams` | useTeacherExams | Teacher exams |
| `maxedu.api_folder.teacher_data.get_my_profile` | useTeacherDashboard | Teacher info |
| `maxedu.api_folder.teacher_data.get_teacher_pending_tasks` | useTeacherDashboard | Pending tasks |
| `maxedu.api_folder.classes.get_my_schedule` | useTeacherClasses | Schedule |
| `maxedu.api_folder.grading.get_plan_details` | useGreading | Grading plan |
| `maxedu.api_folder.grading.save_marks` | useGreading | Save marks |
| `maxedu.api_folder.event.get_all_events` | useEvents | Events |
| `maxedu.library_management.api.get_catalog` | useLibraryBooks | All books |
| `maxedu.library_management.api.get_my_issues` | useBorrowedBooks | Borrowed books |
| `maxedu.library_management.api.get_my_requests` | useLibraryBooks | Requests |
| `maxedu.library_management.api.get_book_recommendations` | useLibraryBooks | Recommendations |
| `maxedu.library_management.api.request_book` | useBookRequest | Request book |
| `maxedu.library_management.api.cancel_request` | useBookRequest | Cancel request |
| `maxedu.desk_approval.doctype.application.application.get_approved_notices` | useNotices | Notices |
| `maxedu.desk_approval.doctype.application.application.get_notice` | useNotices | Notice detail |
| `/api/method/upload_file` | useAssignments | File upload |

> **Migration needed:** All `maxedu.*` endpoints should be migrated to `vidyaan.*` or native Frappe resource API.

---

## 12. Known Issues & Technical Debt

### Critical
| Issue | Description |
|-------|-------------|
| **Wrong branding** | All UI says "MaxEdu ERP" — must be "Vidyaan" |
| **Legacy API endpoints** | All composables call `maxedu.api_folder.*` which is the old module name |
| **Old role names** | Middleware checks for `student`/`teacher` — Vidyaan uses `Student`/`Instructor`/`Institute Admin` |
| **No Institute Admin routes** | No pages or dashboard for Institute Admin role |
| **No System Admin routes** | No SaaS admin dashboard |

### Medium
| Issue | Description |
|-------|-------------|
| **21 console.log statements** | Debug logging left in production code |
| **Hardcoded notification data** | Navbar notifications are fake/sample data |
| **Global search not functional** | Search bar is cosmetic only |
| **Announcements can't be posted** | No submit handler in Announcements component |
| **Social login commented out** | Google/Microsoft buttons disabled |
| **StudyMaterialModal is 13K+ lines** | Should be broken into sub-components |
| **useBookRequest is 8200+ lines** | Overly complex, needs refactoring |
| **Duplicate modal components** | AppModal.vue and AppModal2.vue — consolidate |
| **Typo in folder name** | `components/dashbaord/` should be `dashboard/` |

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
| 1.1 | Rebrand MaxEdu → Vidyaan everywhere | Low | nuxt.config.ts, login.vue, AppSideBar.vue, all page titles |
| 1.2 | Migrate API endpoints from `maxedu.*` to `vidyaan.*` | Medium | All 31 composables |
| 1.3 | Update role detection in middleware | Low | role-based.global.js, useUserProfile.js |
| 1.4 | Remove all console.log statements | Low | ~15 files |
| 1.5 | Fix folder typo `dashbaord` → `dashboard` | Low | Components + imports |

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
| Incomplete / placeholder features | **9** |
| Not yet built (backend ready) | **6** |
| Not yet built (needs backend + frontend) | **12** |
| Composables | **31** |
| Components | **22** |
| Pages/Routes | **~31** |
| Known issues / tech debt items | **14** |

---

*Last updated: 2026-04-01*
