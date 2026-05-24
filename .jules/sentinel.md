## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.
## 2024-05-24 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext admin password in `admin.js` used for rudimentary authentication.
**Learning:** Hardcoding passwords in client-side JS exposes them to anyone who inspects the source code.
**Prevention:** Instead of storing plaintext passwords, use the Web Crypto API to hash the password and compare hashes, providing at least basic deterrence for unauthorized access.
## 2024-05-24 - Persistent Storage of GitHub Access Token
**Vulnerability:** Found GitHub Personal Access Token (PAT) stored persistently in `localStorage`.
**Learning:** Storing sensitive, long-lived tokens in `localStorage` leaves them highly vulnerable to theft if any DOM-based or cross-site scripting (XSS) vulnerability exists, as the token persists indefinitely across browser sessions.
**Prevention:** Store sensitive access tokens in `sessionStorage` instead, which automatically clears the tokens when the browser session ends, limiting the vulnerability window. Ensure tokens are also explicitly cleared upon logout.
