## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.
## 2024-05-24 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext admin password in `admin.js` used for rudimentary authentication.
**Learning:** Hardcoding passwords in client-side JS exposes them to anyone who inspects the source code.
**Prevention:** Instead of storing plaintext passwords, use the Web Crypto API to hash the password and compare hashes, providing at least basic deterrence for unauthorized access.
## 2024-05-25 - Persistent API Token Exposure
**Vulnerability:** GitHub Personal Access Token was stored persistently in `localStorage`.
**Learning:** Storing highly sensitive API credentials in `localStorage` increases the exposure window significantly; if an XSS vulnerability exists, the token remains accessible indefinitely across sessions.
**Prevention:** Use `sessionStorage` for temporary sensitive credentials to ensure they are cleared when the browser/tab is closed, reducing the attack surface.
