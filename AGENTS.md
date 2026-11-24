# Sarkari Sarthi (Sarkari-Sarthi) - Agent Instructions

These rules REPLACE the previous generic agent protocol that described a
Next.js/React/Tailwind stack which does NOT exist in this repository. This repo is a Python
scraper plus a static HTML/CSS/JS portal; do not introduce new frameworks.

## Read first
- KNOWLEDGE.md and AGENT_NOTES.md (repo root) before every session. Inspect existing code
  before modifying it; reuse existing modules; make the smallest safe change.

## Data rules (highest priority)
- Expiry logic only from VERIFIED past last_date; expired/cancelled records are kept but
  excluded from the sitemap and JSON-LD and shown with an honest banner.
- Never guess missing dates, eligibility or links; use "See official notification".
- Deadline arithmetic must use Asia/Kolkata.
- Duplicates merge fill-only-missing with source_refs; never overwrite richer scraped fields
  with flatter manual fields (a flat-schema overwrite bug destroyed data once before).
- Respect robots.txt findings per source; never bypass CAPTCHA/login/anti-bot.

## Frontend rules
- Relative paths only (script.js fetches jobs/job_manifest.json relatively) so the portal
  keeps working under https://gogocompany.in/sarkari-sarthi/.
- Keep fail-closed behavior when the manifest is unavailable (honest error + Retry); never
  bring back sample/fake job data.
- Anchors referenced by the tests (trust chips, saved-jobs filter, sorted timestamps) must
  not be silently renamed; extend the jest/pytest suites with any behavior change and never
  weaken assertions (they scan comments too - keep sensitive identifiers out of comments).

## Admin and security
- admin.html/admin.js stay a read-only viewer with textContent-only rendering and no write
  paths and no client-side credential gates.
- All workflow credentials come from GitHub secrets. Never hardcode tokens; never commit
  .env values; document environment variable names only.

## Workflow / CI
- daily-job-fetch-deploy.yml pushes data + gh-pages. Jobs/steps gated off on PRs execute
  for the first time only after merging to main - never assume a runner has preinstalled
  binaries (ffmpeg): keep install-if-missing fallbacks.
- Keep workflow permissions minimal; escalate only where required.

## Process
- Inspect first; feature branches + PRs; conventional commit messages; update README if
  architecture changes; update AGENT_NOTES.md + KNOWLEDGE.md after every significant change;
  no force push; merge only with owner approval.
