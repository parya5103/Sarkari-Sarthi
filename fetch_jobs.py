#!/usr/bin/env python3
"""
SarkariSarthi 2.0 - Job Fetcher (Fixed Version for GitHub Actions)
AI-powered job scraper for Indian government and private sector jobs
"""

import logging
import os
import json
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import fitz # PyMuPDF
import pdfplumber
import hashlib
import re
import urllib.request
import time
import random

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory for storing job data and manifest - IMPORTANT: Changed back to 'jobs'
JOB_DIR = 'jobs'
MANIFEST_FILE = os.path.join(JOB_DIR, 'job_manifest.json')

# Comprehensive list of Indian job portals (Government + Private)
JOB_PORTALS = {
    # Government Job Portals
    'government': [
        'https://www.freejobalert.com',
        'https://www.sarkariresult.com',
        'https://www.sarkarinaukri.com',
        'https://www.mysarkarinaukri.com',
        'https://bharatsarkarijob.com',
        'https://allgovernmentjobs.in',
        'https://www.sarkariexam.com',
        'https://www.rojgarresult.com',
        'https://www.jobriya.com',
        'https://www.sarkari-naukri.info',
        'https://www.freshersworld.com/government-jobs'
    ],
    # Private Job Portals
    'private': [
    "https://www.sarkarinaukridaily.in/",
    "https://www.fresherslive.com/govt-jobs",
    "https://www.jobsarkari.com/",
    "https://www.naukrigulf.com/government-jobs",
    "https://rojgarresult.com/",
    "https://www.employmentnews.gov.in/",
    "https://www.latestgovtjobs.in/",
    "https://www.indiagovtjobs.in/",
    "https://www.kirannewsagency.com/",
    "https://www.mysarkarinaukri.com/",
    "https://sarkariprep.in/",
    "https://linkingsky.com/ '
    ]
}

# --- Utility Functions ---

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
            # Basic validation for manifest structure
            if not isinstance(manifest_data, dict) or "jobs" not in manifest_data:
                raise ValueError("Manifest file has an invalid structure.")
            return manifest_data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from manifest file {MANIFEST_FILE}: {e}. Recreating manifest.")
        # Return an empty manifest if file is corrupted
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
        # Ensure the directory for the manifest file exists
        os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Manifest saved: {MANIFEST_FILE}")
    except Exception as e:
        logger.error(f"Error saving manifest to {MANIFEST_FILE}: {e}")

def fetch_page_content(url, timeout=15, retries=3):
    """Fetch page content with retry logic and proper headers."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    for attempt in range(retries):
        try:
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(2, 4))

            response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            logger.info(f"✅ Successfully fetched: {url} (Status: {response.status_code})")
            return response.content

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            if attempt == retries - 1:
                logger.error(f"❌ Failed to fetch {url} after {retries} attempts")
                return None
    return None

def download_pdf(url, save_path):
    """Download PDF file from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Ensure directory exists before writing file
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Downloaded PDF from {url} to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return False

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF and pdfplumber as fallback."""
    text = ""
    try:
        # Try PyMuPDF first
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        if text.strip():
            logger.debug(f"Successfully extracted text using PyMuPDF from {pdf_path}")
            return text
    except Exception as e:
        logger.warning(f"PyMuPDF failed for {pdf_path}: {e}. Falling back to pdfplumber.")

    try:
        # Fallback to pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if text.strip():
            logger.debug(f"Successfully extracted text using pdfplumber from {pdf_path}")
            return text
    except Exception as e:
        logger.error(f"pdfplumber also failed for {pdf_path}: {e}")

    logger.warning(f"Could not extract any text from PDF: {pdf_path}")
    return text

def summarize_job_description(text):
    """Summarize job description (simple truncation for now)."""
    if not text:
        return "No description available"

    if len(text) > 500:
        return text[:497] + "..."
    return text

def extract_important_dates_and_links(text):
    """Extract important dates and links from job text."""
    dates = {}
    links = []

    if not text:
        return dates, links

    # Date patterns (expanded and ordered by specificity)
    date_patterns = [
        r'(?:Last Date|Application Deadline|Closing Date|Apply Before)\s*[:-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(?:Exam Date|Test Date)\s*[:-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})' # General date pattern (DD-MM-YYYY or DD/MM/YYYY)
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if 'last' in pattern.lower() or 'deadline' in pattern.lower() or 'closing' in pattern.lower():
                dates['last_date'] = match
            elif 'exam' in pattern.lower() or 'test' in pattern.lower():
                dates['exam_date'] = match
            else:
                # Only add if it's not already covered by more specific types
                if 'found_date' not in dates:
                    dates['found_date'] = match

    # Link patterns - more robust to capture various URL forms
    link_pattern = r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    links = re.findall(link_pattern, text)
    # Deduplicate links
    links = list(set(links))

    return dates, links

def auto_detect_job_category(text):
    """Auto-detect job category based on text content."""
    if not text:
        return "General"

    text_lower = text.lower()

    # Category keywords mapping
    categories = {
        'Banking': ['bank', 'banking', 'sbi', 'pnb', 'icici', 'hdfc', 'axis', 'clerk', 'po', 'probationary officer', 'rbi'],
        'SSC': ['ssc', 'staff selection commission', 'cgl', 'chsl', 'mts', 'stenographer'],
        'Railway': ['railway', 'rrb', 'ntpc', 'group d', 'alp', 'technician', 'loco pilot'],
        'Police': ['police', 'constable', 'sub inspector', 'asi', 'head constable', 'security'],
        'Defence': ['defence', 'defense', 'army', 'navy', 'air force', 'bsf', 'crpf', 'cisf', 'itbp', 'agniveer'],
        'Teaching': ['teacher', 'teaching', 'education', 'professor', 'lecturer', 'principal', 'school', 'college', 'ctet', 'ugc'],
        'UPSC': ['upsc', 'ias', 'ips', 'ifs', 'civil services', 'union public service'],
        'Medical': ['doctor', 'nurse', 'medical', 'hospital', 'aiims', 'mbbs', 'pharmacist', 'health'],
        'Engineering': ['engineer', 'engineering', 'technical', 'je', 'junior engineer', 'assistant engineer', 'psu'],
        'IT': ['software', 'developer', 'programmer', 'it', 'computer', 'data analyst', 'web developer', 'cybersecurity', 'ai', 'ml'],
        'Administrative': ['clerk', 'assistant', 'officer', 'administrative', 'data entry', 'section officer', 'patwari', 'lekpal']
    }

    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category

    return "General"

def extract_trending_skills(text):
    """Extract trending skills from job text."""
    if not text:
        return []

    text_lower = text.lower()
    skills = []

    # Skills database (can be expanded)
    skill_keywords = {
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'excel', 'powerpoint', 'word',
        'communication skills', 'computer knowledge', 'ms office', 'typing',
        'general knowledge', 'reasoning', 'english', 'hindi', 'mathematics', 'aptitude',
        'leadership', 'teamwork', 'problem solving', 'data entry', 'analyst', 'cloud', 'aws', 'azure', 'gcp',
        'machine learning', 'artificial intelligence', 'data science', 'big data', 'devops', 'automation',
        'networking', 'cyber security', 'project management', 'agile', 'scrum'
    }

    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title()) # Capitalize first letter

    return list(set(skills)) # Return unique skills

# --- Core Scrapers ---

def scrape_generic_job_site(url, site_name):
    """Enhanced generic job site scraper."""
    logger.info(f"\n🔍 Scraping {site_name}...")
    html_content = fetch_page_content(url)
    jobs = []

    if not html_content:
        logger.warning(f"❌ No content fetched from {site_name}. Skipping.")
        return jobs

    try:
        soup = BeautifulSoup(html_content, 'lxml')

        # Multiple selector strategies, ordered by typical effectiveness
        job_selectors = [
            # Common patterns for job listings
            '.job-title a', '.vacancy-link', '.post-title a', '.job-link',
            # More general link patterns often containing job info
            'a[href*="jobs"]', 'a[href*="notification"]', 'a[href*="vacancy"]',
            'a[href*="recruitment"]', 'a[href*="bharti"]', 'a[href*="apply-online"]',
            # Headings containing links
            'h3 a', 'h2 a', 'h1 a',
            # Specific attributes
            'a[title*="job" i]', 'a[title*="recruitment" i]', 'a[class*="job" i]', 'a[id*="job" i]'
        ]

        logger.info(f"🔎 Trying {len(job_selectors)} different selectors for {site_name}...")

        found_links_overall = set() # To prevent adding the same URL multiple times across selectors

        for i, selector in enumerate(job_selectors):
            current_selector_links = []
            try:
                links = soup.select(selector)
                logger.debug(f"  Selector {i+1} '{selector}': Found {len(links)} raw links.")

                for link in links[:20]: # Process up to 20 links per selector
                    try:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')

                        # Skip empty titles or invalid hrefs
                        if not title or not href or len(title) < 5:
                            continue

                        full_url = urljoin(url, href).split('#')[0] # Remove fragments

                        # Basic URL validation and de-duplication
                        if not full_url.startswith('http') or full_url in found_links_overall:
                            continue

                        # Expanded job keywords for filtering (case-insensitive)
                        job_keywords = [
                            'job', 'recruitment', 'vacancy', 'notification', 'exam',
                            'apply', 'bharti', 'posts', 'officer', 'clerk', 'assistant',
                            'manager', 'engineer', 'teacher', 'constable', 'govt',
                            'government', 'sarkari', 'admission form', 'eligibility',
                            'syllabus', 'result', 'admit card', # Often related to job cycle
                            'walk-in', 'interview', 'selection', 'merit list'
                        ]

                        # More lenient filtering logic
                        # Consider it a job if title contains any keyword, or URL contains certain keywords,
                        # or if the title is relatively long (indicating a detailed post).
                        is_job = (
                            any(keyword in title.lower() for keyword in job_keywords) or
                            len(title) > 30 or # Longer titles are more likely job postings
                            any(word in full_url.lower() for word in ['job', 'recruitment', 'vacancy', 'notification', 'apply'])
                        )

                        # Exclude common non-job links
                        if any(exclude_word in full_url.lower() for exclude_word in ['login', 'register', 'contact', 'about', 'privacy', 'terms']):
                            is_job = False

                        if is_job:
                            job_id = hashlib.md5(full_url.encode()).hexdigest()
                            current_selector_links.append({
                                'id': job_id,
                                'title': title,
                                'url': full_url,
                                'source': site_name,
                                'description': '', # To be filled later
                                'pdf_link': None,
                                'important_dates': {},
                                'category': 'General', # To be filled later
                                'skills': [], # To be filled later
                                'scraped_at': datetime.now().isoformat()
                            })
                            found_links_overall.add(full_url) # Add to overall set

                    except Exception as e_link:
                        logger.debug(f"  Error processing link from {selector}: {e_link}. Skipping link.")
                        continue # Skip to the next link

                if current_selector_links:
                    jobs.extend(current_selector_links)
                    logger.info(f"  ✅ Found {len(current_selector_links)} potentially valid jobs with selector '{selector}'.")
                    # If you want to stop after the first successful selector, uncomment the line below:
                    # break # uncomment to stop after first successful selector
            except Exception as e_selector:
                logger.warning(f"  ⚠️ Selector '{selector}' failed for {site_name}: {e_selector}. Trying next selector.")
                continue

    except Exception as e_soup:
        logger.error(f"❌ Error parsing HTML content for {site_name}: {e_soup}")

    logger.info(f"📊 Total unique potential jobs found from {site_name}: {len(jobs)}")
    return jobs

def scrape_all_job_portals():
    """Scrape all configured job portals with better error handling."""
    all_jobs = []
    successful_sites = 0

    logger.info(f"\n🚀 Starting comprehensive job scraping from {len(JOB_PORTALS['government']) + len(JOB_PORTALS['private'])} portals...")

    # Scrape government job portals
    logger.info(f"\n📋 Scraping {len(JOB_PORTALS['government'])} government job portals...")
    for i, url in enumerate(JOB_PORTALS['government'], 1):
        try:
            site_name = url.split('//')[1].split('/')[0]
            logger.info(f"\n[{i}/{len(JOB_PORTALS['government'])}] Government Site: {site_name}")

            jobs = scrape_generic_job_site(url, site_name)
            if jobs:
                all_jobs.extend(jobs)
                successful_sites += 1
                logger.info(f"✅ Success! Added {len(jobs)} jobs from {site_name}")
            else:
                logger.info(f"⚠️ No jobs found from {site_name}")

            # Delay between requests
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            logger.error(f"❌ Unhandled error during scraping of {url}: {e}")

    # Scrape private job portals (limit to avoid overload for demonstration/initial run)
    # You might want to remove the `[:3]` limit for a full run in production.
    logger.info(f"\n💼 Scraping {min(3, len(JOB_PORTALS['private']))} private job portals (limited to 3 for this run)...")
    for i, url in enumerate(JOB_PORTALS['private'][:3], 1): # Limit to 3 for testing in GitHub Actions to save time
        try:
            site_name = url.split('//')[1].split('/')[0]
            logger.info(f"\n[{i}/{min(3, len(JOB_PORTALS['private']))}] Private Site: {site_name}")

            jobs = scrape_generic_job_site(url, site_name)
            if jobs:
                all_jobs.extend(jobs)
                successful_sites += 1
                logger.info(f"✅ Success! Added {len(jobs)} jobs from {site_name}")
            else:
                logger.info(f"⚠️ No jobs found from {site_name}")

            # Delay between requests
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            logger.error(f"❌ Unhandled error during scraping of {url}: {e}")

    logger.info(f"\n📈 Scraping Summary:")
    logger.info(f"  Successful sites: {successful_sites}")
    logger.info(f"  Total potential jobs found across all sites: {len(all_jobs)}")

    return all_jobs

def process_job_content(job):
    """Process individual job content to extract description, dates, category, and skills."""
    logger.info(f"🔄 Processing content for: {job['title'][:70]}...")

    job_content_text = ""

    try:
        # Check if it's a PDF link
        if job['url'].lower().endswith('.pdf') or '.pdf' in job['url'].lower():
            pdf_filename = os.path.join(JOB_DIR, f"temp_{job['id']}.pdf")
            if download_pdf(job['url'], pdf_filename):
                job_content_text = extract_text_from_pdf(pdf_filename)
                job['pdf_link'] = job['url'] # Store original PDF URL
            else:
                logger.warning(f"Failed to download or process PDF for {job['url']}. Using title as fallback content.")
                job_content_text = job['title'] # Fallback
            if os.path.exists(pdf_filename):
                # Ensure temp PDF is cleaned up in GitHub Actions to save space
                try:
                    os.remove(pdf_filename)
                except OSError as e:
                    logger.error(f"Error removing temporary PDF file {pdf_filename}: {e}")
        else:
            # Fetch job page content (with timeout to avoid hanging)
            job_page_content = fetch_page_content(job['url'], timeout=15) # Increased timeout for content pages
            if job_page_content:
                soup = BeautifulSoup(job_page_content, 'lxml')

                # Try to extract main content more robustly
                main_content_elements = soup.find_all(['article', 'main', 'div', 'section'],
                                                     class_=['job-description', 'content', 'post-content', 'entry-content', 'detail-body'])
                text_parts = []
                if main_content_elements:
                    for element in main_content_elements:
                        text_parts.append(element.get_text(separator=' ', strip=True))
                    job_content_text = " ".join(text_parts)
                else:
                    # Fallback to entire body text if specific elements not found
                    if soup.body:
                        job_content_text = soup.body.get_text(separator=' ', strip=True)
                    else:
                        job_content_text = soup.get_text(separator=' ', strip=True) # Last resort, entire page

                # Limit text length to avoid processing huge pages and potential memory issues
                if len(job_content_text) > 10000: # Increased limit for more content
                    job_content_text = job_content_text[:10000] + "..." # Add ellipsis to indicate truncation
                    logger.debug(f"Truncated job content for {job['url']}")
            else:
                logger.warning(f"Could not fetch content for {job['url']}. Using title as fallback.")
                job_content_text = job['title'] # Fallback

    except Exception as e:
        logger.error(f"Error processing job content for {job['url']}: {e}. Using title as content.")
        job_content_text = job['title'] # Ensure there's always some text

    # Apply AI processing (rule-based for now)
    if job_content_text:
        job['description'] = summarize_job_description(job_content_text)
        job['important_dates'], job['links'] = extract_important_dates_and_links(job_content_text)
        job['category'] = auto_detect_job_category(job_content_text)
        job['skills'] = extract_trending_skills(job_content_text)

    return job

def save_jobs_to_files(jobs):
    """Save jobs to individual JSON files."""
    saved_count = 0

    if not jobs:
        logger.info("No new jobs to save to individual files.")
        return 0

    logger.info(f"\n💾 Saving {len(jobs)} new jobs to individual files in '{JOB_DIR}'...")

    # Ensure the main job data directory exists
    os.makedirs(JOB_DIR, exist_ok=True)

    for i, job in enumerate(jobs, 1):
        # Construct the file path using the job ID
        job_file_path = os.path.join(JOB_DIR, f"{job['id']}.json")

        try:
            with open(job_file_path, 'w', encoding='utf-8') as f:
                json.dump(job, f, indent=2, ensure_ascii=False) # `ensure_ascii=False` for proper Unicode characters

            logger.info(f"  [{i}/{len(jobs)}] ✅ Saved: {job['title'][:60]}... to {os.path.basename(job_file_path)}")
            saved_count += 1

        except Exception as e:
            logger.error(f"Error saving job file for ID {job.get('id', 'unknown')} at {job_file_path}: {e}")

    logger.info(f"\n📁 Successfully saved {saved_count}/{len(jobs)} job files to '{JOB_DIR}' directory.")
    return saved_count

def delete_expired_jobs():
    """Delete expired jobs based on 'last_date' or if older than 30 days (scraped_at)."""
    logger.info("\n🧹 Cleaning up expired jobs...")
    manifest = load_manifest() # Reload manifest to get the latest state
    active_jobs = []
    expired_count = 0
    current_date = datetime.now()

    jobs_in_manifest = manifest.get('jobs', [])
    if not jobs_in_manifest:
        logger.info("No jobs in manifest to clean.")
        manifest['expired_jobs'] = 0 # Ensure this is reset if no jobs are present
        save_manifest(manifest)
        return

    for job_entry in jobs_in_manifest:
        is_expired = False

        # Check for 'last_date' expiry
        if 'important_dates' in job_entry and 'last_date' in job_entry['important_dates']:
            date_str = job_entry['important_dates']['last_date']
            parsed_date = None
            # Try different date formats for robustness
            for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %b %Y', '%d %B %Y'):
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue

            if parsed_date:
                # Compare only dates, ignore time for expiry check
                if parsed_date.date() < current_date.date():
                    is_expired = True
                    logger.debug(f"Job {job_entry['id']} expired by last_date: {date_str}")
            else:
                logger.warning(f"Could not parse 'last_date' '{date_str}' for job {job_entry.get('id', 'unknown')}. Skipping date-based expiry for this job.")

        # Also consider jobs scraped more than 30 days ago as potentially expired if no 'last_date' or it wasn't parsed
        if not is_expired and 'scraped_at' in job_entry:
            try:
                scraped_date = datetime.fromisoformat(job_entry['scraped_at'])
                # Add a buffer for 'recently scraped' jobs, e.g., 2 days for initial processing
                if (current_date - scraped_date).days > 30: # Removed small buffer for simpler check
                    is_expired = True
                    logger.debug(f"Job {job_entry['id']} expired by age (scraped_at): {job_entry['scraped_at']}")
            except ValueError:
                logger.warning(f"Could not parse 'scraped_at' for job {job_entry.get('id', 'unknown')}. Skipping age-based expiry for this job.")

        if not is_expired:
            active_jobs.append(job_entry)
        else:
            expired_count += 1
            job_file_path = os.path.join(JOB_DIR, f"{job_entry.get('id', 'unknown')}.json")
            if os.path.exists(job_file_path):
                try:
                    os.remove(job_file_path)
                    logger.info(f"🗑️ Deleted expired job file: {os.path.basename(job_file_path)}")
                except OSError as e:
                    logger.error(f"Error deleting expired job file {job_file_path}: {e}")
            else:
                logger.debug(f"Expired job file not found (already deleted?): {os.path.basename(job_file_path)}")

    manifest['jobs'] = active_jobs
    manifest['active_jobs'] = len(active_jobs)
    manifest['expired_jobs'] = expired_count # Update expired count correctly
    manifest['total_jobs'] = len(active_jobs) # Total jobs now reflects only active ones
    save_manifest(manifest)

    logger.info(f"✅ Cleanup complete: Deleted {expired_count} expired jobs.")

# --- Main Execution ---

def main():
    """Main function to orchestrate job fetching process"""
    print("=" * 60)
    print("🚀 SarkariSarthi 2.0 Job Fetcher Started (for GitHub Actions)")
    print("=" * 60)

    # Create jobs directory if it doesn't exist
    # This is crucial in GitHub Actions as the runner starts in a clean environment.
    os.makedirs(JOB_DIR, exist_ok=True)
    logger.info(f"📁 Jobs data directory ready: {os.path.abspath(JOB_DIR)}")

    # Load existing manifest
    manifest = load_manifest()
    # Use a set for efficient lookup of existing job URLs
    existing_job_urls = {job['url'] for job in manifest.get('jobs', [])}
    logger.info(f"📋 Existing jobs in manifest: {len(existing_job_urls)}")

    # Scrape all job portals
    all_scraped_jobs = scrape_all_job_portals()

    if not all_scraped_jobs:
        logger.warning("⚠️ WARNING: No jobs were scraped from any portal!")
        logger.warning("This might be due to: Network issues, website blocking, or structural changes.")
        # Attempt to clean up even if no new jobs were found
        delete_expired_jobs()
        print("\n" + "=" * 60)
        print("📈 FINAL SUMMARY (No new jobs scraped)")
        print("=" * 60)
        final_manifest = load_manifest()
        print(f"📊 Total active jobs in system: {final_manifest.get('active_jobs', 0)}")
        print(f"🕒 Last updated: {final_manifest.get('last_updated', 'Unknown')}")
        print("=" * 60)
        return # Exit if no jobs were found to process

    logger.info(f"\n🔍 Processing {len(all_scraped_jobs)} raw scraped jobs...")

    # Filter new jobs and process them
    new_jobs_to_add = []
    duplicate_count = 0

    for job_candidate in all_scraped_jobs:
        # Check if job URL already exists in our manifest
        if job_candidate['url'] in existing_job_urls:
            duplicate_count += 1
            continue

        # Process job content (description, dates, category, skills)
        processed_job = process_job_content(job_candidate)
        new_jobs_to_add.append(processed_job)
        existing_job_urls.add(job_candidate['url']) # Add to set to prevent duplicates *within* this run

    logger.info(f"📊 Processing Summary:")
    logger.info(f"  New unique jobs to save: {len(new_jobs_to_add)}")
    logger.info(f"  Duplicates skipped: {duplicate_count}")

    if new_jobs_to_add:
        # Save new jobs to individual files
        saved_count = save_jobs_to_files(new_jobs_to_add)

        # Update manifest
        # We need to load manifest again because delete_expired_jobs might have modified it
        manifest = load_manifest()
        manifest['jobs'].extend(new_jobs_to_add)
        manifest['last_updated'] = datetime.now().isoformat()
        manifest['total_jobs'] = len(manifest['jobs']) # Total jobs includes new ones
        manifest['active_jobs'] = len(manifest['jobs']) # Initially, all new jobs are active
        save_manifest(manifest)

        logger.info(f"\n✅ Successfully added {saved_count} new jobs to the system!")
    else:
        logger.info("\n📋 No new unique jobs to add (all were duplicates or none found).")

    # Clean up expired jobs (important to run this after adding new jobs)
    delete_expired_jobs()

    # Final summary based on the updated manifest
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

# --- Test Functions (for development/debugging) ---

def test_single_site():
    """Test function for debugging a single site."""
    test_url = "https://www.freejobalert.com" # Or any other URL you want to test
    logger.info(f"🧪 Testing single site: {test_url}")

    # Ensure JOB_DIR exists for the test run
    os.makedirs(JOB_DIR, exist_ok=True)

    jobs = scrape_generic_job_site(test_url, "freejobalert_test")

    if jobs:
        logger.info(f"✅ Test successful! Found {len(jobs)} jobs (first 5 shown):")
        for i, job in enumerate(jobs[:5], 1):
            logger.info(f"  {i}. Title: {job['title'][:60]}... URL: {job['url']}")

        # Optionally, process and save these test jobs to see JSON output
        processed_test_jobs = [process_job_content(job) for job in jobs[:5]]
        save_jobs_to_files(processed_test_jobs)
        return True
    else:
        logger.warning("❌ Test failed - no jobs found from the test site.")
        return False

# --- Entry Point ---

if __name__ == "__main__":
    # Uncomment the line below to test a single site first for debugging
    # test_single_site()

    # Run the main function for full scraping and processing
    main()
