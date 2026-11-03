"""Static job detail pages + sitemap (master plan Phase 5).

The listing page stays JavaScript-driven, but every job also gets a
static prerendered HTML page at job/<id>/index.html with:
- stable readable URL: /sarkari-sarthi/job/<id>/
- unique title and meta description
- canonical URL
- breadcrumb navigation
- official notification/application links when verified
- source attribution and last-verified date
- related jobs in the same category

JobPosting JSON-LD is built ONLY from verified fields. Unknown
fields (salary, location, organization, dates) are omitted from the
JSON-LD, never invented. Jobs without a verified last date get no
validThrough entry at all.

The root sitemap.xml lists the homepage and every generated detail
page with an honest lastmod (the job's last_verified timestamp).
"""
import html
import json
import logging
import os
from datetime import datetime

from job_schema import parse_date
from storage import is_valid_job_id

logger = logging.getLogger(__name__)

BASE_URL = 'https://gogocompany.in/sarkari-sarthi'
DETAIL_DIR = 'job'
SITEMAP_FILE = 'sitemap.xml'
NOT_SPECIFIED = 'Not specified in official notification'
MAX_RELATED = 5


def detail_url(job_id):
    return BASE_URL + '/job/' + job_id + '/'


def _esc(value):
    return html.escape(str(value), quote=True)


def _iso_date(value):
    parsed = parse_date(value)
    return parsed.strftime('%Y-%m-%d') if parsed else None


def job_posting_jsonld(job, page_url):
    """JobPosting structured data, verified fields only."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'JobPosting',
        'title': job.get('title') or '',
        'description': job.get('description') or '',
        'url': page_url,
        'identifier': {'@type': 'PropertyValue', 'value': job.get('id')},
    }
    if not data['title'] or not data['description']:
        return None
    dates = job.get('important_dates') or {}
    last_iso = _iso_date(dates.get('last_date') or job.get('last_date'))
    if last_iso:
        data['validThrough'] = last_iso + 'T23:59:59'
    published_iso = _iso_date(job.get('published_date'))
    if published_iso:
        data['datePosted'] = published_iso
    if job.get('organization'):
        data['hiringOrganization'] = {
            '@type': 'Organization',
            'name': job['organization'],
        }
    if job.get('official_application_url'):
        data['directApply'] = True
    return data


def _info_row(label, value, escape_value=True):
    shown = _esc(value) if escape_value else value
    return '<tr><th scope="row">' + label + '</th><td>' + shown + '</td></tr>'


def render_detail_page(job, related):
    """Return the full HTML string for one job detail page."""
    job_id = job['id']
    page_url = detail_url(job_id)
    dates = job.get('important_dates') or {}
    title = _esc(job.get('title') or 'Government Job Notification')
    org = job.get('organization')
    status = str(job.get('status') or 'active').lower()

    meta_source = (job.get('description') or job.get('title') or 'Government job notification.')
    meta_desc = _esc(meta_source[:157] + '...' if len(meta_source) > 160 else meta_source)

    ld = job_posting_jsonld(job, page_url)
    ld_block = ''
    if ld:
        # JSON unicode-escape < > & so untrusted job text can never
        # close the JSON-LD script element early (script injection).
        ld_json = json.dumps(ld, ensure_ascii=False)
        ld_json = (ld_json.replace('<', chr(92) + 'u003c')
                          .replace('>', chr(92) + 'u003e')
                          .replace('&', chr(92) + 'u0026'))
        ld_block = ('<script type="application/ld+json">' +
                    ld_json +
                    '</script>')

    status_banner = ''
    if status == 'cancelled':
        status_banner = ('<div class="job-status-banner status-cancelled">This recruitment has been '
                         'marked cancelled. Verify on the official website before relying on it.</div>')

    rows = []
    rows.append(_info_row('Organization', org or NOT_SPECIFIED))
    if job.get('department'):
        rows.append(_info_row('Department', job['department']))
    rows.append(_info_row('Category', job.get('category') or 'General'))
    if job.get('vacancies'):
        rows.append(_info_row('Vacancies', job['vacancies']))
    if job.get('qualification'):
        rows.append(_info_row('Qualification', job['qualification']))
    if job.get('age_limit'):
        rows.append(_info_row('Age Limit', job['age_limit']))
    rows.append(_info_row('Last Date', dates.get('last_date') or job.get('last_date') or NOT_SPECIFIED))
    if dates.get('application_start_date') or job.get('application_start_date'):
        rows.append(_info_row('Application Start Date',
                              dates.get('application_start_date') or job.get('application_start_date')))
    if dates.get('exam_date'):
        rows.append(_info_row('Exam Date', dates['exam_date']))
    if job.get('published_date'):
        rows.append(_info_row('Published', job['published_date']))
    rows.append(_info_row('Advertisement No', job.get('advertisement_no') or NOT_SPECIFIED))
    info_table = chr(10).join(rows)

    links = []
    if job.get('official_notification_url'):
        links.append('<a class="detail-link" href="' + _esc(job['official_notification_url']) +
                     '" target="_blank" rel="noopener noreferrer">Official Notification</a>')
    if job.get('official_application_url'):
        links.append('<a class="detail-link" href="' + _esc(job['official_application_url']) +
                     '" target="_blank" rel="noopener noreferrer">Official Application Page</a>')
    source_url = job.get('original_source_url') or job.get('url')
    if source_url:
        links.append('<a class="detail-link secondary" href="' + _esc(source_url) +
                     '" target="_blank" rel="noopener noreferrer">Original Source Page</a>')
    links_block = chr(10).join(links)

    last_verified = str(job.get('last_verified') or '')
    verified_line = 'Last verified: ' + _esc(last_verified[:10]) if last_verified else 'Last verified: unknown'
    source_line = _esc(job.get('source') or 'unknown source')

    related_items = []
    for rel in related:
        # Defensive filtering (write_detail_pages also filters):
        # related links never show expired or cancelled vacancies,
        # and only same-category jobs are related to this one.
        if not isinstance(rel, dict) or rel.get('id') == job_id:
            continue
        if rel.get('category') != job.get('category'):
            continue
        if str(rel.get('status') or 'active').lower() in ('expired', 'cancelled'):
            continue
        related_items.append('<li><a href="' + detail_url(rel['id']) + '">' +
                              _esc(rel.get('title') or rel['id']) + '</a></li>')
    related_block = ''
    if related_items:
        related_block = ('<section class="related-jobs"><h2>Related Government Jobs</h2><ul>' +
                         chr(10).join(related_items) + '</ul></section>')

    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>''' + title + ''' - SarkariSarthi</title>
<meta name="description" content="''' + meta_desc + '''">
<link rel="canonical" href="''' + page_url + '''">
<link rel="stylesheet" href="/sarkari-sarthi/style.css">
''' + ld_block + '''
</head>
<body class="dark-mode">
<header class="header">
<nav class="navbar"><div class="nav-container">
<div class="nav-logo"><a href="/sarkari-sarthi/" style="text-decoration:none;color:inherit;">
<img src="/sarkari-sarthi/ai-powered-icon.png" alt="SarkariSarthi logo" class="logo-icon">
<span class="logo-text">SarkariSarthi 2.0</span></a></div>
</div></nav>
</header>
<main class="container detail-page">
<nav class="breadcrumb" aria-label="Breadcrumb">
<a href="/sarkari-sarthi/">Home</a> &gt;
<a href="/sarkari-sarthi/#jobs">Government Jobs</a> &gt;
<span>''' + title + '''</span>
</nav>
''' + status_banner + '''
<article class="job-detail">
<h1>''' + title + '''</h1>
<table class="job-info-table">
''' + info_table + '''
</table>
<section class="job-description">
<h2>Notification Details</h2>
<p>''' + _esc(job.get('description') or 'No description available.') + '''</p>
</section>
<div class="job-links">
''' + links_block + '''
</div>
<p class="job-source">Source: ''' + source_line + '''. ''' + verified_line + '''.</p>
<p class="job-disclaimer">Sarkari Sarthi is an independent information portal, not a government
website. Always verify details on the official notification before applying.</p>
</article>
''' + related_block + '''
</main>
</body>
</html>'''
    return page


def _remove_orphan_detail_dirs(detail_root, active_ids):
    """Delete job/<id>/ directories whose id left the manifest.

    Containment-checked: only directories physically inside
    detail_root are ever removed.
    """
    if not os.path.isdir(detail_root):
        return 0
    import shutil
    removed = 0
    root_abs = os.path.abspath(detail_root)
    for name in os.listdir(detail_root):
        path = os.path.join(detail_root, name)
        if name in active_ids or not os.path.isdir(path):
            continue
        resolved = os.path.realpath(path)
        if not resolved.startswith(root_abs + os.sep):
            logger.warning('Skipping suspicious detail dir outside root: %s', name)
            continue
        shutil.rmtree(path)
        removed += 1
    return removed


def write_detail_pages(jobs, out_root='.'):
    """Write job/<id>/index.html for every safe job id + sitemap.xml.

    Returns the number of pages written. Invalid job ids are skipped
    (never written, never traversed). Failures are logged and do not
    raise: the data pipeline result is unaffected.
    """
    detail_root = os.path.join(out_root, DETAIL_DIR)
    os.makedirs(detail_root, exist_ok=True)

    safe_jobs = []
    seen = set()
    for job in jobs:
        if not isinstance(job, dict):
            continue
        job_id = job.get('id')
        if not is_valid_job_id(job_id) or job_id in seen:
            continue
        seen.add(job_id)
        safe_jobs.append(job)

    written = 0
    for job in safe_jobs:
        related = [
            rel for rel in safe_jobs
            if rel['id'] != job['id']
            and rel.get('category') == job.get('category')
            and str(rel.get('status') or 'active').lower() not in ('expired', 'cancelled')
        ][:MAX_RELATED]
        try:
            page = render_detail_page(job, related)
            page_dir = os.path.join(detail_root, job['id'])
            os.makedirs(page_dir, exist_ok=True)
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(page)
            written += 1
        except Exception as e:
            logger.error('Failed to render detail page for %s: %s', job.get('id'), e)

    removed = _remove_orphan_detail_dirs(detail_root, seen)
    if removed:
        logger.info('Removed %d stale job detail directory/directories.', removed)

    _write_sitemap(safe_jobs, out_root)
    logger.info('Job detail pages written: %d', written)
    return written


def _write_sitemap(jobs, out_root='.'):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    def url_entry(loc, lastmod):
        if lastmod:
            return ('<url><loc>' + loc + '</loc><lastmod>' + str(lastmod)[:10] +
                    '</lastmod></url>')
        return '<url><loc>' + loc + '</loc></url>'

    lines.append(url_entry(BASE_URL + '/', ''))
    for job in jobs:
        verified = job.get('last_verified') or ''
        lines.append(url_entry(detail_url(job['id']), verified))
    lines.append('</urlset>')
    sitemap_path = os.path.join(out_root, SITEMAP_FILE)
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(chr(10).join(lines))
