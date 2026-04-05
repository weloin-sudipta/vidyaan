# Memory Index
# Tracks patterns, mistakes, and optimizations learned

## Patterns
- useFrappeFetch composable pattern: Standard API wrapper with loading/error states
- Role-based middleware: Global auth + role-based route protection
- Component consolidation: Merge duplicate components (AppModal/AppModal2)
- DocType extension: Add company field for multi-tenancy
- API method naming: vidyaan.api_folder.module.method format

## Mistakes
- Orphan custom fields from reinstalls (fixed with cleanup)
- Missing approver role in publications (fixed to Institute Admin)
- Fragile examiner validation chain (added fallback lookups)
- Typoed directory names (dashbaord/ vs dashboard/)
- Incomplete agent registry and project state tracking

## Optimizations
- Batch API calls for related data
- Cache repeated lookups in hooks
- Use native Frappe doctypes before creating custom ones
- Consolidated component library to reduce duplication
- Automated publication creation on assessment submission