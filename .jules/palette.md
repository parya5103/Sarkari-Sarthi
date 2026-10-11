## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-06-10 - Dynamic ARIA Labels on Category Cards
**Learning:** When interactive UI elements (like the app's custom `.category-card` buttons) dynamically update their internal text counts via JS, screen readers will announce stale data unless their `aria-label` attributes are updated simultaneously in the same function. Furthermore, because `aria-label` replaces the element's inner text for screen readers, the label must incorporate all critical inner text (like category name and updated job count) to prevent accessibility regressions.
**Action:** Whenever implementing or modifying components that fetch and display dynamic counts (like `.category-card`), ensure the DOM update function explicitly updates the `aria-label` to reflect the new state, maintaining full context (e.g., `Filter by ${category}, ${count} available`).
