"""Tests for static job detail pages and sitemap generation."""
import os

from detail_pages import (
    BASE_URL, SITEMAP_FILE, detail_url, job_posting_jsonld,
    render_detail_page, write_detail_pages, is_indexable_detail_job,
)


def sample_job(job_id='en_sample1', **overrides):
    job = {
        'id': job_id,
        'title': 'TGT Computer Science - Sainik School Nagrota',
        'organization': 'SAINIK SCHOOL NAGROTA',
        'url': 'https://example.gov.in/job/1',
        'source': 'employmentnews.gov.in',
        'description': 'The recruiting authority has published this teaching vacancy for eligible applicants. Review the official notification for the post requirements, educational qualification, application process, required documents, selection stages and important dates. Applicants should compare every condition with the original notice before submitting an application.',
        'important_dates': {'last_date': '21-11-2026', 'found_date': '02-11-2026'},
        'published_date': '02-11-2026',
        'location': {'addressCountry': 'IN', 'addressRegion': 'Himachal Pradesh', 'addressLocality': 'Nagrota'},
        'official_notification_url': 'https://example.gov.in/notice.pdf',
        'official_application_url': 'https://example.gov.in/apply',
        'verification_status': 'official_verified',
        'category': 'Teaching',
        'skills': [],
        'scraped_at': '2026-11-03T10:00:00',
        'last_verified': '2026-11-03T10:00:00',
        'status': 'active',
    }
    job.update(overrides)
    return job


class TestIndexableDetailPolicy:
    def test_only_substantial_officially_backed_details_are_indexable(self):
        assert is_indexable_detail_job(sample_job()) is True

    def test_secondary_source_only_record_is_not_indexable(self):
        assert is_indexable_detail_job(sample_job(verification_status='secondary_source_only')) is False

    def test_needs_review_record_is_not_indexable(self):
        assert is_indexable_detail_job(sample_job(verification_status='needs_review')) is False

    def test_thin_official_record_is_not_indexable(self):
        assert is_indexable_detail_job(sample_job(description='Short notice.')) is False

    def test_missing_core_facts_is_not_indexable(self):
        assert is_indexable_detail_job(sample_job(
            organization=None,
            qualification=None,
            vacancies=None,
            age_limit=None,
            important_dates={},
            official_notification_url=None,
            official_application_url=None,
            salary=None,
            selection_process=None,
        )) is False


class TestJobPostingJsonld:
    def test_verified_fields_included(self):
        job = sample_job()
        ld = job_posting_jsonld(job, detail_url(job['id']))
        assert ld['@type'] == 'JobPosting'
        assert ld['title'] == job['title']
        assert ld['validThrough'].startswith('2026-11-21T23:59')
        assert ld['hiringOrganization']['name'] == 'SAINIK SCHOOL NAGROTA'
        assert ld['datePosted'] == '2026-11-02'

    def test_no_valid_through_without_last_date(self):
        job = sample_job(important_dates={'found_date': '02-11-2026'})
        ld = job_posting_jsonld(job, detail_url(job['id']))
        assert 'validThrough' not in ld

    def test_no_jobposting_without_verified_organization(self):
        job = sample_job(organization=None)
        assert job_posting_jsonld(job, detail_url(job['id'])) is None

    def test_location_is_only_emitted_from_verified_address_data(self):
        ld = job_posting_jsonld(sample_job(), detail_url('en_sample1'))
        assert 'baseSalary' not in ld
        assert ld['jobLocation']['address']['addressCountry'] == 'IN'
        assert 'directApply' not in ld

    def test_none_when_title_or_description_missing(self):
        assert job_posting_jsonld({'id': 'x'}, 'u') is None

    def test_secondary_source_only_jobs_get_no_jobposting_markup(self):
        job = sample_job(verification_status='secondary_source_only')
        assert job_posting_jsonld(job, detail_url(job['id'])) is None

    def test_missing_location_or_apply_route_gets_no_jobposting_markup(self):
        job = sample_job(location=None)
        assert job_posting_jsonld(job, detail_url(job['id'])) is None
        job = sample_job(official_notification_url=None, official_application_url=None)
        assert job_posting_jsonld(job, detail_url(job['id'])) is None

    def test_date_posted_is_required_and_direct_apply_is_not_assumed(self):
        job = sample_job(published_date=None)
        assert job_posting_jsonld(job, detail_url(job['id'])) is None
        ld = job_posting_jsonld(sample_job(), detail_url('en_sample1'))
        assert ld['datePosted'] == '2026-11-02'
        assert 'directApply' not in ld


class TestRenderDetailPage:
    def test_contains_canonical_and_breadcrumb(self):
        job = sample_job()
        page = render_detail_page(job, [])
        assert '<meta name="robots" content="index,follow">' in page
        assert 'rel="canonical" href="' + detail_url(job['id']) + '"' in page
        assert 'Breadcrumb' in page
        assert 'href="/sarkari-sarthi/"' in page

    def test_secondary_and_thin_records_are_noindex(self):
        secondary = render_detail_page(sample_job(verification_status='secondary_source_only'), [])
        thin = render_detail_page(sample_job(description='Short notice.'), [])
        assert '<meta name="robots" content="noindex,follow">' in secondary
        assert '<meta name="robots" content="noindex,follow">' in thin

    def test_html_escaped(self):
        job = sample_job(title='X <script>alert(1)</script>')
        page = render_detail_page(job, [])
        assert '<script>alert(1)</script>' not in page
        assert '&lt;script&gt;' in page

    def test_jsonld_script_injection_escaped(self):
        job = sample_job(title='X Job', description='Y </script><script>alert(1)</script>')
        page = render_detail_page(job, [])
        assert '</script><script>' not in page
        assert 'u003c' in page

    def test_not_specified_shown_for_missing_last_date(self):
        job = sample_job(important_dates={'found_date': '02-11-2026'})
        page = render_detail_page(job, [])
        assert 'Not specified in official notification' in page

    def test_cancelled_banner(self):
        page = render_detail_page(sample_job(status='cancelled'), [])
        assert 'cancelled' in page

    def test_related_links_only_same_category_active(self):
        rel_a = sample_job('en_rel_a', category='Teaching', title='Related Teaching Job')
        rel_b = sample_job('en_rel_b', category='Banking', title='Banking Job')
        rel_c = sample_job('en_rel_c', category='Teaching', status='cancelled', title='Cancelled Job')
        page = render_detail_page(sample_job(), [rel_a, rel_b, rel_c])
        assert 'Related Teaching Job' in page
        assert 'Banking Job' not in page
        assert 'Cancelled Job' not in page

    def test_links_use_verified_urls(self):
        job = sample_job(
            official_notification_url='https://ssc.gov.in/notice.pdf',
            official_application_url='https://ssc.gov.in/apply',
        )
        page = render_detail_page(job, [])
        assert 'https://ssc.gov.in/notice.pdf' in page
        assert 'https://ssc.gov.in/apply' in page

    def test_search_metadata_is_concise_but_visible_heading_stays_complete(self):
        long_title = 'A Very Long Government Recruitment Notification Title With Many Extra Words'
        page = render_detail_page(sample_job(title=long_title, description='Official recruitment details. ' * 20), [])
        head_title = page.split('<title>', 1)[1].split('</title>', 1)[0]
        meta_description = page.split('<meta name="description" content="', 1)[1].split('">', 1)[0]
        assert len(head_title) <= 60
        assert len(meta_description) <= 140
        assert '<h1>' + long_title + '</h1>' in page


class TestClosedJobHandling:
    """Expired and cancelled vacancies: honest banners, no misleading
    JobPosting metadata, no active sitemap entries."""

    def test_expired_and_cancelled_get_no_jsonld(self):
        expired = job_posting_jsonld(
            sample_job(status='expired'), detail_url('en_sample1'))
        cancelled = job_posting_jsonld(
            sample_job(status='cancelled'), detail_url('en_sample1'))
        assert expired is None
        assert cancelled is None

    def test_active_job_still_gets_jsonld(self):
        ld = job_posting_jsonld(sample_job(), detail_url('en_sample1'))
        assert ld is not None
        assert ld['@type'] == 'JobPosting'

    def test_expired_banner_on_detail_page(self):
        page = render_detail_page(sample_job(status='expired'), [])
        assert 'no longer open for' in page
        assert 'kept for reference only' in page

    def test_cancelled_banner_on_detail_page(self):
        page = render_detail_page(sample_job(status='cancelled'), [])
        assert 'marked cancelled' in page

    def test_sitemap_excludes_closed_jobs(self, tmp_path):
        active = sample_job('en_open1')
        expired = sample_job('en_closed1', status='expired')
        cancelled = sample_job('en_cancel1', status='cancelled')
        secondary = sample_job('en_secondary', verification_status='secondary_source_only')
        thin = sample_job('en_thin', description='Short notice.')
        written = write_detail_pages([active, expired, cancelled, secondary, thin], out_root=str(tmp_path))
        # Every safe record remains available as a reference page.
        assert written == 5
        assert (tmp_path / 'job' / 'en_closed1' / 'index.html').exists()
        assert (tmp_path / 'job' / 'en_cancel1' / 'index.html').exists()
        # Only substantial, officially backed records enter the sitemap.
        sitemap = (tmp_path / SITEMAP_FILE).read_text(encoding='utf-8')
        assert detail_url('en_open1') in sitemap
        for job_id in ('en_closed1', 'en_cancel1', 'en_secondary', 'en_thin'):
            assert detail_url(job_id) not in sitemap
        assert BASE_URL + '/verification-guide.html' in sitemap


class TestWriteDetailPages:
    def test_writes_pages_and_sitemap(self, tmp_path):
        jobs = [sample_job('en_a1'), sample_job('en_a2', category='Banking')]
        written = write_detail_pages(jobs, out_root=str(tmp_path))
        assert written == 2
        assert (tmp_path / 'job' / 'en_a1' / 'index.html').exists()
        assert (tmp_path / 'job' / 'en_a2' / 'index.html').exists()
        sitemap = (tmp_path / SITEMAP_FILE).read_text(encoding='utf-8')
        assert BASE_URL + '/' in sitemap
        assert detail_url('en_a1') in sitemap
        assert detail_url('en_a2') in sitemap
        assert '<urlset' in sitemap and '</urlset>' in sitemap

    def test_orphan_dirs_removed(self, tmp_path):
        stale = tmp_path / 'job' / 'en_gone'
        stale.mkdir(parents=True)
        (stale / 'index.html').write_text('stale', encoding='utf-8')
        write_detail_pages([sample_job('en_keep')], out_root=str(tmp_path))
        assert not stale.exists()
        assert (tmp_path / 'job' / 'en_keep' / 'index.html').exists()

    def test_unsafe_ids_skipped(self, tmp_path):
        evil = sample_job('../evil')
        written = write_detail_pages([evil, sample_job('en_ok1')], out_root=str(tmp_path))
        assert written == 1
        assert (tmp_path / 'job' / 'en_ok1' / 'index.html').exists()
        job_root = tmp_path / 'job'
        assert sorted(p.name for p in job_root.iterdir()) == ['en_ok1']

    def test_lastmod_from_last_verified(self, tmp_path):
        write_detail_pages([sample_job('en_lm1')], out_root=str(tmp_path))
        sitemap = (tmp_path / SITEMAP_FILE).read_text(encoding='utf-8')
        assert '<lastmod>2026-11-03</lastmod>' in sitemap


class TestVerificationChip:
    """Phase 3: honest source-of-information chip on detail pages.

    Known statuses get a labelled chip; unknown or missing statuses
    get nothing (no invented labels)."""

    def test_official_verified_chip(self):
        page = render_detail_page(
            sample_job(verification_status='official_verified'), [])
        assert 'Official source' in page
        assert 'trust-official' in page
        assert 'job-verification' in page

    def test_secondary_source_chip(self):
        page = render_detail_page(
            sample_job(verification_status='secondary_source_only'), [])
        assert 'Secondary source' in page
        assert 'trust-secondary' in page

    def test_unknown_status_gets_no_chip(self):
        page = render_detail_page(
            sample_job(verification_status='some-future-status'), [])
        assert 'job-verification' not in page

    def test_missing_status_gets_no_chip(self):
        page = render_detail_page(sample_job(verification_status=None), [])
        assert 'job-verification' not in page
