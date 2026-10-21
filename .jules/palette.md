## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-06-29 - Dynamic ARIA Labels for Interactive Elements
**Learning:** When interactive UI elements (like category cards) include dynamic data such as counts within their visual text, screen readers may fail to announce state updates if `aria-label` attributes aren't synchronized. Decorative emojis also need `aria-hidden="true"` so they aren't read redundantly.
**Action:** When adding an `aria-label` to an interactive element with dynamic sub-content, ensure the `aria-label` is updated dynamically inside the same JavaScript functions that update the DOM. Hide visual decorative emojis with `aria-hidden="true"`.
