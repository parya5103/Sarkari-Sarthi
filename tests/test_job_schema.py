"""Tests for the Phase 4 job schema: normalization, status, dedup.

Covers: missing and malformed dates, duplicate advertisements,
expired/cancelled handling, no fabrication of missing values, and the
storage-level status backfill during delete_expired_jobs.

Run with: python -m pytest tests/test_job_schema.py -v
"""
from datetime import date, timedelta

import pytest

import storage
from job_schema import (
    NOT_SPECIFIED_TEXT, parse_date, compute_status, normalize_job,
    advertisement_key, is_duplicate_job,
)

TODAY = date(2026, 11, 3)


def base_job():
    return {
        'id': 'abc123',
        'title': 'SSC CGL 2026 Notification',
        'url': 'https://example.gov.in/job/1',
        'source': 'example.gov.in',
        'description': 'Official notification text',
        'important_dates': {'found_date': '09-11-2026'},
        'category': 'SSC',
        'skills': [],
        'scraped_at': '2026-10-20T02:02:03.926475',
        'links': [],
    }


class TestParseDate:
    def test_common_indian_formats(self):
        assert parse_date('09-11-2026') == date(2026, 11, 9)
        assert parse_date('09/11/2026') == date(2026, 11, 9)
        assert parse_date('2026-11-09') == date(2026, 11, 9)
        assert parse_date('09 Nov 2026') == date(2026, 11, 9)
        assert parse_date('09 November 2026') == date(2026, 11, 9)

    def test_iso_timestamp(self):
        assert parse_date('2026-11-09T14:22:48') == date(2026, 11, 9)

    def test_invalid_and_missing(self):
        assert parse_date(None) is None
        assert parse_date('') is None
        assert parse_date('   ') is None
        assert parse_date('not a date') is None
        assert parse_date('32-13-2026') is None
        assert parse_date(20261109) is None


class TestComputeStatus:
    def test_expired_when_last_date_in_past(self):
        job = base_job()
        job['important_dates'] = {'last_date': '01-11-2026'}
        assert compute_status(job, TODAY) == 'expired'

    def test_active_when_last_date_today_or_future(self):
        job = base_job()
        job['important_dates'] = {'last_date': '03-11-2026'}
        assert compute_status(job, TODAY) == 'active'
        job['important_dates'] = {'last_date': '30-11-2026'}
        assert compute_status(job, TODAY) == 'active'

    def test_cancelled_wins(self):
        job = base_job()
        job['status'] = 'cancelled'
        job['important_dates'] = {'last_date': '30-11-2026'}
        assert compute_status(job, TODAY) == 'cancelled'

    def test_upcoming_when_start_date_in_future(self):
        job = base_job()
        job['important_dates'] = {'application_start_date': '10-11-2026'}
        assert compute_status(job, TODAY) == 'upcoming'

    def test_active_when_no_dates(self):
        # No fabricated dates: a job without dates stays active.
        assert compute_status(base_job(), TODAY) == 'active'

    def test_unparseable_last_date_keeps_active(self):
        job = base_job()
        job['important_dates'] = {'last_date': 'asap'}
        assert compute_status(job, TODAY) == 'active'

    def test_flat_last_date_also_recognised(self):
        job = base_job()
        del job['important_dates']
        job['last_date'] = '01-11-2026'
        assert compute_status(job, TODAY) == 'expired'


class TestNormalizeJob:
    def test_schema_fields_added_without_data_loss(self):
        job = base_job()
        out = normalize_job(job)
        for field in ('organization', 'department', 'location', 'vacancies',
                      'advertisement_no', 'qualification', 'age_limit',
                      'official_notification_url', 'official_application_url',
                      'published_date', 'last_verified', 'status',
                      'original_source_url'):
            assert field in out, field
        for key in job:
            assert key in out
        assert out['description'] == 'Official notification text'
        assert out['skills'] == []

    def test_missing_fields_are_none_not_fabricated(self):
        out = normalize_job(base_job())
        assert out['organization'] is None
        assert out['qualification'] is None
        assert out['important_dates'].get('last_date') is None
        assert NOT_SPECIFIED_TEXT == 'Not specified in official notification'

    def test_last_verified_defaults_to_scraped_at(self):
        out = normalize_job(base_job())
        assert out['last_verified'] == '2026-10-20T02:02:03.926475'

    def test_last_verified_not_overwritten(self):
        job = base_job()
        job['last_verified'] = '2026-01-01T00:00:00'
        assert normalize_job(job)['last_verified'] == '2026-01-01T00:00:00'

    def test_flat_admin_last_date_backfilled_into_important_dates(self):
        job = base_job()
        del job['important_dates']
        job['last_date'] = (date.today() + timedelta(days=20)).strftime('%d-%m-%Y')
        out = normalize_job(job)
        assert out['important_dates']['last_date'] == job['last_date']
        assert out['status'] == 'active'

    def test_summary_becomes_description_when_missing(self):
        job = base_job()
        del job['description']
        job['summary'] = 'Manual summary'
        assert normalize_job(job)['description'] == 'Manual summary'

    def test_original_source_url_from_url(self):
        out = normalize_job(base_job())
        assert out['original_source_url'] == 'https://example.gov.in/job/1'

    def test_rejects_non_dict(self):
        with pytest.raises(ValueError):
            normalize_job('not-a-dict')

    def test_existing_values_never_overwritten(self):
        job = base_job()
        job['organization'] = 'Staff Selection Commission'
        job['vacancies'] = '1200'
        out = normalize_job(job)
        assert out['organization'] == 'Staff Selection Commission'
        assert out['vacancies'] == '1200'


class TestDeduplication:
    def test_same_url_duplicate(self):
        urls = {'https://example.gov.in/job/1'}
        cand = {'url': 'https://example.gov.in/job/1', 'title': 'X'}
        assert is_duplicate_job(cand, urls, set()) == 'same-url'

    def test_same_advertisement_and_organization_duplicate(self):
        keys = {('adv/2026/01', 'staff selection commission')}
        cand = {
            'url': 'https://other.example.in/xyz',
            'title': 'X',
            'advertisement_no': 'ADV/2026/01',
            'organization': 'Staff Selection Commission',
        }
        assert is_duplicate_job(cand, set(), keys) == 'same-advertisement'

    def test_title_similarity_alone_is_not_duplicate(self):
        urls = {'https://example.gov.in/job/1'}
        cand = {
            'url': 'https://different.gov.in/job/2',
            'title': 'SSC CGL 2026 Notification',
        }
        assert is_duplicate_job(cand, urls, set()) is None

    def test_partial_advertisement_key_is_none(self):
        assert advertisement_key({'advertisement_no': 'ADV/2026/01'}) is None
        assert advertisement_key({'organization': 'SSC'}) is None
        assert advertisement_key({}) is None

    def test_advertisement_key_normalizes_case_and_whitespace(self):
        key = advertisement_key({
            'advertisement_no': '  ADV/2026/01  ',
            'organization': 'staff   selection commission',
        })
        assert key == ('adv/2026/01', 'staff selection commission')

    def test_unique_job_returns_none(self):
        cand = {'url': 'https://example.gov.in/job/9', 'title': 'X'}
        assert is_duplicate_job(cand, set(), set()) is None


class TestStorageStatusBackfill:
    """delete_expired_jobs must keep the normalized schema: retained
    jobs get status/last_verified and unavailable fields stay None."""

    def test_retained_jobs_get_status(self, tmp_path, monkeypatch):
        job_dir = tmp_path / 'jobs'
        job_dir.mkdir()
        monkeypatch.setattr(storage, 'JOB_DIR', str(job_dir))
        monkeypatch.setattr(storage, 'MANIFEST_FILE', str(job_dir / 'job_manifest.json'))

        active = {
            'id': 'active_job_1',
            'title': 'Active Job',
            'url': 'https://example.gov.in/a',
            'important_dates': {
                'last_date': (date.today() + timedelta(days=20)).strftime('%d-%m-%Y')
            },
        }
        expired = {
            'id': 'expired_job_1',
            'title': 'Old Job',
            'url': 'https://example.gov.in/b',
            'important_dates': {
                'last_date': (date.today() - timedelta(days=30)).strftime('%d-%m-%Y')
            },
        }
        storage.save_jobs_to_files([active, expired])
        storage.save_manifest({'jobs': [active, expired]})

        storage.delete_expired_jobs()

        manifest = storage.load_manifest()
        ids = [job['id'] for job in manifest['jobs']]
        assert ids == ['active_job_1']
        kept = manifest['jobs'][0]
        assert kept['status'] == 'active'
        assert kept['last_verified']
        assert kept['organization'] is None
        assert not (job_dir / 'expired_job_1.json').exists()
        assert (job_dir / 'active_job_1.json').exists()
