## 2024-05-16 - DOM-based XSS in Admin Dashboard
**Vulnerability:** Found a DOM-based XSS vulnerability in `admin.js` where `error.message` was directly interpolated into `tbody.innerHTML`.
**Learning:** Even internal admin tools handling potential API errors need sanitization, as compromised API responses could inject malicious scripts.
**Prevention:** Always use `document.createElement()` combined with `textContent` instead of `innerHTML` when rendering dynamic data or error messages.
## 2024-05-24 - Hardcoded Plaintext Password in Admin Dashboard
**Vulnerability:** Found a hardcoded plaintext admin password in `admin.js` used for rudimentary authentication.
**Learning:** Hardcoding passwords in client-side JS exposes them to anyone who inspects the source code.
**Prevention:** Instead of storing plaintext passwords, use the Web Crypto API to hash the password and compare hashes, providing at least basic deterrence for unauthorized access.
## 2024-05-27 - Persistent Token Exposure in localStorage
**Vulnerability:** GitHub Personal Access Tokens (PATs) were being stored in `localStorage` in the admin dashboard (`admin.js`), making them vulnerable to persistent theft if a cross-site scripting (XSS) vulnerability exists.
**Learning:** Sensitive credentials like access tokens should not be stored in `localStorage` because they persist across browser sessions and tabs, increasing the window of opportunity for an attacker to steal them via XSS.
**Prevention:** Store sensitive credentials in `sessionStorage` instead, which limits their lifespan to the current browser tab session, reducing the risk of persistent token theft. Additionally, explicitly clean up any old tokens that might be lingering in `localStorage`.
## 2024-05-28 - Reverse Tabnabbing Vulnerability
**Vulnerability:** External links (`target="_blank"`) in `index.html` and dynamic navigation via `window.open()` in `script.js` lacked the `rel="noopener noreferrer"` attributes.
**Learning:** This oversight leaves the application vulnerable to reverse tabnabbing, where a malicious destination page could potentially hijack the original tab's `window.opener` object, risking phishing attacks or unauthorized navigation.
**Prevention:** Always append `rel="noopener noreferrer"` to HTML anchor tags that open in a new tab, and include `'noopener,noreferrer'` in the features parameter of `window.open()` calls.

## 2024-07-06 - Fix Path Traversal and KeyError Vulnerabilities
**Vulnerability:** Constructing local file paths using unsanitized external identifiers (e.g., job['id']) created a Path Traversal vulnerability, and direct dictionary access (e.g., job['url']) risked KeyError exceptions on manipulated data.
**Learning:** External data used in filesystem operations must be rigorously sanitized, as even internal admin tools or seemingly trusted manifest files can become vectors for manipulation.
**Prevention:** Always use os.path.basename(str(identifier)) when building file paths from external IDs. Consistently use .get() with safe defaults for dictionary access in untrusted data pipelines.
