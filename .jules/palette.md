## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-05-28 - Dynamic ARIA Labels for Interactive Elements
**Learning:** In interactive elements (like category cards) that contain dynamically updating data (such as job counts), static ARIA attributes or relying on inner text can lead to screen reader desynchronization.
**Action:** Always dynamically update the `aria-label` attribute inside the same JavaScript function that updates the visual DOM text to ensure accurate states are announced.
