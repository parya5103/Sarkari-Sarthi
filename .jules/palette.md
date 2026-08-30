## 2026-05-28 - Empty State Enhancement
**Learning:** Adding actionable empty states (like a "Clear All Filters" button) significantly improves UX by preventing users from getting stuck in dead ends after an over-constrained search.
**Action:** When implementing filtering or search logic, always pair the "no results" state with an immediate, one-click action to reset the filters and return the user to a baseline populated state.

## 2024-06-24 - Dynamic ARIA Labels for Interactive Elements with Counts
**Learning:** When interactive elements (like `category-card` components) include dynamic data such as job counts within their visual text, relying only on inner text or static `aria-label`s leads to screen reader desynchronization and redundant or inaccurate announcements. Text emojis also get read redundantly if not hidden.
**Action:** Apply `aria-hidden="true"` to decorative text emojis inside such components. Explicitly set an `aria-label` on the parent interactive element and dynamically update this `aria-label` inside the exact same JavaScript functions that update the visible DOM text to ensure accurate states are announced.
