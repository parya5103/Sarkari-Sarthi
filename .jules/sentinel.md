## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.
## 2024-05-24 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext admin password in `admin.js` used for rudimentary authentication.
**Learning:** Hardcoding passwords in client-side JS exposes them to anyone who inspects the source code.
**Prevention:** Instead of storing plaintext passwords, use the Web Crypto API to hash the password and compare hashes, providing at least basic deterrence for unauthorized access.
## 2024-05-25 - Persistent XSS Token Theft Risk
**Vulnerability:** The GitHub Personal Access Token (`ghToken`) was stored in `localStorage`, making it persistently vulnerable to theft in the event of an XSS attack across browsing sessions.
**Learning:** `localStorage` persists data across sessions and tabs indefinitely until explicitly cleared, increasing the window of opportunity for attackers to exfiltrate highly privileged tokens.
**Prevention:** Always store highly sensitive credentials (like GitHub PATs or session tokens) in `sessionStorage` instead of `localStorage` so the risk footprint is minimized to the active tab/session, or prefer `HttpOnly` secure cookies if a backend server exists.
