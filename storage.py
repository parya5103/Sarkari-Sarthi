import logging
import os
import json
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# Directory for storing job data and manifest
JOB_DIR = 'jobs'
MANIFEST_FILE = os.path.join(JOB_DIR, 'job_manifest.json')

# Security: strict allowlist for job IDs. Job IDs reach filesystem
# operations (jobs/<id>.json, temp_<id>.pdf) from scraped URLs and from
# manually entered admin records, so they are EXTERNAL INPUT and must
# never be trusted as path components.
JOB_ID_PATTERN = re.compile(r'[A-Za-z0-9_-]{1,80}')


def is_valid_job_id(job_id):
    """True only for IDs matching the strict [A-Za-z0-9_-]{1,80} allowlist."""
    return (
        isinstance(job_id, str)
        and bool(job_id)
        and bool(JOB_ID_PATTERN.fullmatch(job_id))
    )


def job_file_path(job_id):
    """Return the validated jobs/<id>.json path for a job ID.

    Rejects traversal ('../'), encoded traversal, absolute paths,
    separators, over-long IDs and anything outside the allowlist.
    Also verifies the RESOLVED path stays inside the jobs directory
    (realpath containment, symlink-safe), so no write or delete can
    ever escape JOB_DIR.
    """
    if not is_valid_job_id(job_id):
        raise ValueError('Invalid job ID: %r' % (job_id,))
    job_dir_abs = os.path.abspath(JOB_DIR)
    path = os.path.join(JOB_DIR, job_id + '.json')
    resolved = os.path.realpath(path)
    if not resolved.startswith(job_dir_abs + os.sep):
        raise ValueError('Resolved job path escapes the jobs directory: %r' % (path,))
    return path

def load_manifest():
    """Load job manifest from file or create default structure if it doesn't exist or is invalid."""
    if not os.path.exists(MANIFEST_FILE):
        logger.info(f"Manifest file not found at {MANIFEST_FILE}. Creating a new one.")
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }
    try:
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
            if not isinstance(manifest_data, dict) or "jobs" not in manifest_data:
                raise ValueError("Manifest file has an invalid structure.")
            return manifest_data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from manifest file {MANIFEST_FILE}: {e}. Recreating manifest.")
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }
    except Exception as e:
        logger.error(f"Error loading manifest from {MANIFEST_FILE}: {e}. Recreating manifest.")
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }

def save_manifest(manifest):
    """Save job manifest to file."""
    try:
        os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Manifest saved: {MANIFEST_FILE}")
    except Exception as e:
        logger.error(f"Error saving manifest to {MANIFEST_FILE}: {e}")

def save_jobs_to_files(jobs):
    """Save jobs to individual JSON files."""
    saved_count = 0
    if not jobs:
        logger.info("No new jobs to save to individual files.")
        return 0

    logger.info(f"\n💾 Saving {len(jobs)} new jobs to individual files in '{JOB_DIR}'...")
    os.makedirs(JOB_DIR, exist_ok=True)

    for i, job in enumerate(jobs, 1):
        try:
            safe_path = job_file_path(job.get('id'))
        except ValueError as e:
            logger.error(f"  [{i}/{len(jobs)}] ⛔ Skipping job with unsafe ID: {e}")
            continue
        try:
            with open(safe_path, 'w', encoding='utf-8') as f:
                json.dump(job, f, indent=2, ensure_ascii=False)
            logger.info(f"  [{i}/{len(jobs)}] ✅ Saved: {job['title'][:60]}... to {os.path.basename(safe_path)}")
            saved_count += 1
        except Exception as e:
            logger.error(f"Error saving job file for ID {job.get('id', 'unknown')} at {safe_path}: {e}")

    logger.info(f"\n📁 Successfully saved {saved_count}/{len(jobs)} job files to '{JOB_DIR}' directory.")
    return saved_count

def _remove_orphan_job_files(manifest):
    """Delete individual job JSON files that are no longer referenced by
    the manifest (e.g. records removed by a manifest cleanup or link
    filter). Keeps the jobs/ directory in sync with the manifest."""
    if not os.path.isdir(JOB_DIR):
        return
    active_ids = {job_entry.get('id') for job_entry in manifest.get('jobs', [])}
    removed = 0
    for file_name in os.listdir(JOB_DIR):
        if not file_name.endswith('.json') or file_name == os.path.basename(MANIFEST_FILE):
            continue
        file_id = file_name[:-len('.json')]
        if file_id in active_ids:
            continue
        file_path = os.path.join(JOB_DIR, file_name)
        job_dir_abs = os.path.abspath(JOB_DIR)
        resolved = os.path.realpath(file_path)
        if not resolved.startswith(job_dir_abs + os.sep):
            logger.warning(f"Skipping suspicious job file outside jobs dir: {file_name}")
            continue
        try:
            os.remove(file_path)
            removed += 1
        except OSError as e:
            logger.error(f"Error removing orphaned job file {file_path}: {e}")
    if removed:
        logger.info(f"\U0001f5d1\ufe0f Removed {removed} orphaned job file(s) not present in the manifest.")

def delete_expired_jobs():
    """Delete expired jobs based on 'last_date' or if older than 30 days (scraped_at)."""
    logger.info("\n🧹 Cleaning up expired jobs...")
    manifest = load_manifest()
    active_jobs = []
    expired_count = 0
    current_date = datetime.now()

    jobs_in_manifest = manifest.get('jobs', [])
    if not jobs_in_manifest:
        logger.info("No jobs in manifest to clean.")
        manifest['expired_jobs'] = 0
        save_manifest(manifest)
        _remove_orphan_job_files(manifest)
        return

    for job_entry in jobs_in_manifest:
        is_expired = False
        if 'important_dates' in job_entry and 'last_date' in job_entry['important_dates']:
            date_str = job_entry['important_dates']['last_date']
            parsed_date = None
            for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %b %Y', '%d %B %Y'):
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue

            if parsed_date:
                if parsed_date.date() < current_date.date():
                    is_expired = True
                    logger.debug(f"Job {job_entry['id']} expired by last_date: {date_str}")
            else:
                logger.warning(f"Could not parse 'last_date' '{date_str}' for job {job_entry.get('id', 'unknown')}. Skipping date-based expiry.")

        if not is_expired and 'scraped_at' in job_entry:
            try:
                scraped_date = datetime.fromisoformat(job_entry['scraped_at'])
                if (current_date - scraped_date).days > 15:
                    is_expired = True
                    logger.debug(f"Job {job_entry['id']} expired by age (scraped_at): {job_entry['scraped_at']}")
            except ValueError:
                logger.warning(f"Could not parse 'scraped_at' for job {job_entry.get('id', 'unknown')}. Skipping age-based expiry.")

        if not is_expired:
            active_jobs.append(job_entry)
        else:
            expired_count += 1
            try:
                safe_path = job_file_path(job_entry.get('id'))
            except ValueError as e:
                logger.warning(f"Expired job had an unsafe ID; removing from manifest only: {e}")
                safe_path = None
            if safe_path and os.path.exists(safe_path):
                try:
                    os.remove(safe_path)
                    logger.info(f"🗑️ Deleted expired job file: {os.path.basename(safe_path)}")
                except OSError as e:
                    logger.error(f"Error deleting expired job file {safe_path}: {e}")

    manifest['jobs'] = active_jobs
    manifest['active_jobs'] = len(active_jobs)
    manifest['expired_jobs'] = expired_count
    manifest['total_jobs'] = len(active_jobs)
    save_manifest(manifest)
    _remove_orphan_job_files(manifest)
    logger.info(f"✅ Cleanup complete: Deleted {expired_count} expired jobs.")

SEO_STOPWORDS = {'recruitment', 'apply', 'online', 'post', 'posts', 'vacancies', 'notification', 'various', 'department', 'board', 'commission', 'service', '2023', '2024', '2025', '2026', 'india', 'state', 'vacancy', 'examination', 'exam'}

def update_seo_keywords():
    """Extract keywords from jobs and update index.html."""
    logger.info("\n🔍 Updating SEO keywords based on active jobs...")
    try:
        manifest = load_manifest()
    except Exception as e:
        logger.error(f"Failed to load manifest for SEO update: {e}")
        return

    jobs = manifest.get('jobs', [])
    if not jobs:
        logger.info("No jobs found to extract keywords.")
        return

    words = []
    base_keywords = ['sarkari job', 'government jobs', 'sarkari naukri', 'indian government jobs', 'job portal']

    for job in jobs:
        title = job.get('title', '')
        category = job.get('category', '')

        t_lower = title.lower()
        tokens = re.findall(r'\b[a-zA-Z]{4,}\b', t_lower)
        filtered_tokens = [t for t in tokens if t not in SEO_STOPWORDS]

        words.extend(filtered_tokens)
        if category:
            words.append(category.lower())

    from collections import Counter
    word_counts = Counter(words)
    top_words = [word for word, count in word_counts.most_common(15)]

    all_keywords = list(dict.fromkeys(base_keywords + top_words))
    keywords_str = ", ".join(all_keywords)

    html_path = 'index.html'
    try:
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            pattern = r'<meta name="keywords" content="[^"]*">'
            replacement = f'<meta name="keywords" content="{keywords_str}">'

            if re.search(pattern, html_content):
                new_html = re.sub(pattern, replacement, html_content)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                logger.info(f"✅ Successfully updated index.html with {len(all_keywords)} SEO keywords.")
            else:
                logger.warning("Could not find keywords meta tag in index.html to update.")
    except Exception as e:
        logger.error(f"Failed to update index.html for SEO: {e}")
