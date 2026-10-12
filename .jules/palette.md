## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.
## 2024-05-24 - Screen Reader Compatibility with role="button" Cards
**Learning:** Adding an aria-label to a parent element with role="button" (like a job card) causes screen readers to announce ONLY the label and ignore all inner text. This can unintentionally hide critical information (like deadlines or categories) that is visible on screen.
**Action:** When adding aria-label to a composite interactive element, ensure the label encompasses all critical data presented within the element to prevent accessibility regressions.
