## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.
## 2026-06-06 - Dynamic ARIA Labels for Data-Driven UI
**Learning:** When interactive elements (like custom buttons or cards) display dynamic data (like job counts) as part of their visual text, relying solely on inner text can lead to poor screen reader experiences or desynchronization.
**Action:** Always bind the `aria-label` updates directly to the same JavaScript functions that update the visual DOM elements to ensure the accessible name remains perfectly synced with the dynamic data.
