## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-07-02 - Dynamic ARIA Labels on Interactive Elements
**Learning:** When interactive elements (like category cards) include dynamic data (such as job counts) and require an explicit `aria-label` (due to decorative emojis needing `aria-hidden="true"`), their `aria-label` must be dynamically updated alongside the DOM to prevent screen reader desynchronization.
**Action:** Always update the `aria-label` attributes inside the same JavaScript functions that update the DOM text content for dynamic components. Ensure the `aria-label` includes all critical information from the inner text.
