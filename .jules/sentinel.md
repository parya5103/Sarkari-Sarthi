## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.

## 2024-05-18 - [CRITICAL] Fix hardcoded plaintext password
**Vulnerability:** Found a hardcoded plaintext password (`admin`) in the client-side JavaScript (`admin.js`) used as a deterrence for basic UI access.
**Learning:** Storing plaintext passwords in client-side code completely nullifies any intended security or deterrence, as the password can be trivially read by anyone inspecting the source code or network responses.
**Prevention:** Always use a secure hash (e.g., SHA-256 via Web Crypto API) to perform client-side authentication, preventing the plaintext password from being exposed directly in the source code.
