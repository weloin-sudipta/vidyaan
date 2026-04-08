# Frontend Restructure — 2026-04-08

## Summary

A full structural refactor of the Vidyaan Nuxt 4 frontend was carried out on
branch `refactor/frontend-structure` (11 commits). The goals were:

1. Enable Nuxt 4 auto-imports by renaming `composable/` → `composables/`
2. Organise composables into topic-based subfolders
3. Merge redundant role-specific pages into role-aware unified pages
4. Fix a long-standing `dashbaord` typo
5. Add a reusable UI primitives library
6. Add a global confirmation dialog pattern

---

## Commit Hashes (branch `refactor/frontend-structure`)

| Hash | Description |
|------|-------------|
| `f789525` | Rename `composable/` → `composables/` for Nuxt 4 auto-imports |
| `2e5d4a0` | Remove unused components, composables, and dead pages |
| `0cf730b` | Rename misnamed composables (`useGrading`, `useStudentDashboard`) |
| `91f85ef` | Fix `dashbaord` typo; PascalCase student dashboard components |
| `b5c8ff3` | Add reusable UI primitives (Button, Input, Select, Avatar, Badge, EmptyState, SearchFilterBar) |
| `a2c5a4e` | Add global `useConfirm` with single mounted `<ConfirmDialog>` |
| `ae44e2e` | Merge student/teacher/admin dashboards into role-aware `/dashboard/index.vue` |
| `1987771` | Unify attendance and profile pages by role |
| `071ce59` | Reorganise composables into 7 subfolders and misc cleanup |
| `fbdd2e2` | Repair imports and type errors after restructure |

The 11th commit on the branch was `8071630` (from main: surface real Frappe errors
in `useFrappeFetch`), merged before the refactor started.

---

## Detailed Changes

### `composable/` → `composables/` (Nuxt 4 auto-imports)

Nuxt 4 requires the plural `composables/` folder name for auto-imports to work.
The old singular folder was a remnant from the JavaScript prototype phase.

### Composable subfolder organisation

| Subfolder | Contents |
|-----------|----------|
| `api/` | `useFrappeFetch.ts`, `parseFrappeError.ts`, `types.ts` |
| `auth/` | `useAuth.ts` |
| `academics/` | useAssignments, useAttendance, useCourseTopics, useEvents, useExaminations, useHolidays, useNotices, useStudyMaterials, useTimetable |
| `library/` | useBookRequest, useLibraryAdmin, useLibraryBooks |
| `student/` | useProfile, useStudent, useStudentDashboard, useUserProfile |
| `teacher/` | useFacultyMember, useGrading, useTeacherAssignments, useTeacherClasses, useTeacherDashboard, useTeacherExams |
| `ui/` | useConfirm, usePdf, useToast |

### Composables renamed

| Old name | New name | Reason |
|----------|----------|--------|
| `useGreading.ts` | `useGrading.ts` | Typo fix |
| `userDashboard.ts` | `useStudentDashboard.ts` | Naming convention — all composables prefixed `use` |

### Composables deleted (dead code)

| Composable | Reason |
|-----------|--------|
| `useAdmitCard` | Unused — admit card accessed via Frappe print format |
| `useAllWorkFlow` | Replaced by direct API calls in applications page |
| `useBorrowedBooks` | Merged into `useLibraryBooks` |
| `useLeaveApplication` | Dead — applications page refactored |
| `useLibraryMember` | Unused |

### Deleted components

| Component | Reason |
|-----------|--------|
| `AppModal2.vue` | Duplicate of AppModal.vue |
| `AppLoader.vue` | Replaced by UiSkeleton |
| `UiStatusBadge.vue` | Replaced by UiBadge |
| `DataTable.vue` | Unused |
| `BookCard.vue` | Inlined into library page |
| `BookRecommendation.vue` (root) | Moved to `dashboard/student/BookRecommendation.vue` |

### `dashbaord` typo fixed

`components/dashbaord/` → `components/dashboard/student/` with all widget files
renamed to PascalCase:

| Old | New |
|-----|-----|
| `components/dashbaord/academicCalendar.vue` | `components/dashboard/student/AcademicCalendar.vue` |
| `components/dashbaord/campusNotice.vue` | `components/dashboard/student/CampusNotice.vue` |
| _(and 9 more widgets)_ | _(all PascalCase in new path)_ |

### Unified pages

| Old pages | Unified page | Logic |
|-----------|-------------|-------|
| `pages/dashboard/student.vue` + `teacher.vue` + `admin.vue` | `pages/dashboard/index.vue` | Reads user role from `useUserProfile`, renders appropriate `*DashboardView` component |
| `pages/attendance.vue` (student) + `pages/teacher/academics/attendance.vue` | `pages/academics/attendance.vue` | Role-aware rendering |
| `pages/teacher/profile.vue` | Dropped — `pages/profile/index.vue` is now role-aware | Reads role, renders `StudentProfileView` or `TeacherProfileView` |

### Layout rename

`layouts/authLayout.vue` → `layouts/auth.vue`

Nuxt resolves layout by filename. The rename aligns with Nuxt 4 conventions and
removes the redundant `Layout` suffix.

### Middleware: `.js` → `.ts`

`auth.global.js` + `role-based.global.js` → `auth.global.ts` + `role-based.global.ts`

No logic changes — purely the TypeScript migration.

### `forgot-password` spelling fix

`pages/auth/forget-password.vue` → `pages/auth/forgot-password.vue`

### Template moved

`frontend/templates/certificate.html` → `frontend/utils/pdf-templates/certificate.html`

The `templates/` directory is now deleted. PDF templates live under `utils/pdf-templates/`.

### New UI primitives (`components/ui/`)

`UiButton`, `UiInput`, `UiSelect`, `UiTextarea`, `UiAvatar`, `UiBadge`,
`UiEmptyState`, `UiSearchFilterBar`

All documented individually in `docs/components/ui/`.

### Global `useConfirm` pattern

`composables/ui/useConfirm.ts` + `components/ui/ConfirmDialog.vue`

A single `<ConfirmDialog>` is mounted in `app.vue`. Any page/composable calls
`useConfirm()` to get a `confirm(message, options)` function that returns a
`Promise<boolean>`. Eliminates per-page confirmation modals.

---

## Migration Notes for Open Branches

If you had a branch open during this refactor, you will encounter import errors.
Follow these steps:

1. **Update all imports from `~/composable/` to `~/composables/<subfolder>/`**
   - See the subfolder table above to find which subfolder each composable moved to.
   - Nuxt 4 auto-imports mean you may be able to drop the explicit import entirely
     if the composable name is unique across the project.

2. **Rename `useGreading` → `useGrading`** in any import or usage.

3. **Rename `userDashboard` → `useStudentDashboard`** in any import or usage.

4. **Update layout references:**
   - `layout: 'authLayout'` in page `<script setup>` → `layout: 'auth'`

5. **Update dashboard route links:**
   - `/dashboard/student` → `/dashboard`
   - `/dashboard/teacher` → `/dashboard`
   - `/dashboard/admin` → `/dashboard`

6. **Update attendance route links:**
   - `/attendance` → `/academics/attendance`

7. **Update teacher profile route:**
   - `/teacher/profile` → `/profile`

8. **Update forgot-password links:**
   - `/auth/forget-password` → `/auth/forgot-password`

9. **Remove any usage of deleted composables** (`useAdmitCard`, `useAllWorkFlow`,
   `useBorrowedBooks`, `useLeaveApplication`, `useLibraryMember`) and replace with
   the appropriate alternative (see table above).

10. **Update dashboard component imports** from old paths like
    `components/dashbaord/academicCalendar.vue` to
    `components/dashboard/student/AcademicCalendar.vue`.
