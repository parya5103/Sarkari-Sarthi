## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-07-03 - Dynamic ARIA Labels for Count Badges
**Learning:** When custom UI elements (like category cards acting as buttons) include dynamically updated data (like job counts), explicitly synchronizing their `aria-label` inside the same JavaScript function that updates the DOM prevents screen readers from announcing stale information or disjointed inner text.
**Action:** Always update the container's `aria-label` dynamically alongside its text content inside count-updating functions to maintain accessibility tree sync.
