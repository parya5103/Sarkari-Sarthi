# Sarkari Sarthi daily source report

Run started: 2026-11-27T06:40:14

## Run totals

- archived expired: 0
- duplicates: 8
- expired now: 43
- merged: 0
- new jobs: 0
- raw candidates: 8
- rejected unsafe ids: 0

## Sources

| Source | Status | Duration | Found | New | Dup | Merged | Errors | Notes |
|---|---|---|---|---|---|---|---|---|
| allgovernmentjobs.in | ok | 3.08 | 8 |  |  |  |  |  |
| bharatsarkarijob.com | no-jobs | 3.78 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| employmentnews.gov.in | fetch-failed |  | 0 |  |  |  |  | listing request failed: HTTPSConnectionPool(host='employmentnews.gov.in', port=443): Max retries exceeded with url: /newemp/AllJobs.aspx?k=All (Caused by ConnectTimeoutError(<HTTPS |
| www.freejobalert.com | no-jobs | 2.97 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.fresherslive.com | fetch-failed | 10.39 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.freshersnow.com | no-jobs | 3.46 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.freshersworld.com | fetch-failed | 10.08 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.jobriya.com | no-jobs | 22.9 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.jobsarkari.com | no-jobs | 3.03 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.mysarkarinaukri.com | fetch-failed | 8.58 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.rojgarresult.com | no-jobs | 5.86 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkari-naukri.info | fetch-failed | 10.75 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.sarkariexam.com | no-jobs | 3.1 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukri.com | no-jobs | 2.99 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
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
