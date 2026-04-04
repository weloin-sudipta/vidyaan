# Vidyaan — AI Agent Instructions

> **Every AI/agent MUST read the relevant agent file before doing ANY work.**

## Agent Instruction Files

| Working On | Read This First | Then Read |
|-----------|----------------|-----------|
| **Backend** (Python, doctypes, hooks, API) | `docs/AGENT_BACKEND.md` | `docs/DOCTYPES.md`, `docs/IMPLEMENTATION_PLAN.md` |
| **Frontend** (Nuxt, Vue, Tailwind, pages) | `docs/AGENT_FRONTEND.md` | `docs/FRONTEND.md`, `docs/IMPLEMENTATION_PLAN.md` |
| **Admin Panel** (permissions, roles, desk) | `docs/AGENT_ADMIN.md` | `docs/CUSTOMIZATIONS.md`, `docs/IMPLEMENTATION_PLAN.md` |

## Critical Rules (All Agents)

1. **Read implementation plans BEFORE coding** — `docs/IMPLEMENTATION_PLAN.md` and `docs/implementation/plan1-5.md`
2. **Do NOT create new doctypes** unless absolutely necessary — use existing Education/ERPNext doctypes first
3. **Do NOT create duplicate components** — reuse what exists, consolidate duplicates
4. **Do NOT change the visual design** — maintain glassmorphism, gradients, dark mode, responsive layout
5. **Write automation hooks** — when one doctype changes, cascade updates to related doctypes
6. **Minimal code changes** — smallest diff that solves the problem without side effects
7. **Check for side effects** — search for all usages before modifying any function/component/API
8. **Admin panel = Frappe Desk** — no custom admin UI, give direct doctype access

## Project Documentation

| Doc | Purpose |
|-----|---------|
| `docs/PROJECT.md` | What Vidyaan is, tech stack, architecture |
| `docs/FEATURES.md` | Feature status (done, partial, planned) |
| `docs/DOCTYPES.md` | All doctypes — native and custom |
| `docs/CUSTOMIZATIONS.md` | Every modification to native doctypes |
| `docs/BACKLOG.md` | Bugs and priority roadmap |
| `docs/FRONTEND.md` | Complete frontend documentation |
| `docs/IMPLEMENTATION_PLAN.md` | Consolidated plan with phases |
| `docs/architecture_and_workflow.md` | Multi-tenant SaaS architecture |
| `docs/implementation/plan1-5.md` | Individual feature design plans |

## Tech Stack

- **Backend:** Frappe 15 + ERPNext 15 + Education 15.2 + Python 3.12
- **Frontend:** Nuxt 4.3.1 + Vue 3.5.28 + Tailwind CSS + Frappe-UI
- **Solver:** Google OR-Tools CP-SAT (timetable generation)
- **Admin:** Frappe Desk (native)
