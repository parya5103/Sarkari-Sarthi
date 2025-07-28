def main():
    """Main function to orchestrate job fetching process"""
    logger.info("🚀 SarkariSarthi 2.0 Job Fetcher started.")
    
    # Create jobs directory
    os.makedirs(JOB_DIR, exist_ok=True)
    
    # Load existing manifest
    manifest = load_manifest()
    existing_job_urls = {job['url'] for job in manifest.get('jobs', [])}
    
    # Scrape all job portals
    logger.info("🌐 Starting comprehensive job scraping...")
    all_new_jobs = scrape_all_job_portals()
    
    # Process and filter new jobs
    new_jobs_added = 0
    for job in all_new_jobs:
        if job['url'] in existing_job_urls:
            logger.debug(f"⏩ Skipping existing job: {job['title']}")
            continue
        
        logger.info(f"🧠 Processing new job: {job['title']} from {job['source']}")
        
        # Process job content with AI
        processed_job = process_job_content(job)
        
        # Save individual job file
        job_file_path = os.path.join(JOB_DIR, f"{processed_job['id']}.json")
        try:
            with open(job_file_path, 'w', encoding='utf-8') as f:
                json.dump(processed_job, f, indent=2, ensure_ascii=False)
            
            manifest['jobs'].append(processed_job)
            new_jobs_added += 1
            logger.info(f"✅ Saved job: {processed_job['title']}")
            
        except Exception as e:
            logger.error(f"❌ Error saving job {processed_job['id']}: {e}")
    
    # If no jobs were scraped, add a dummy job
    if new_jobs_added == 0:
        logger.warning("⚠ No jobs scraped – adding fallback dummy job.")
        dummy_job = {
            "id": "dummy-ssc-2025",
            "title": "SSC CGL 2025 – Apply Online",
            "url": "https://example.com/ssc-cgl",
            "source": "fallback-dummy",
            "description": "Apply now for SSC CGL 2025. Graduate level vacancies.",
            "pdf_link": None,
            "important_dates": {
                "last_date": "2025-09-15"
            },
            "category": "SSC",
            "skills": ["General Knowledge", "Reasoning", "Quantitative Aptitude"],
            "scraped_at": datetime.now().isoformat()
        }

        dummy_path = os.path.join(JOB_DIR, f"{dummy_job['id']}.json")
        try:
            with open(dummy_path, 'w', encoding='utf-8') as f:
                json.dump(dummy_job, f, indent=2, ensure_ascii=False)
            manifest['jobs'].append(dummy_job)
            manifest['total_jobs'] += 1
            manifest['active_jobs'] += 1
            logger.info(f"✅ Dummy job written to: {dummy_path}")
        except Exception as e:
            logger.error(f"❌ Failed to write dummy job: {e}")

    # Update manifest
    manifest['last_updated'] = datetime.now().isoformat()
    manifest['total_jobs'] = len(manifest['jobs'])
    manifest['active_jobs'] = len(manifest['jobs'])
    save_manifest(manifest)
    
    # Clean up expired jobs
    delete_expired_jobs()
    
    logger.info(f"🏁 Job fetch completed. New jobs added: {new_jobs_added}")
    logger.info(f"📊 Total active jobs: {len(manifest['jobs'])}")
