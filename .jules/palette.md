## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.
## 2024-07-02 - Synchronize dynamic ARIA labels on custom components
**Learning:** When interactive elements (like category cards) have explicit `aria-label` attributes and dynamic text content (like job counts updated via JS), the `aria-label` MUST be updated simultaneously in the DOM script to prevent screen reader desynchronization, while decorative elements like emojis within them should be explicitly hidden from screen readers using `aria-hidden="true"`.
**Action:** Always verify that JavaScript functions updating inner text of elements with custom ARIA labels also explicitly update those ARIA labels to match the new state.
