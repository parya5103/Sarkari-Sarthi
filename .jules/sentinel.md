## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.
## 2024-05-24 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext admin password in `admin.js` used for rudimentary authentication.
**Learning:** Hardcoding passwords in client-side JS exposes them to anyone who inspects the source code.
**Prevention:** Instead of storing plaintext passwords, use the Web Crypto API to hash the password and compare hashes, providing at least basic deterrence for unauthorized access.
## 2024-05-24 - Persistent XSS Risk via LocalStorage Token
**Vulnerability:** Sensitive GitHub API tokens were stored in `localStorage`, meaning they persisted across sessions and were vulnerable to token theft if a persistent XSS vulnerability was ever introduced.
**Learning:** Credentials that grant write access to external systems should have the shortest possible lifecycle and storage persistence on the client side.
**Prevention:** Store sensitive session credentials like tokens in `sessionStorage` (or memory if feasible) rather than `localStorage` to limit their exposure window to the active browser tab.
