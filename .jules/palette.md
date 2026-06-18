## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-06-13 - Dynamic ARIA Label Synchronization
**Learning:** In custom interactive elements (like category cards) that display dynamic data (e.g., job counts), updating only the text content in JS causes screen readers to fall out of sync if an `aria-label` is present.
**Action:** Always dynamically update the `aria-label` inside the same JavaScript function that updates the element's DOM text to ensure accurate states are announced.
