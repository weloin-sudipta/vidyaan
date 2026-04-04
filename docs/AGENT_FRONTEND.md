# Frontend Agent — Vidyaan Project Rules

> **READ THIS ENTIRE FILE BEFORE WRITING ANY CODE.**
> This file defines the mandatory workflow, rules, and constraints for any AI/agent working on Vidyaan frontend (Nuxt 4, Vue 3, Tailwind CSS).

---

## Step 0 — Mandatory Pre-Read (DO NOT SKIP)

Before touching any code, read these files **in order**:

1. `docs/FRONTEND.md` — complete frontend documentation (architecture, features, components, composables, API endpoints, known issues, roadmap)
2. `docs/IMPLEMENTATION_PLAN.md` — understand the phased roadmap and priorities
3. `docs/BACKLOG.md` — know active bugs and frontend migration tasks (FE-001 to FE-004)
4. `docs/frontend_feature_backlog.md` — detailed frontend work items
5. `docs/FEATURES.md` — know what backend features are ready for frontend

**Then explore the actual codebase:**

6. `frontend/components/ui/` — read ALL UI components to know what's available
7. `frontend/composable/` — scan composable names to know what state/API wrappers exist
8. `frontend/middleware/` — understand auth and RBAC flow
9. `frontend/layouts/` — understand the layout system

**If you have not read these files, STOP and read them now.**

---

## Step 1 — Understand the Task

Before writing code, answer these questions (internally):

1. What page/feature is being built or modified?
2. Does a page for this already exist? (check `frontend/pages/`)
3. Does a composable for the data already exist? (check `frontend/composable/`)
4. Which existing UI components can I reuse? (check `frontend/components/ui/`)
5. Does this need a new API endpoint or does the backend already support it?
6. Will this change affect other pages or components?

---

## Step 2 — Component Rules (CRITICAL)

### Rule 1: USE EXISTING COMPONENTS FIRST

Before creating any new component, check what already exists:

**Available UI primitives (`components/ui/`):**
| Component | Purpose |
|-----------|---------|
| `AppSideBar.vue` | Navigation sidebar (role-based) |
| `AppNavBar.vue` | Top navbar (search, notifications, profile) |
| `DataTable.vue` | Data grid with sort/filter |
| `AppModal.vue` | Modal dialog |
| `AppModal2.vue` | Modal dialog (variant) |
| `HeroHeader.vue` | Page header with icon and search |
| `StatCard.vue` | Statistics card |
| `UiCard.vue` | Generic card wrapper |
| `UiSkeleton.vue` | Loading skeleton |
| `UiStatusBadge.vue` | Status badge |
| `AppLoader.vue` | Loading spinner |

**Available feature components:**
| Component | Purpose |
|-----------|---------|
| `BookCard.vue` | Book display |
| `BookRecommendation.vue` | Book recommendation item |
| `StudyMaterialModal.vue` | Study material form |
| `ToastContainer.vue` | Toast notifications |
| `applications/NewRequestModal.vue` | Application form |
| `dashboard/DailyRoutine.vue` | Daily schedule |
| `dashboard/academicCalendar.vue` | Calendar widget |
| `dashboard/campusNotice.vue` | Notice widget |
| `profile/ProfileForm.vue` | Profile edit form |

**Decision tree:**
```
Does an existing component do what I need?
  ├── YES → Use it. Pass props/slots for customization.
  │
  └── NO → Is there a similar component that does 80% of what I need?
      ├── YES → Extend/modify that component. Do NOT create a duplicate.
      │
      └── NO → Is this a reusable pattern (used in 2+ places)?
          ├── YES → Create ONE new component in components/ui/
          │
          └── NO → Inline it in the page. No component needed.
```

### Rule 2: CONSOLIDATE, DON'T DUPLICATE

If you find multiple components doing the same thing, **merge them into one** and update all imports.

Known duplicates to consolidate:
- `AppModal.vue` and `AppModal2.vue` — pick the better one, migrate all usages
- Any dashboard widgets that repeat card+stat patterns — use `StatCard.vue`

**When consolidating:**
- The visual output MUST NOT change
- The behavior MUST NOT change
- Only the internal implementation gets cleaner
- Update ALL import paths after merging

### Rule 3: MINIMAL NEW COMPONENTS

- Do NOT create a component for something used only once — inline it in the page
- Do NOT create wrapper components that just pass props through
- Do NOT create "util" components — use composables for logic, components for UI only
- Every new component must justify its existence by being used in 2+ places

---

## Step 3 — Design Rules (CRITICAL)

### Rule 1: DO NOT CHANGE THE EXISTING DESIGN

The app has an established visual style. **Do not alter it:**

- **Glassmorphism** — frosted glass card effects (`backdrop-blur`, semi-transparent bg)
- **Gradient backgrounds** — indigo/purple/pink gradients
- **Rounded corners** — `rounded-2xl` or `rounded-3xl` on cards
- **Shadow depth** — layered shadows on cards and modals
- **Color palette** — indigo, purple, slate, emerald, amber (Tailwind extended)
- **Dark mode** — every element MUST have `dark:` variants
- **Responsive** — mobile-first, grid cols adapt (1 col mobile → 2-3 col desktop)

### Rule 2: BE CREATIVE WITHIN THE STYLE

You can be creative with:
- Animations and transitions (use `transition`, `transform`)
- Layout arrangements within the existing grid system
- Icon choices (Font Awesome 7)
- Micro-interactions (hover states, focus rings)
- Loading state presentations (skeletons, spinners)
- Data visualization (ApexCharts)

You MUST NOT:
- Introduce a new color scheme
- Change font sizes/weights globally
- Add a new CSS framework or library
- Override Tailwind defaults
- Remove dark mode support from any element
- Break responsive behavior

### Rule 3: DARK MODE IS MANDATORY

Every single element you create must work in both light and dark mode.

```vue
<!-- CORRECT -->
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">

<!-- WRONG — no dark mode -->
<div class="bg-white text-gray-900">
```

No exceptions.

---

## Step 4 — Code Quality Rules

### Composables

- Check `frontend/composable/` before creating a new one
- If a composable exists for the data you need, **use it**
- If you need to extend an API call, add it to the existing composable
- New composables should follow the established pattern:
  ```js
  export function useFeatureName() {
    const data = ref(null)
    const loading = ref(false)
    const error = ref(null)

    async function fetchData() {
      loading.value = true
      // ... API call via useFrappeFetch
      loading.value = false
    }

    return { data, loading, error, fetchData }
  }
  ```

### API Calls

- ALL API calls go through `useFrappeFetch.ts` — never use raw `fetch()` or `axios`
- Use `createResource()` for method calls
- Use `createListResource()` for listing doctypes
- Include loading states and error handling
- Current endpoints use `maxedu.*` prefix — new work should use `vidyaan.*` prefix

### State Management

- Use `useState()` for global SSR-safe state (auth, user profile)
- Use `ref()` for local composable state
- Do NOT add Vuex, Pinia, or any external state library
- Keep state close to where it's used

### Don't Break Existing Code

- **Before modifying any file**, read it completely
- **Search for all imports** of any component you change (`grep -r "ComponentName"`)
- **Check the router** — if you rename/move a page, update all `navigateTo()` and `<NuxtLink>` references
- **Check the sidebar** — `AppSideBar.vue` has hardcoded route paths for navigation
- **Check middleware** — `role-based.global.js` has route-to-role mappings
- **Test in both light and dark mode**
- **Test on mobile viewport** (375px width minimum)

---

## Step 5 — Implementation Flow

```
1. READ the docs (Step 0)
2. UNDERSTAND the task (Step 1)
3. INVENTORY existing components and composables that can be reused
4. CHECK if a similar page/feature exists that you can extend
5. PLAN the minimal changes needed
6. READ every file you plan to modify
7. WRITE the code:
   a. Reuse existing components
   b. Follow the design system (glassmorphism, gradients, dark mode)
   c. Use existing composables for data
   d. Add loading skeletons for async data
   e. Make it responsive
8. VERIFY:
   a. No visual regression on existing pages
   b. Dark mode works
   c. Mobile responsive
   d. No broken imports/routes
9. UPDATE docs/FRONTEND.md if you added new pages, components, or composables
```

---

## Step 6 — File Location Guide

| What | Where |
|------|-------|
| Pages (routes) | `frontend/pages/` |
| Reusable UI | `frontend/components/ui/` |
| Feature components | `frontend/components/` |
| State + API logic | `frontend/composable/` |
| Layouts | `frontend/layouts/` |
| Route protection | `frontend/middleware/` |
| Static assets | `frontend/assets/` |
| Tailwind config | `frontend/tailwind.config.ts` |
| Nuxt config | `frontend/nuxt.config.ts` |

### Page Naming Convention
- Kebab-case: `study-materials.vue`, `mark-entry.vue`
- Dynamic routes: `[slug].vue`
- Index pages: `index.vue`

### Component Naming Convention
- PascalCase: `StatCard.vue`, `HeroHeader.vue`
- Prefix with domain: `BookCard.vue`, `ProfileForm.vue`

---

## Step 7 — Checklist Before Committing

- [ ] Read all mandatory docs (Step 0)
- [ ] Reused existing components — did NOT create unnecessary new ones
- [ ] No duplicate components — consolidated if found
- [ ] Design matches existing style (glassmorphism, gradients, rounded corners)
- [ ] Dark mode works on every new element (`dark:` variants present)
- [ ] Responsive layout (mobile + desktop)
- [ ] Loading skeletons/spinners for async data
- [ ] API calls go through `useFrappeFetch.ts`
- [ ] Existing composable used/extended (not duplicated)
- [ ] No broken imports — searched for all usages of modified components
- [ ] Sidebar routes updated if new page added (`AppSideBar.vue`)
- [ ] Middleware updated if new role-restricted page added (`role-based.global.js`)
- [ ] No `console.log` left in code
- [ ] Updated `docs/FRONTEND.md` if structure changed

---

## Quick Reference — Existing Pages by Role

**Student:**
`/academics/*`, `/attendance`, `/exam/*`, `/library/*`, `/applications`, `/notices/*`, `/events`, `/faculty`, `/profile/*`, `/documents/*`

**Teacher:**
`/teacher/academics/*`, `/teacher/grading/*`, `/teacher/students/*`, `/teacher/library/*`, `/teacher/profile`

**Admin:**
`/admin/library/*`, `/admin/students/*`

**Shared:**
`/`, `/notices/*`, `/events`, `/error/*`

**Auth:**
`/auth/login`, `/auth/forget-password`

---

*This file is the law for frontend work. Follow it.*
