# Vidyaan - School ERP System

## Vision

Vidyaan is a **Multi-Tenant School ERP** built on Frappe/ERPNext that transforms educational institutions into a comprehensive digital ecosystem. It leverages native Frappe Education doctypes wherever possible, extending them with smart custom fields and a handful of purpose-built doctypes to deliver:

- AI-powered timetable generation (OR-Tools CP-SAT solver)
- Multi-tenant SaaS isolation (Company-per-Institute)
- Exam/Assignment management with zero new doctypes
- Publication system for notices, news, and announcements
- Modern student/teacher portal (Nuxt 4 + Vue 3)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Frappe 15 |
| ERP Base | ERPNext 15 |
| HR Module | Frappe HRMS 15 |
| Education Module | Frappe Education 15.2 |
| Language | Python 3.12 |
| Database | MariaDB |
| Cache/Queue | Redis |
| Constraint Solver | Google OR-Tools (CP-SAT) |
| Frontend | Nuxt 4 + Vue 3 + Tailwind CSS |
| UI Library | Frappe-UI |
| Build Tool | Vite |

---

## Architecture Overview

### Multi-Tenant SaaS Model

```
                   ┌─────────────────────────────┐
                   │      Single Frappe Site      │
                   │      (dev.localhost)          │
                   └──────────┬──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
     ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
     │  Company A  │  │  Company B  │  │  Company C  │
     │ (School 1)  │  │ (School 2)  │  │ (School 3)  │
     └─────────────┘  └─────────────┘  └─────────────┘
```

Each school = one `Company` doctype record. All education records (Students, Instructors, Programs, etc.) carry a mandatory `company` field linking them to their institute. User Permissions enforce data isolation.

### Triple-Layer Isolation

1. **UI Layer** - Form filters restrict dropdowns to current user's Company
2. **Validation Layer** - Ownership checks in Python before save/submit
3. **Query Layer** - Backend queries always include `company` filter

### Dependency Chain

```
frappe → erpnext → hrms → education → vidyaan
```

---

## Project Structure

```
apps/vidyaan/
├── vidyaan/
│   ├── hooks.py                          # App configuration & event hooks
│   ├── events.py                         # Document event handlers
│   ├── utils.py                          # Utility functions (bootinfo, auto-publication)
│   │
│   ├── vidyaan/                          # Custom Doctypes
│   │   └── doctype/
│   │       ├── period_timing/            # Child: time slots for periods
│   │       ├── instructor_course_mapping/ # Child: teacher-subject-program mapping
│   │       ├── routine_slot/             # Child: generated timetable entries
│   │       ├── routine_generation_program/ # Child: programs for routine batch
│   │       ├── routine_generation/       # Main: AI timetable generator
│   │       ├── publication/              # Main: notices, news, announcements
│   │       └── vidyaan_settings/         # Single: global configuration
│   │
│   ├── setup/                            # Installation & setup scripts
│   │   ├── install.py                    # After-install orchestrator
│   │   ├── custom_fields.py             # Injects Company field into education doctypes
│   │   ├── roles.py                      # Role creation & permissions
│   │   ├── user.py                       # Default admin user creation
│   │   ├── wizard.py                     # First-run setup wizard backend
│   │   ├── onboarding.py                # Module onboarding steps
│   │   └── workspace.py                 # Dashboard workspace builder
│   │
│   ├── public/js/
│   │   └── vidyaan_setup.js             # Frontend setup wizard dialog
│   │
│   ├── templates/
│   │   └── admit_card.html              # Jinja print format for admit cards
│   │
│   └── workspace/
│       └── vidyaan_dashboard/            # Workspace JSON definition
│
├── frontend/                             # Nuxt 4 Student/Teacher Portal
│   ├── pages/                            # Auto-routed pages
│   │   ├── dashboard/                    # Role-specific dashboards
│   │   ├── academics/                    # Subjects, timetable, materials
│   │   ├── teacher/                      # Teacher modules
│   │   ├── admin/                        # Admin modules
│   │   ├── exam/                         # Assessment pages
│   │   ├── library/                      # Library management
│   │   ├── notices/                      # Publications
│   │   └── profile/                      # User profile
│   ├── components/                       # Reusable Vue components
│   ├── composable/                       # Vue 3 composables (API logic)
│   ├── middleware/                        # Auth & role-based route guards
│   ├── layouts/                          # Page layouts
│   └── nuxt.config.ts                    # Nuxt configuration
│
└── docs/                                 # Documentation (you are here)
```

---

## Roles & Access

| Role | Access Level | Scope |
|------|-------------|-------|
| System Administrator | Full system access | All institutes |
| System Manager | Full system access | All institutes |
| Institute Admin | Full CRUD on education + routine doctypes | Own institute only |
| Instructor | Read + attendance + grading (per-document) | Own institute only |
| Student | Read-only via frontend portal | Own records only |

---

## Installation

### Prerequisites
```bash
# Required apps (in order)
bench get-app erpnext --branch version-15
bench get-app hrms --branch version-15
bench get-app education --branch version-15.2   # Note: no version-15 branch exists
bench get-app https://github.com/Sudipto-tales/vidyaan.git

# OR-Tools for timetable generation
pip install ortools
```

### Install on Site
```bash
# Ensure Redis is running (all 3 ports)
redis-server --port 11000 --daemonize yes   # queue
redis-server --port 12000 --daemonize yes   # socketio
redis-server --port 13000 --daemonize yes   # cache

bench --site dev.localhost install-app erpnext
bench --site dev.localhost install-app hrms
bench --site dev.localhost install-app education
bench --site dev.localhost install-app vidyaan
```

### Post-Install Sequence (Automatic)
```
after_install()
  → create_roles()                  # System Admin, Institute Admin, Instructor
  → create_default_user()           # vidyaan@weloin.com
  → create_vidyaan_custom_fields()  # Company field injection + Instructor mapping
  → create_vidyaan_onboarding()     # 3-step guided setup
  → setup_vidyaan_settings()        # Default period timings (09:00-13:00)
  → create_vidyaan_workspace()      # Dashboard with shortcuts & stats
  → setup_admit_card_print_format() # Jinja print format for Students
  → setup_assessment_groups()       # "Exams" + "Assignments" tree nodes
  → Mark ERPNext setup_complete = 1
  → Set vidyaan_setup_complete = 0  # Triggers setup wizard on first login
```

---

## Known Issues & Gotchas

| Issue | Details | Status |
|-------|---------|--------|
| Education branch naming | No `version-15` branch — must use `version-15.2` | Workaround documented |
| Redis required for install | All 3 Redis instances (queue:11000, socketio:12000, cache:13000) must be running | Workaround documented |
| `institute` field conflict | Previous install may leave orphan custom fields that block reinstall | Needs cleanup script |
| Frontend branding | Frontend still uses "MaxEdu" branding instead of "Vidyaan" | Pending migration |
| Plan 5 incomplete | Dynamic Application System design has open questions | Needs design decision |
| `hrms` dependency | App requires hrms which is heavy — consider making optional | Design decision needed |
