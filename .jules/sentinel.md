## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.
## 2024-05-24 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext admin password in `admin.js` used for rudimentary authentication.
**Learning:** Hardcoding passwords in client-side JS exposes them to anyone who inspects the source code.
**Prevention:** Instead of storing plaintext passwords, use the Web Crypto API to hash the password and compare hashes, providing at least basic deterrence for unauthorized access.
## 2024-05-26 - [Mitigating Persistent XSS for Sensitive Tokens]
**Vulnerability:** The admin UI stored the highly sensitive GitHub Personal Access Token (PAT) in `localStorage`. If the frontend suffered from a Cross-Site Scripting (XSS) vulnerability, an attacker could silently exfiltrate this persistent token long after the admin had closed the tab.
**Learning:** For single-page applications without backend session management, sensitive credentials that must be stored client-side for API requests should be stored in `sessionStorage` rather than `localStorage`. `sessionStorage` is cleared when the tab/window is closed, significantly reducing the window of opportunity for token theft via XSS.
**Prevention:** Avoid `localStorage` for sensitive tokens (like PATs or session IDs). Prefer `sessionStorage` for temporary, in-memory tokens if client-side storage is strictly necessary, and always ensure tokens are cleared upon logout.
