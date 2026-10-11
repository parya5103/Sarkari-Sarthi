## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-05-28 - Dynamic ARIA Label Synchronization
**Learning:** When interactive UI elements (like custom buttons or category cards) include dynamic data such as counts within their visual text, ensure their `aria-label` attributes are updated dynamically inside the same JavaScript functions that update the DOM. This prevents screen reader desynchronization and ensures accurate states are announced.
**Action:** Always verify that JavaScript functions updating visual element text also update corresponding `aria-label` or `aria-valuenow` attributes for accessibility.
