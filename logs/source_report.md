# Sarkari Sarthi daily source report

Run started: 2026-11-27T18:28:43

## Run totals

- archived expired: 0
- duplicates: 9
- expired now: 43
- merged: 9
- new jobs: 0
- raw candidates: 9
- rejected unsafe ids: 0

## Sources

| Source | Status | Duration | Found | New | Dup | Merged | Errors | Notes |
|---|---|---|---|---|---|---|---|---|
| allgovernmentjobs.in | ok | 4.79 | 9 |  |  |  |  |  |
| bharatsarkarijob.com | no-jobs | 5.52 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| employmentnews.gov.in | fetch-failed |  | 0 |  |  |  |  | listing request failed: HTTPSConnectionPool(host='employmentnews.gov.in', port=443): Max retries exceeded with url: /newemp/AllJobs.aspx?k=All (Caused by ConnectTimeoutError(<HTTPS |
| www.freejobalert.com | no-jobs | 5.47 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.fresherslive.com | fetch-failed | 7.37 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.freshersnow.com | no-jobs | 6.29 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.freshersworld.com | fetch-failed | 8.17 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.jobriya.com | no-jobs | 5.42 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.jobsarkari.com | no-jobs | 3.57 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.mysarkarinaukri.com | fetch-failed | 10.6 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.rojgarresult.com | no-jobs | 7.27 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkari-naukri.info | fetch-failed | 9.04 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.sarkariexam.com | no-jobs | 5.52 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukri.com | no-jobs | 5.27 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukridaily.in | no-jobs | 2.4 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |

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
