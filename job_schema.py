"""Consistent job record schema, status computation and deduplication.

Every job saved to the manifest and to jobs/<id>.json passes through
normalize_job() so the whole system works with one structure:

    id, title, organization, department, category, location, vacancies,
    advertisement_no, qualification, age_limit, description,
    important_dates (last_date, application_start_date, exam_date, ...),
    official_notification_url, official_application_url,
    original_source_url, url, source, published_date, scraped_at,
    last_verified, status.

Rules from the project master plan:
- Missing information is stored as None. It is NEVER fabricated here.
  The UI renders None values as NOT_SPECIFIED_TEXT.
- status is derived only from real parsed dates:
  cancelled > expired > upcoming > active.
- Deduplication matches on the official URL, or on a non-empty
  (advertisement_no, organization) pair. Jobs are never merged just
  because their titles look similar.
"""

from datetime import date, datetime, timedelta

NOT_SPECIFIED_TEXT = 'Not specified in official notification'

DATE_FORMATS = ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %b %Y', '%d %B %Y')

OPTIONAL_TEXT_FIELDS = (
    'organization', 'department', 'location', 'vacancies',
    'advertisement_no', 'qualification', 'age_limit',
    'official_notification_url', 'official_application_url',
    'published_date',
)


def parse_date(value):
    """Parse a job date string to datetime.date, or None.

    Understands the common Indian job-notification formats and ISO
    timestamps. Returns None for anything unparseable: callers must
    treat None as 'not available', never guess a date.
    """
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(cleaned).date()
    except ValueError:
        return None


def compute_status(job, today=None):
    """Derive job status without inventing information.

    cancelled: previously stored status says so (admin-controlled).
    expired:   parsed last_date is strictly before today.
    upcoming:  parsed application_start_date is strictly after today.
    active:    otherwise (including jobs with no parseable dates).
    """
    today = today or date.today()
    if str(job.get('status') or '').lower() == 'cancelled':
        return 'cancelled'
    dates = job.get('important_dates') or {}
    last_date = parse_date(dates.get('last_date') or job.get('last_date'))
    if last_date and last_date < today:
        return 'expired'
    start_date = parse_date(
        dates.get('application_start_date') or job.get('application_start_date')
    )
    if start_date and start_date > today:
        return 'upcoming'
    return 'active'


def normalize_job(job, now=None):
    """Return a copy of job upgraded to the full schema.

    - Preserves every existing key (no data is dropped or overwritten).
    - Backfills important_dates from flat admin fields (last_date,
      application_start_date) when the nested value is missing.
    - Sets missing optional fields to None (meaning: not available in
      the official notification; the UI shows NOT_SPECIFIED_TEXT).
    - last_verified defaults to scraped_at, else to now.
    - status is (re)computed from the real dates.
    """
    if not isinstance(job, dict):
        raise ValueError('normalize_job expects a dict job record')
    now = now or datetime.now().isoformat()

    normalized = dict(job)
    dates = dict(normalized.get('important_dates') or {})
    if not dates.get('last_date') and normalized.get('last_date'):
        dates['last_date'] = normalized['last_date']
    if not dates.get('application_start_date') and normalized.get('application_start_date'):
        dates['application_start_date'] = normalized['application_start_date']
    normalized['important_dates'] = dates

    for field in OPTIONAL_TEXT_FIELDS:
        if normalized.get(field) in (None, ''):
            normalized[field] = None

    if not normalized.get('description') and normalized.get('summary'):
        normalized['description'] = normalized['summary']
    if not normalized.get('original_source_url') and normalized.get('url'):
        normalized['original_source_url'] = normalized['url']
    if not normalized.get('last_verified'):
        normalized['last_verified'] = normalized.get('scraped_at') or now
    normalized['status'] = compute_status(normalized)
    return normalized


def _clean_text(value):
    """Lowercase, whitespace-collapsed text for comparisons, or None."""
    if not isinstance(value, str):
        return None
    collapsed = ' '.join(value.split()).strip().lower()
    return collapsed or None


def advertisement_key(job):
    """(advertisement_no, organization) comparison key, or None.

    Only non-empty pairs count: deduplicating on a partial key would
    merge unrelated advertisements.
    """
    adv = _clean_text(job.get('advertisement_no'))
    org = _clean_text(job.get('organization'))
    if adv and org:
        return (adv, org)
    return None


def is_duplicate_job(candidate, existing_urls, existing_adv_keys):
    """Return a duplicate reason string, or None if the job is unique.

    Duplicate when the official URL was already stored, or when the
    same (advertisement_no, organization) was already stored. Titles
    alone NEVER deduplicate.
    """
    url = candidate.get('url')
    if url and url in existing_urls:
        return 'same-url'
    key = advertisement_key(candidate)
    if key and key in existing_adv_keys:
        return 'same-advertisement'
    return None


NOTIFICATION_WINDOW_HOURS = 36
NOTIFICATION_CAP = 25


def select_recent_jobs(jobs, now=None, hours=NOTIFICATION_WINDOW_HOURS, cap=NOTIFICATION_CAP):
    """Return jobs first recorded within the notification window, capped.

    Notification channels must not blast the full manifest every run:
    only jobs whose scraped_at (or found_date / last_verified
    fallback) falls inside the window are selected, at most `cap` of
    them. Jobs without any usable timestamp are skipped rather
    than guessed.
    """
    now = now or date.today()
    window_start = now - timedelta(hours=hours)
    selected = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        stamp = (job.get('scraped_at')
                 or (job.get('important_dates') or {}).get('found_date')
                 or job.get('last_verified'))
        parsed = parse_date(stamp) if stamp else None
        if parsed and parsed >= window_start:
            selected.append(job)
    return selected[:cap]
