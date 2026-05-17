## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.

## 2024-11-20 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext password (`ADMIN_PASSWORD = "admin"`) in `admin.js` used for rudimentary authentication.
**Learning:** Even for "deterrence" level security on static sites, hardcoding plaintext credentials in client-side JS exposes them to anyone who views the source.
**Prevention:** Instead of plaintext, store a cryptographic hash (like SHA-256) of the password and use the Web Crypto API (`crypto.subtle.digest`) to hash user input before comparison.
