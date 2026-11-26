# Sarkari Sarthi daily source report

Run started: 2026-11-26T16:56:28

## Run totals

- archived expired: 0
- duplicates: 8
- expired now: 40
- merged: 8
- new jobs: 0
- raw candidates: 8
- rejected unsafe ids: 0

## Sources

| Source | Status | Duration | Found | New | Dup | Merged | Errors | Notes |
|---|---|---|---|---|---|---|---|---|
| allgovernmentjobs.in | ok | 4.5 | 8 |  |  |  |  |  |
| bharatsarkarijob.com | no-jobs | 3.05 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| employmentnews.gov.in | fetch-failed |  | 0 |  |  |  |  | listing request failed: HTTPSConnectionPool(host='employmentnews.gov.in', port=443): Max retries exceeded with url: /newemp/AllJobs.aspx?k=All (Caused by ConnectTimeoutError(<HTTPS |
| www.freejobalert.com | no-jobs | 3.2 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.fresherslive.com | fetch-failed | 8.34 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.freshersnow.com | no-jobs | 3.01 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.freshersworld.com | fetch-failed | 10.34 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.jobriya.com | no-jobs | 3.71 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.jobsarkari.com | no-jobs | 2.7 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.mysarkarinaukri.com | fetch-failed | 8.43 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.rojgarresult.com | no-jobs | 5.03 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkari-naukri.info | fetch-failed | 6.68 | 0 |  |  |  |  | listing page unreachable or blocked |
| www.sarkariexam.com | no-jobs | 3.0 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukri.com | no-jobs | 3.42 | 0 |  |  |  |  | listing fetched but no vacancy links parsed |
| www.sarkarinaukridaily.in | fetch-failed | 55.71 | 0 |  |  |  |  | listing page unreachable or blocked |

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
- www.sarkarinaukridaily.in: fetch-failed

A source returning HTTP 200 with zero extracted jobs still appears above: extraction success is measured by parsed jobs, not by HTTP status alone.
