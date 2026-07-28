## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-07-05 - Dynamic ARIA Labels on Interactive Data Elements
**Learning:** Adding an `aria-label` to an interactive element replaces its text content for screen readers. If the inner text contains dynamically updated data (like job counts), the `aria-label` will fall out of sync unless it's explicitly updated via JavaScript.
**Action:** When implementing interactive elements with dynamic text counts, apply an explicit, descriptive `aria-label` and ensure it is dynamically synchronized in the same JavaScript function that updates the visual count.
