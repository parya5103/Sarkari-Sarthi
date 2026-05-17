## 2026-05-16 - Make Div-based Interactive Elements Keyboard Accessible
**Learning:** Interactive elements built with standard `<div>` tags (like job cards and category cards) are entirely skipped by keyboard navigation (Tab key) by default. Without keyboard focusability, users relying on keyboards cannot access or activate these features.
**Action:** When building interactive components using non-semantic tags (like `<div>` or `<span>`), always add `role="button"`, `tabindex="0"`, appropriate `aria-label`s, AND `keydown` event listeners for the 'Enter' and 'Space' keys to ensure they can be focused and activated like standard buttons.
## 2024-05-17 - Mobile Menu Keyboard Accessibility
**Learning:** This app occasionally uses non-semantic tags (like `<div>` or `<span>`) for interactive components like the mobile menu toggle, which requires manual additions of `role="button"`, `tabindex="0"`, `aria-expanded`, and manual keyboard event bindings for 'Enter' and 'Space' to be fully accessible.
**Action:** Always check interactive icon/menu triggers to ensure they are fully navigable via keyboard and announced correctly to screen readers.
