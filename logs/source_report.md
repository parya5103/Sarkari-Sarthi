# Sarkari Sarthi daily source report

Run started: 2026-11-28T04:33:17

## Run totals

- archived expired: 0
- duplicates: 7
- expired now: 45
- merged: 0
- new jobs: 1
- raw candidates: 8
- rejected unsafe ids: 0

## Sources

| Source | Status | Duration | Found | New | Dup | Merged | Errors | Notes |
|---|---|---|---|---|---|---|---|---|
| allgovernmentjobs.in | ok | 4.61 | 8 | 1 |  |  |  |  |
| bharatsarkarijob.com | no-jobs | 3.68 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| employmentnews.gov.in | fetch-failed |  | 0 |  |  |  |  | listing request failed: HTTPSConnectionPool(host='employmentnews.gov.in', port=443): Max retries exceeded with url: /newemp/AllJobs.aspx?k=All (Caused by ConnectTimeoutError(<HTTPS |
| www.freejobalert.com | no-jobs | 3.99 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.fresherslive.com | fetch-failed | 10.37 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.freshersnow.com | no-jobs | 4.71 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.freshersworld.com | fetch-failed | 9.3 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.jobriya.com | no-jobs | 4.4 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.jobsarkari.com | no-jobs | 4.63 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.mysarkarinaukri.com | fetch-failed | 10.86 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.rojgarresult.com | no-jobs | 6.8 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkari-naukri.info | fetch-failed | 8.83 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.sarkariexam.com | no-jobs | 3.87 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukri.com | no-jobs | 3.89 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukridaily.in | no-jobs | 3.81 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |

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
