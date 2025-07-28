if new_jobs_added == 0:
    logger.warning("⚠ No jobs scraped – adding dummy job to ensure GitHub commit.")

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
    with open(dummy_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_job, f, indent=2, ensure_ascii=False)

    manifest['jobs'].append(dummy_job)
    manifest['total_jobs'] += 1
    manifest['active_jobs'] += 1
    save_manifest(manifest)
    logger.info("✅ Dummy job saved.")
