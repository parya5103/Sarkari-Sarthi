## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-05-29 - Dynamic ARIA Label Synchronization
**Learning:** When interactive elements (like category cards doubling as buttons) include dynamic data such as counts within their visual text, screen readers will quickly fall out of sync if the explicit `aria-label` is not also updated dynamically. Adding an `aria-label` is not a one-time operation for dynamic components.
**Action:** When adding static `aria-label`s to components whose inner text changes dynamically via JavaScript, ensure you also locate the update function (e.g., `updateJobCounts`) and synchronize the `aria-label` update alongside the `textContent` update to prevent accessibility regressions.
