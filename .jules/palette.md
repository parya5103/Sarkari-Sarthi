## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.
## 2026-06-22 - Dynamic ARIA Label Synchronization
**Learning:** When interactive UI elements (like category cards with `role="button"`) include dynamic data such as counts within their visual text, screen readers announce only the static `aria-label` attribute if it is not updated. This leads to desynchronization between visual state and accessible state. Emoticons within these cards can also add noise if not hidden.
**Action:** Ensure `aria-label` attributes are updated dynamically inside the same JavaScript functions that update the DOM. Apply `aria-hidden="true"` to decorative elements (such as emojis or icons rendered as text) inside an interactive component that uses an explicit `aria-label` to prevent redundant or noisy screen reader announcements.
