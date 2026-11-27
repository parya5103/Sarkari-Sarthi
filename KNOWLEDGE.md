# Sarkari Sarthi (parya5103/Sarkari-Sarthi) - Project Knowledge

Persistent project knowledge file. Created by the documentation-sync audit on 2026-11-24.

NOTE: AGENT_NOTES.md (repo root) is the long-running detailed agent log with phase history,
source-permission table and CI gotchas. This file is the audited summary; keep both current.

## What this repo is

- Indian government-job portal ("SarkariSarthi") published at https://gogocompany.in/sarkari-sarthi/.
- A Python scraper + workflow runs daily in GitHub Actions (daily-job-fetch-deploy.yml,
  cron 30 23 * * * = 05:00 IST): it fetches public government job sources, normalizes them
  into jobs/job_manifest.json, generates per-job detail pages (detail_pages.py) and a sitemap,
  commits data to main, and republishes the gh-pages branch that serves the live site.
- Frontend is static HTML/CSS/JS (index.html, script.js, style.css) reading the manifest
  through relative paths, so it works under the /sarkari-sarthi/ subdirectory.

## Verified architecture (source-inspected 2026-11-24)

- Scraper pipeline: scraper.py (source adapters, robots-gated fetching, honest User-Agent
  SarkariSarthiJobPortal/2.0), parser.py (title-based keyword categorization with word-boundary
  rules), official_sources.py (verified official adapters, e.g. Employment News
  employmentnews.gov.in), storage.py (merge fill-only-missing semantics, expiry only on
  verified past last_date, orphan-file sweep, expired archive), job_schema.py,
  source_metrics.py, detail_pages.py (static detail pages with JobPosting JSON-LD).
- Data rules that must never be broken: expiry only from VERIFIED past last_date; expired/
  cancelled jobs keep a banner, get no JSON-LD and are excluded from the sitemap; unknown
  fields are never guessed; duplicates merge without overwriting richer metadata;
  deadline calculations use Asia/Kolkata (UTC runs must not keep expired Indian deadlines
  active); manifest verification_status drives honest trust labels.
- Frontend: script.js renders tabs + search from the manifest, hides non-compliant records,
  shows trust chips, bookmarks (localStorage key sarkariBookmarks) and honest
  getRecordTimestamp-based sorting. ads.js is fail-closed (cmpReady) with slots sarkari-mid and
  sarkari-detail-bottom (fluid). gogo-notifications.js (root) is the GoGo Central push
  module with apiBase + VAPID configured; firebase-messaging-sw.js supports opt-in.
- admin.html + admin.js are a READ-ONLY manifest viewer (real admin edits happen via GitHub
  web UI / Actions; the old fake client-side password auth was removed on purpose as
  security debt cleanup). Do not reintroduce client-side credential gates.

## CI/CD and security posture (merged and verified)

- daily-job-fetch-deploy.yml: tests job (pytest + jest), WebP hero step with ffmpeg
  install-if-missing (fixed 2026-11-09 after ubuntu-latest dropped preinstalled ffmpeg and
  silently broke every deploy from 2026-11-07), fetch + commit + gh-pages deploy + health
  check + Telegram/WhatsApp notifications (secrets.TELEGRAM_BOT_TOKEN etc.).
- security-scan.yml (gitleaks full history + trivy, CRITICAL gate), codeql.yml,
  dependabot (pip/npm/github-actions), scorecard.yml, lighthouse.yml (weekly, audits
  gogocompany.in/sarkari-sarthi/ after the daily data refresh).
- A real Telegram bot token leaked in git history (.github/workflows/fetch.yml, since
  deleted) was revoked by the owner and the repo secret was rotated (2026-11-07);
  .gitleaks.toml allowlists the historical path only, with justification.

## COMPLETED (evidence)

- Phases 0-8 series of upgrades (PRs #190-#200 era): honest parser categories, link validity
  gates, orphan sweeps, fail-closed frontend errors, detail pages with JobPosting JSON-LD,
  sitemap (1 portal + per-job URLs), trust chips, bookmarks, India-local deadlines,
  admin-as-viewer, workflow hardening. CI green + gh-pages republished verified each merge.
- Pinned security CI (PRs #216/#217) and GoGo notifications (PR #218).
- Daily deploys verified green repeatedly (e.g. run #587, 2026-11-09).
- PR #235 (2026-11-20): "Index only verified, substantial recruitment detail pages" -
  indexing gates tightened for detail pages.
- Daily bot auto-update commits are flowing (latest at audit: 2026-11-24).

## PENDING / NOT VERIFIED

- Any live-browser/Android QA of the portal UI; Lighthouse numeric results from the
  scheduled weekly runs were never downloaded and reviewed.
- ncs.gov.in / upsc.gov.in / mprojgar.gov.in robots.txt verification still pending; adapters
  are intentionally absent until robots access is confirmed.
- freejobalert.com + fresherslive.com per-portal adapters (richer metadata than portal-level
  scraping) not yet written.

## PLANNED (not implemented)

- Official Employment News adapter improvements; per-source adapters; richer per-job schema
  fields (vacancies/fees/qualification) where sources really provide them.

## Cross-repository dependencies

- parya5103/gogo-website: sync-products.yml publishes the /sarkari-sarthi/ path from
  this same repository's `gh-pages` branch (daily 06:15 IST cron or manual "Sync product apps").
  Verified 2026-11-27: source is `parya5103/Sarkari-Sarthi@gh-pages`, not `main`.
  Main-branch changes reach gogocompany.in only after the daily fetch/deploy workflow
  successfully publishes the updated gh-pages branch and the central sync succeeds.
- parya5103/gogo-central-backend: notification registration/sends for opt-in users.

## Known documentation debt (intentionally not fixed here without approval)

- README.md still carries inflated AI claims ("Smart AI-Powered", HuggingFace/OpenAI
  "summarization") that do not match the deterministic scraper, plus broken badge links to
  username/SarkariSarthi_2.0. The scraper has NO AI. Fixing the README is a separate
  owner-approved change (flagged in the 2026-11-03 audit and still present 2026-11-24).

## Constraints future agents must preserve

- Never bypass CAPTCHAs, logins or anti-bot protections; always respect robots.txt findings.
- Never invent vacancies, dates, eligibility or application links.
- Keep relative paths (script.js fetches jobs/job_manifest.json relative to the page) so the
  portal keeps working under the /sarkari-sarthi/ subpath.
- Work on feature branches + PRs; never merge without owner approval; update AGENT_NOTES.md
  and this file after every significant change; never commit secrets.


## 2026-11-27 verified maintenance and inventory snapshot

- Latest checked `jobs/job_manifest.json` snapshot (last_updated `2026-11-26T16:56:28`): 306 total records, 266 active and 40 expired. Active category counts: General 128, Medical 59, Administrative 30, Engineering 31, Teaching 9, Banking 3, Defence 2, SSC 1, IT 1, Railway 1 and UPSC 1. These are manifest records, not a claim that every listing is officially verified.
- The homepage title is `Latest Government Jobs 2026 | Sarkari Sarthi`; the homepage no longer carries a meta-keywords tag. Medical, Engineering and Administrative filters/cards are present. Keep source and verification labels accurate; the manifest includes `needs_review` and `secondary_source_only` records.
- Verification guide page says `Updated 26 November 2026`. Its sitemap `lastmod` is aligned to `2026-11-26`. The sitemap generator now reads the visible `Updated DD Month YYYY` date from `verification-guide.html`; keep the page date format and regression test in sync so a daily fetch cannot revert it to an obsolete hard-coded date.
- Dependency maintenance merged on 2026-11-27: `actions/setup-node@v7.1.0`, `ossf/scorecard-action@v2.6.0`, `peaceiris/actions-gh-pages@v4.1.0`, `pdfplumber==0.11.11`, `jest==30.5.2`, `requests==2.34.2`, `lxml==6.1.3` and `PyMuPDF==2.1`. `jest-environment-jsdom` remains at 29.7.0 because 30.5.2 caused `TypeError: Cannot redefine property: location` in `tests/test_script.test.js`.
- CodeQL init and analyze were updated together to the same pinned v4.39.4 action in PR #249 (merged 2026-11-27); do not split these action versions.
- The CSS interface-refresh rules were already present in `style.css` in compact form; do not append a duplicate block.
- Deployment-source caution: the GoGo central sync configuration checks out `parya5103/Sarkari-Sarthi@gh-pages` from this same repository. Verify both the main-to-gh-pages deployment and the central sync before claiming a change is live on `gogocompany.in`.
