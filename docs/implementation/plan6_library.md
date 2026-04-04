# Plan 6: Library Module Redesign

> **Status:** Implemented  
> **Priority:** HIGH  
> **Depends on:** Phase 1 bug fixes (complete), Frontend API migration (complete)

---

## Problem Statement

The existing `library_management` module has 11 doctypes (including 2 unused/redundant ones), fragile inventory sync hooks, and no recommendation engine. The frontend has a complete library UI but the backend APIs were under the dead `maxedu` namespace. The module needs to:

1. **Reduce complexity** — remove unused doctypes, eliminate fragile sync hooks
2. **Support dual mode** — work as both school library submodule AND standalone public library
3. **Physical + Digital** — support physical books (copies, barcodes) and online books (links, files)
4. **Recommendation engine** — Netflix-style "books you might like" based on borrowing history
5. **Keep all features** — every existing workflow must continue working
6. **Librarian admin panel** — real-time admin dashboard with full CRUD operations

---

## Doctype Reduction: 11 → 8

### Removed Doctypes

| Doctype | Reason |
|---------|--------|
| `Book Copy Inventory` | Child table with zero references in any code — completely unused |
| `Book Inventory` | Derived data (total/available copies) computed on-the-fly from Book Copy counts. Removes fragile `sync_inventory` hooks that can get out of sync |
| `Library Shelf` | Single-field master — absorbed as Data field on Book Copy |

### Retained Doctypes (8)

| # | Doctype | Type | Changes |
|---|---------|------|---------|
| 1 | **Library** | Master | +`library_type` (School/Public), +`allow_digital_access`, +`max_renewals` |
| 2 | **Book** | Master | +`shelf` (Data field) |
| 3 | **Book Category** | Master | None |
| 4 | **Book Copy** | Master | +`shelf` (Data). Controller simplified: removed `sync_inventory` |
| 5 | **Book Issue** | Transaction | None — all business logic preserved (fine calc, auto-assign, validation) |
| 6 | **Book Request** | Transaction | None — queue priority system preserved |
| 7 | **Book Tag** | Child | None |
| 8 | **Library Member** | Master | None |

### Why This Works

**Inventory computation** — Instead of maintaining a separate `Book Inventory` doctype with `sync_inventory` hooks that fire on every Book Copy change, we use a SQL aggregation:

```sql
SELECT book, COUNT(*) as total_copies,
       SUM(CASE WHEN status='Available' THEN 1 ELSE 0 END) as available_copies
FROM `tabBook Copy` GROUP BY book
```

This is always accurate (no stale data risk), negligible performance cost for school-sized datasets (<10K copies), and eliminates an entire doctype + complex hook chain.

---

## Recommendation Engine

### Algorithm (5 sections, no new doctypes)

All computed from existing `Book Issue` + `Book` + `Book Category` + `Book Tag` data. Cached with `frappe.cache()` at 6-hour TTL per user.

| # | Section | Algorithm | Data Source |
|---|---------|-----------|-------------|
| 1 | "Based on Your Reading History" | Top 3 categories by borrow frequency × recency → unread books in those categories | Book Issue → Book → Category |
| 2 | "Because You Read [X]" | Tags from last 5 borrowed books → books sharing 2+ tags | Book Issue → Book → Book Tag |
| 3 | "Popular in Your Library" | Most-issued books the user hasn't read | Book Issue GROUP BY book |
| 4 | "Students Also Borrowed" | Collaborative filter: find members with overlapping taste → their other borrows | Book Issue cross-user JOIN |
| 5 | "For Your Program" | Books borrowed by same-program students (school mode only) | Book Issue → Member → User → Student → Program Enrollment |

### Response Format

```json
{
  "sections": [
    {
      "title": "Based on Your Reading History",
      "subtitle": "Books in categories you love",
      "badge": "Personalized",
      "icon": "fa-solid fa-book-open",
      "books": [
        { "id": "BOOK-001", "title": "...", "author": "...", "category": "Fiction", "cover_image": "...", "book_type": "Physical" }
      ]
    }
  ]
}
```

### Performance

- Single SQL query per section (no N+1)
- Max 40 books total across all sections
- Cache per-user with 6-hour TTL
- If user has zero history → return only Popular + Program sections

---

## API Endpoints

### Student/Member APIs (9 total)

| # | Endpoint | Change |
|---|----------|--------|
| 1 | `get_catalog()` | **Modified** — Book Copy aggregation replaces Book Inventory JOIN |
| 2 | `get_my_issues()` | Unchanged |
| 3 | `get_my_requests()` | Unchanged |
| 4 | `request_book(book, library)` | Unchanged |
| 5 | `cancel_request(request_name)` | Unchanged |
| 6 | `renew_book(issue_name)` | **Modified** — Added max_renewals check from Library settings |
| 7 | `approve_renewal(issue_name)` | Unchanged |
| 8 | `get_member_details()` | Unchanged |
| 9 | `get_book_recommendations()` | **NEW** — recommendation engine |

### Librarian Admin APIs (8 total)

| # | Endpoint | Purpose |
|---|----------|---------|
| 1 | `get_library_stats()` | Dashboard stats — 11 metrics (total books, available, issued, overdue, pending requests, renewals, fines, low stock, members) |
| 2 | `get_inventory()` | All books with total/available/issued copy counts via SQL aggregation |
| 3 | `get_all_issues(status)` | All book issues with member + book details, optional status filter (including "Overdue" virtual status) |
| 4 | `get_all_requests(status)` | All book requests with member + book details, optional status filter |
| 5 | `get_all_members()` | All library members with issue counts |
| 6 | `return_book(issue_name)` | Process a book return — sets status to Returned, calculates fine, triggers auto-assign |
| 7 | `approve_request(request_name)` | Approve a pending request — auto-assigns available copy |
| 8 | `reject_request(request_name, remarks)` | Reject a pending request with optional remarks |
| 9 | `issue_from_request(request_name)` | Create Book Issue from an approved request |

All admin APIs are protected by `_check_librarian()` role verification (Librarian or System Manager required). All SQL queries use parameterized inputs to prevent injection.

---

## Preserved Business Logic

All existing workflows remain intact:

- **Request queue** — priority-based, auto-reorder on cancel
- **Auto-assign on return** — next pending request auto-approved when book returned
- **Fine calculation** — days_overdue × fine_per_day on return
- **Librarian validation** — only library's assigned librarian or System Manager can issue/approve
- **Renewal system** — blocked if reservations exist, max renewals enforced, librarian approval extends due_date
- **Membership limits** — max_books_allowed enforced on issue
- **Digital books** — book_type Physical/Digital/Both with external_link + book_file support

---

## Dual Mode: School Library vs Public Library

The new `library_type` field on `Library` doctype enables:

| Feature | School Mode | Public Mode |
|---------|-------------|-------------|
| Ownership | `organization` → Company (multi-tenant) | `owner_user` → User (individual) |
| Members | Auto-created from Student/Instructor records | Manual registration (External type) |
| Program recommendations | Enabled (section 5) | Disabled |
| Data isolation | Company-scoped | Library-scoped |
| Roles | Institute Admin + Librarian | Librarian only |

---

## Frontend Implementation

### Recommendations Page (`pages/library/tabs/recommendations.vue`)

- Calls `get_book_recommendations()` API on mount
- Renders dynamic sections from backend (no hardcoded demo data)
- Horizontal scrollable cards with cover images (fallback to icon placeholder)
- "Request" button on hover calls real request API
- "Read Now" button for digital books opens external link
- Loading skeleton with 3-section placeholder
- Empty state when no recommendations available

### Librarian Admin Panel (`pages/admin/library/`)

**Composable: `useLibraryAdmin.js`**
- Centralized state management for all admin data (stats, inventory, issues, requests, members)
- Action functions with toast notifications and server error parsing
- Single composable shared across all admin tab components

**Admin Dashboard (`index.vue`)**
- 4-tab navigation: Inventory | Issuance | Requests | Members
- Badge counters on tabs for overdue issues and pending requests
- Stats bar with 6 key metrics from `get_library_stats()`

**Inventory Tab (`inventory.vue`)**
- Real book data from `get_inventory()` API
- Search by title/author/ISBN
- Filter by category (dynamically populated from data)
- Stock status filters: All / In Stock / Low Stock / Out of Stock
- Copy progress bars (available/total ratio)

**Issuance Tab (`issuance.vue`)**
- Real issue data from `get_all_issues()` API
- Status filters: All / Active / Overdue / Returned
- **Return Book** action — calls `return_book()`, shows fine amount
- **Approve Renewal** action — calls `approve_renewal()`, shows new due date
- Overdue highlighting with days-late counter

**Requests Tab (`requests.vue`)**
- Real request data from `get_all_requests()` API
- Status filters: All / Pending / Approved / Issued / Rejected
- **Approve** action — calls `approve_request()`
- **Reject** action — calls `reject_request()`
- **Issue Book** action (for approved requests) — calls `issue_from_request()`

**Members Tab (`members.vue`)**
- Real member data from `get_all_members()` API
- Search by name/email/phone
- Filter by member type (Student/Teacher/Staff/External)
- Filter by status (Active/Suspended/Expired)
- Books issued counter with max-limit highlighting

All admin pages support dark mode, responsive design, and use consistent design patterns (rounded cards, uppercase tracking labels, status badges with color coding).

---

## Implementation Steps

1. Create `vidyaan/library/` module directory structure
2. Copy 8 doctypes, change module name, add new fields
3. Simplify Book Copy controller (remove sync_inventory)
4. Create `library/api.py` with all 17 endpoints (9 student + 8 admin)
5. Add `override_whitelisted_methods` in `hooks.py` for backward compat
6. Create `useLibraryAdmin.js` composable for admin state management
7. Rewrite `recommendations.vue` to use real API
8. Rewrite admin `index.vue` with 4-tab layout and stats dashboard
9. Rewrite admin `inventory.vue` with real API + search/filter
10. Rewrite admin `issuance.vue` with real API + return/renewal actions
11. Create admin `requests.vue` with approve/reject/issue actions
12. Create admin `members.vue` with search/filter
13. Update 6 frontend files to new API paths
14. Run `bench migrate`
15. Remove old `library_management/` module

---

## Files Affected

### New Files
```
vidyaan/library/__init__.py
vidyaan/library/api.py
vidyaan/library/doctype/__init__.py
vidyaan/library/doctype/{8 doctype directories}/
frontend/composable/useLibraryAdmin.js
frontend/pages/admin/library/requests.vue
frontend/pages/admin/library/members.vue
```

### Modified Files
```
vidyaan/modules.txt                          # Add "Library"
vidyaan/hooks.py                             # Add override_whitelisted_methods
frontend/composable/useLibraryBooks.js       # 4 path updates
frontend/composable/useBookRequest.js        # 3 path updates
frontend/composable/useBorrowedBooks.js      # 1 path update
frontend/composable/useLibraryMember.js      # 1 path update
frontend/pages/library/tabs/issuedBooks.vue  # 1 path update
frontend/pages/library/tabs/recommendations.vue  # Full rewrite (real API)
frontend/pages/admin/library/index.vue       # Full rewrite (4-tab admin)
frontend/pages/admin/library/inventory.vue   # Full rewrite (real API)
frontend/pages/admin/library/issuance.vue    # Full rewrite (real API)
```

### Deleted Files (after migration verified)
```
vidyaan/library_management/                  # Entire old module
```

---

*Created: 2026-04-02*  
*Updated: 2026-04-03 — Added librarian admin panel, recommendation frontend, admin APIs*
