# Sentinel Security Learnings

- Replaced a hardcoded plaintext admin password in `admin.js` with a client-side SHA-256 hashed password.
- Used the standard Web Crypto API (`crypto.subtle.digest`) for hashing the user's input before comparison.
- Leftover garbage files from agent-driven development operations should be cleaned up prior to the commit stage.
