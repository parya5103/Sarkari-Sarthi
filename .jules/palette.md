## 2026-05-16 - Make Div-based Interactive Elements Keyboard Accessible
**Learning:** Interactive elements built with standard `<div>` tags (like job cards and category cards) are entirely skipped by keyboard navigation (Tab key) by default. Without keyboard focusability, users relying on keyboards cannot access or activate these features.
**Action:** When building interactive components using non-semantic tags (like `<div>` or `<span>`), always add `role="button"`, `tabindex="0"`, appropriate `aria-label`s, AND `keydown` event listeners for the 'Enter' and 'Space' keys to ensure they can be focused and activated like standard buttons.

## 2024-05-19 - Keyboard Accessibility for Non-Semantic Interactive Elements
**Learning:** When building interactive elements using non-semantic tags like `<div>` or `<span>` (e.g., a custom hamburger menu), they must be explicitly made keyboard accessible. This requires adding `role="button"`, `tabindex="0"`, an appropriate `aria-label`, adding CSS focus styles, and importantly, attaching a `keydown` event listener to handle 'Enter' and 'Space' key activations.
**Action:** Always ensure that custom interactive elements created from `div` or `span` tags have full keyboard support and ARIA attributes mimicking native buttons.
