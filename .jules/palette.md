## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-06-07 - Dynamic ARIA Label Synchronization
**Learning:** When adding `aria-label` to elements with `role="button"`, screen readers announce the label *instead* of the inner content. If the element contains dynamic data (like item counts), the `aria-label` becomes a stale source of truth.
**Action:** Always ensure that `aria-label` attributes are dynamically updated inside the same JavaScript functions that update the DOM content, ensuring all critical dynamic information is included in the label to prevent screen reader desynchronization.
