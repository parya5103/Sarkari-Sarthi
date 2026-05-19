## Security Learnings - Admin Authentication

- **Client-Side Auth Flaws:** Hardcoding a password in frontend code (like `admin.js`) is an insecure pattern. Attackers can bypass it by inspecting the code, altering local storage (`sessionStorage`), or directly invoking protected functions (e.g., `showDashboard()`).
- **Secure Pattern (SPA without a backend):** If a backend cannot be used, sensitive actions must rely on third-party API authentication (e.g., GitHub API). The application should collect a token (like a Personal Access Token) from the user and validate it directly with the API provider (e.g., `fetch('https://api.github.com/user', { headers: { 'Authorization': 'token ' + input } })`).
- **Token Security:** Tokens should only be sent securely (via Headers, never URL parameters) and stored appropriately (e.g., `localStorage` for SPAs, though `HttpOnly` cookies are better if a backend exists).
- **Validation Fallback:** The server or API providing the protected resources (in this case, GitHub API managing `job_manifest.json`) is the ultimate source of security. Even if the UI is bypassed, the lack of a valid token prevents any malicious actions from succeeding.
