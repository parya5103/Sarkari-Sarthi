#!/usr/bin/env python3
"""
SarkariSarthi 2.0 - Job Fetcher (Fixed Version for GitHub Actions)
AI-powered job scraper for Indian government and private sector jobs
"""

import logging
import os
import sys

from datetime import datetime

import concurrent.futures

# Import from refactored modules
from storage import (
    JOB_DIR, MANIFEST_FILE, load_manifest, save_manifest,
    save_jobs_to_files, delete_expired_jobs, update_seo_keywords,
    is_valid_job_id
)
from scraper import JOB_PORTALS, fetch_page_content, scrape_generic_job_site, _scrape_single_portal, scrape_all_job_portals
from job_schema import normalize_job, is_duplicate_job, advertisement_key
from official_sources import fetch_employment_news_jobs, SOURCE_NAME as OFFICIAL_SOURCE_NAME
from detail_pages import write_detail_pages
from parser import (
    download_pdf, extract_text_from_pdf, summarize_job_description,
    extract_important_dates_and_links, auto_detect_job_category,
    extract_trending_skills, process_job_content
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Main Execution ---

def _publish_detail_pages():
    """Regenerate static job detail pages + sitemap from the manifest.

    Non-fatal on purpose: a template failure must not block the data
    pipeline, but it is logged loudly in the workflow run.
    """
    try:
        manifest = load_manifest()
        write_detail_pages(manifest.get('jobs', []))
    except Exception as e:
        logger.error(f"❌ Failed to regenerate job detail pages: {e}")


def main():
    """Main function to orchestrate job fetching process"""
    print("=" * 60)
    print("🚀 SarkariSarthi 2.0 Job Fetcher Started (for GitHub Actions)")
    print("=" * 60)

    os.makedirs(JOB_DIR, exist_ok=True)
    logger.info(f"📁 Jobs data directory ready: {os.path.abspath(JOB_DIR)}")

    manifest = load_manifest()
    existing_job_urls = {job['url'] for job in manifest.get('jobs', [])}
    existing_adv_keys = {advertisement_key(job) for job in manifest.get('jobs', [])}
    existing_adv_keys.discard(None)
    logger.info(f"📋 Existing jobs in manifest: {len(existing_job_urls)}")

    all_scraped_jobs = scrape_all_job_portals()

    # Official source (Phase 3): Employment News rows arrive already
    # complete with verified listing data. They must NOT be re-fetched
    # through process_job_content, so they are kept in a separate list.
    official_jobs = fetch_employment_news_jobs()
    all_scraped_jobs.extend(official_jobs)

    if not all_scraped_jobs:
        logger.warning("⚠️ WARNING: No jobs were scraped from any portal!")
        logger.warning("This might be due to: Network issues, website blocking, or structural changes.")
        delete_expired_jobs()
        update_seo_keywords()
        _publish_detail_pages()
        print("\n" + "=" * 60)
        print("📈 FINAL SUMMARY (No new jobs scraped)")
        print("=" * 60)
        final_manifest = load_manifest()
        print(f"📊 Total active jobs in system: {final_manifest.get('active_jobs', 0)}")
        print(f"🕒 Last updated: {final_manifest.get('last_updated', 'Unknown')}")
        print("=" * 60)
        # Honest failure (master plan Phase 7): zero jobs scraped from
        # every portal means the pipeline is broken. Fail the run
        # instead of silently pretending the site is up to date.
        sys.exit(1)

    logger.info(f"\n🔍 Processing {len(all_scraped_jobs)} raw scraped jobs...")

    duplicate_count = 0
    jobs_to_process = []
    official_to_add = []

    for job_candidate in all_scraped_jobs:
        dup_reason = is_duplicate_job(job_candidate, existing_job_urls, existing_adv_keys)
        if dup_reason:
            duplicate_count += 1
            logger.info(f"Duplicate skipped ({dup_reason}): {job_candidate.get('title', '')[:60]}")
            continue
        # Security: drop any record whose ID would be unsafe as a
        # filesystem path component (jobs/<id>.json).
        if not is_valid_job_id(job_candidate.get('id')):
            logger.warning(f"⛔ Dropping scraped job with unsafe ID: {job_candidate.get('id')!r}")
            continue
        if job_candidate.get('source') == OFFICIAL_SOURCE_NAME:
            # Official listing rows are already complete records.
            official_to_add.append(job_candidate)
        else:
            jobs_to_process.append(job_candidate)
        existing_job_urls.add(job_candidate['url'])
        adv_key = advertisement_key(job_candidate)
        if adv_key:
            existing_adv_keys.add(adv_key)

    # Official records are normalized immediately (no per-job fetch).
    new_jobs_to_add = [normalize_job(j) for j in official_to_add]

    if jobs_to_process:
        logger.info(f"🔄 Concurrently processing {len(jobs_to_process)} unique jobs...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_job = {executor.submit(process_job_content, job): job for job in jobs_to_process}

            for future in concurrent.futures.as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    processed_job = future.result()
                    new_jobs_to_add.append(normalize_job(processed_job))
                except Exception as exc:
                    logger.error(f"❌ Job processing generated an exception for {job['url']}: {exc}")

    logger.info(f"📊 Processing Summary:")
    logger.info(f"  New unique jobs to save: {len(new_jobs_to_add)}")
    logger.info(f"  Duplicates skipped: {duplicate_count}")

    if new_jobs_to_add:
        saved_count = save_jobs_to_files(new_jobs_to_add)
        manifest = load_manifest()
        manifest['jobs'].extend(new_jobs_to_add)
        manifest['last_updated'] = datetime.now().isoformat()
        manifest['total_jobs'] = len(manifest['jobs'])
        manifest['active_jobs'] = len(manifest['jobs'])
        save_manifest(manifest)

        logger.info(f"\n✅ Successfully added {saved_count} new jobs to the system!")
    else:
        logger.info("\n📋 No new unique jobs to add (all were duplicates or none found).")

    delete_expired_jobs()
    update_seo_keywords()
    _publish_detail_pages()

    final_manifest = load_manifest()
    print("\n" + "=" * 60)
    print("📈 FINAL SYSTEM SUMMARY")
    print("=" * 60)
    print(f"✅ SarkariSarthi 2.0 Job Fetcher completed successfully!")
    print(f"📊 Total active jobs currently in system: {final_manifest.get('active_jobs', 0)}")
    print(f"📁 Jobs directory: {os.path.abspath(JOB_DIR)}")
    print(f"📋 Manifest file: {os.path.abspath(MANIFEST_FILE)}")
    print(f"🕒 Last updated: {final_manifest.get('last_updated', 'Unknown')}")
    print("=" * 60)

def test_single_site():
    """Test function for debugging a single site."""
    test_url = "https://www.freejobalert.com"
    logger.info(f"🧪 Testing single site: {test_url}")

    os.makedirs(JOB_DIR, exist_ok=True)
    jobs = scrape_generic_job_site(test_url, "freejobalert_test")

    if jobs:
        logger.info(f"✅ Test successful! Found {len(jobs)} jobs (first 5 shown):")
        for i, job in enumerate(jobs[:5], 1):
            logger.info(f"  {i}. Title: {job['title'][:60]}... URL: {job['url']}")

        processed_test_jobs = [process_job_content(job) for job in jobs[:5]]
        save_jobs_to_files(processed_test_jobs)
        return True
    else:
        logger.warning("❌ Test failed - no jobs found from the test site.")
        return False

if __name__ == "__main__":
    main()
