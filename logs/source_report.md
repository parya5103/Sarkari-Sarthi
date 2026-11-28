# Sarkari Sarthi daily source report

Run started: 2026-11-28T04:54:39

## Run totals

- archived expired: 0
- duplicates: 6
- expired now: 45
- merged: 1
- new jobs: 2
- raw candidates: 8
- rejected unsafe ids: 0

## Sources

| Source | Status | Duration | Found | New | Dup | Merged | Errors | Notes |
|---|---|---|---|---|---|---|---|---|
| allgovernmentjobs.in | ok | 3.68 | 8 | 2 |  |  |  |  |
| bharatsarkarijob.com | no-jobs | 3.51 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| employmentnews.gov.in | fetch-failed |  | 0 |  |  |  |  | listing request failed: HTTPSConnectionPool(host='employmentnews.gov.in', port=443): Max retries exceeded with url: /newemp/AllJobs.aspx?k=All (Caused by ConnectTimeoutError(<HTTPS |
| www.freejobalert.com | no-jobs | 3.5 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.fresherslive.com | fetch-failed | 8.31 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.freshersnow.com | no-jobs | 4.09 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.freshersworld.com | fetch-failed | 7.24 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.jobriya.com | no-jobs | 6.6 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.jobsarkari.com | no-jobs | 2.87 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.mysarkarinaukri.com | fetch-failed | 9.1 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.rojgarresult.com | no-jobs | 4.7 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkari-naukri.info | fetch-failed | 13.5 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.sarkariexam.com | no-jobs | 3.68 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukri.com | no-jobs | 3.55 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukridaily.in | no-jobs | 3.47 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |

## Needs attention

- bharatsarkarijob.com: no-jobs
- employmentnews.gov.in: fetch-failed
- www.freejobalert.com: no-jobs
- www.fresherslive.com: fetch-failed
- www.freshersnow.com: no-jobs
- www.freshersworld.com: fetch-failed
- www.jobriya.com: no-jobs
- www.jobsarkari.com: no-jobs
- www.mysarkarinaukri.com: fetch-failed
- www.rojgarresult.com: no-jobs
- www.sarkari-naukri.info: fetch-failed
- www.sarkariexam.com: no-jobs
- www.sarkarinaukri.com: no-jobs
- www.sarkarinaukridaily.in: no-jobs

A source returning HTTP 200 with zero extracted jobs still appears above: extraction success is measured by parsed jobs, not by HTTP status alone.
