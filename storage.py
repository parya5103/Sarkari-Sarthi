import logging
import os
import json
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# Directory for storing job data and manifest
JOB_DIR = 'jobs'
MANIFEST_FILE = os.path.join(JOB_DIR, 'job_manifest.json')

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
        safe_id = os.path.basename(str(job['id']))
        job_file_path = os.path.join(JOB_DIR, f"{safe_id}.json")
        try:
            with open(job_file_path, 'w', encoding='utf-8') as f:
                json.dump(job, f, indent=2, ensure_ascii=False)
            logger.info(f"  [{i}/{len(jobs)}] ✅ Saved: {job['title'][:60]}... to {os.path.basename(job_file_path)}")
            saved_count += 1
        except Exception as e:
            logger.error(f"Error saving job file for ID {job.get('id', 'unknown')} at {job_file_path}: {e}")

    logger.info(f"\n📁 Successfully saved {saved_count}/{len(jobs)} job files to '{JOB_DIR}' directory.")
    return saved_count

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
            safe_id = os.path.basename(str(job_entry.get('id', 'unknown')))
            job_file_path = os.path.join(JOB_DIR, f"{safe_id}.json")
            if os.path.exists(job_file_path):
                try:
                    os.remove(job_file_path)
                    logger.info(f"🗑️ Deleted expired job file: {os.path.basename(job_file_path)}")
                except OSError as e:
                    logger.error(f"Error deleting expired job file {job_file_path}: {e}")

    manifest['jobs'] = active_jobs
    manifest['active_jobs'] = len(active_jobs)
    manifest['expired_jobs'] = expired_count
    manifest['total_jobs'] = len(active_jobs)
    save_manifest(manifest)
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
