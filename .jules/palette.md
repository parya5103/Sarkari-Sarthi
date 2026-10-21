## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-06-23 - Dynamic ARIA Label Synchronization
**Learning:** When interactive elements (like category cards) contain dynamic data such as counts, simply updating the visible text can lead to screen reader desynchronization, leaving assistive tech users with outdated information.
**Action:** Always ensure `aria-label` attributes are updated dynamically inside the same JavaScript functions that update the DOM text, ensuring the screen reader always announces the most accurate state.
