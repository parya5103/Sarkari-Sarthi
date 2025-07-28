#!/usr/bin/env python3
"""
SarkariSarthi 2.0 - Job Fetcher (Fixed Version)
AI-powered job scraper for Indian government and private sector jobs
"""

import logging
import os
import json
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import fitz  # PyMuPDF
import pdfplumber
import hashlib
import re
import urllib.request
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        'https://www.govtjobsportal.in',
        'https://www.freshersworld.com/government-jobs'
    ],
    # Private Job Portals
    'private': [
        'https://www.naukri.com',
        'https://www.indeed.co.in',
        'https://www.monster.com',
        'https://www.shine.com',
        'https://www.timesjobs.com',
        'https://www.glassdoor.co.in',
        'https://www.foundit.in',
        'https://www.freshersworld.com',
        'https://www.internshala.com'
    ]
}

def load_manifest():
    """Load job manifest from file or create default structure"""
    if not os.path.exists(MANIFEST_FILE):
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }
    try:
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading manifest: {e}")
        return {
            "last_updated": "",
            "total_jobs": 0,
            "active_jobs": 0,
            "expired_jobs": 0,
            "jobs": []
        }

def save_manifest(manifest):
    """Save job manifest to file"""
    try:
        os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"✅ Manifest saved: {MANIFEST_FILE}")
    except Exception as e:
        logger.error(f"Error saving manifest: {e}")

def fetch_page_content(url, timeout=15, retries=3):
    """Fetch page content with retry logic and proper headers"""
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
            response.raise_for_status()
            
            print(f"✅ Successfully fetched: {url} (Status: {response.status_code})")
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == retries - 1:
                logger.error(f"❌ Failed to fetch {url} after {retries} attempts")
                return None
    return None

def download_pdf(url, save_path):
    """Download PDF file from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"Downloaded PDF from {url} to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return False

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF and pdfplumber as fallback"""
    text = ""
    try:
        # Try PyMuPDF first
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"PyMuPDF failed for {pdf_path}: {e}")
    
    try:
        # Fallback to pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        logger.error(f"pdfplumber also failed for {pdf_path}: {e}")
    
    return text

def summarize_job_description(text):
    """Summarize job description"""
    if not text:
        return "No description available"
    
    # Simple truncation for now
    if len(text) > 500:
        return text[:497] + "..."
    return text

def extract_important_dates_and_links(text):
    """Extract important dates and links from job text"""
    dates = {}
    links = []
    
    if not text:
        return dates, links
    
    # Date patterns
    date_patterns = [
        r'(?:Last Date|Application Deadline|Closing Date|Apply Before)[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(?:Exam Date|Test Date)[\s:]*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if 'last' in pattern.lower() or 'deadline' in pattern.lower():
                dates['last_date'] = match
            elif 'exam' in pattern.lower() or 'test' in pattern.lower():
                dates['exam_date'] = match
            else:
                dates['found_date'] = match
    
    # Link patterns
    link_pattern = r'https?://[\w\.-]+(?:/[\w\.-]*)*/?(?:\?[\w&=%\.-]*)?'
    links = re.findall(link_pattern, text)
    
    return dates, links

def auto_detect_job_category(text):
    """Auto-detect job category based on text content"""
    if not text:
        return "General"
    
    text_lower = text.lower()
    
    # Category keywords mapping
    categories = {
        'Banking': ['bank', 'banking', 'sbi', 'pnb', 'icici', 'hdfc', 'axis', 'clerk', 'po', 'probationary officer'],
        'SSC': ['ssc', 'staff selection commission', 'cgl', 'chsl', 'mts', 'stenographer'],
        'Railway': ['railway', 'rrb', 'ntpc', 'group d', 'alp', 'technician', 'loco pilot'],
        'Police': ['police', 'constable', 'sub inspector', 'asi', 'head constable', 'security'],
        'Defence': ['defence', 'defense', 'army', 'navy', 'air force', 'bsf', 'crpf', 'cisf', 'itbp', 'agniveer'],
        'Teaching': ['teacher', 'teaching', 'education', 'professor', 'lecturer', 'principal', 'school', 'college'],
        'UPSC': ['upsc', 'ias', 'ips', 'ifs', 'civil services', 'union public service'],
        'Medical': ['doctor', 'nurse', 'medical', 'hospital', 'aiims', 'mbbs', 'pharmacist'],
        'Engineering': ['engineer', 'engineering', 'technical', 'je', 'junior engineer', 'assistant engineer'],
        'IT': ['software', 'developer', 'programmer', 'it', 'computer', 'data analyst', 'web developer'],
        'Administrative': ['clerk', 'assistant', 'officer', 'administrative', 'data entry']
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "General"

def extract_trending_skills(text):
    """Extract trending skills from job text"""
    if not text:
        return []
    
    text_lower = text.lower()
    skills = []
    
    # Skills database
    skill_keywords = {
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'excel', 'powerpoint',
        'communication skills', 'computer knowledge', 'ms office', 'typing',
        'general knowledge', 'reasoning', 'english', 'hindi', 'mathematics',
        'leadership', 'teamwork', 'problem solving', 'data entry'
    }
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title())
    
    return list(set(skills))

def scrape_generic_job_site(url, site_name):
    """Enhanced generic job site scraper"""
    print(f"\n🔍 Scraping {site_name}...")
    html_content = fetch_page_content(url)
    jobs = []
    
    if not html_content:
        print(f"❌ No content fetched from {site_name}")
        return jobs
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Multiple selector strategies
        job_selectors = [
            # More specific selectors first
            '.job-title a',
            '.vacancy-link',
            '.post-title a',
            'a[href*="jobs"]',
            'a[href*="notification"]',
            'a[href*="vacancy"]',
            'a[href*="recruitment"]',
            'a[href*="bharti"]',
            'h3 a',
            'h2 a',
            '.job-link',
            'a[title*="job" i]',
            'a[title*="recruitment" i]'
        ]
        
        print(f"🔎 Trying {len(job_selectors)} different selectors...")
        
        for i, selector in enumerate(job_selectors):
            try:
                links = soup.select(selector)
                print(f"  Selector {i+1} '{selector}': Found {len(links)} links")
                
                temp_jobs = []
                for link in links[:15]:  # Increased limit
                    try:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        # Better filtering
                        if not title or not href or len(title) < 5:
                            continue
                        
                        # Expanded job keywords
                        job_keywords = [
                            'job', 'recruitment', 'vacancy', 'notification', 'exam', 
                            'apply', 'bharti', 'posts', 'officer', 'clerk', 'assistant', 
                            'manager', 'engineer', 'teacher', 'constable', 'govt',
                            'government', 'sarkari', 'admission', 'form', 'eligibility'
                        ]
                        
                        # More lenient filtering
                        is_job = (
                            any(keyword in title.lower() for keyword in job_keywords) or
                            len(title) > 25 or  # Longer titles likely job postings
                            any(word in href.lower() for word in ['job', 'recruitment', 'vacancy'])
                        )
                        
                        if is_job:
                            full_url = urljoin(url, href)
                            
                            # Avoid duplicates and invalid URLs
                            if full_url.startswith('http') and full_url not in [j['url'] for j in temp_jobs]:
                                job_id = hashlib.md5(full_url.encode()).hexdigest()
                                
                                temp_jobs.append({
                                    'id': job_id,
                                    'title': title.strip(),
                                    'url': full_url,
                                    'source': site_name,
                                    'description': '',
                                    'pdf_link': None,
                                    'important_dates': {},
                                    'category': 'General',
                                    'skills': [],
                                    'scraped_at': datetime.now().isoformat()
                                })
                                
                    except Exception as e:
                        continue
                
                if temp_jobs:
                    jobs.extend(temp_jobs)
                    print(f"  ✅ Found {len(temp_jobs)} valid jobs with this selector")
                    break  # Stop trying other selectors if we found jobs
                    
            except Exception as e:
                print(f"  ⚠️ Selector {i+1} failed: {e}")
                continue
    
    except Exception as e:
        logger.error(f"❌ Error scraping {site_name}: {e}")
    
    print(f"📊 Total jobs found from {site_name}: {len(jobs)}")
    return jobs

def scrape_all_job_portals():
    """Scrape all configured job portals with better error handling"""
    all_jobs = []
    successful_sites = 0
    
    print(f"\n🚀 Starting comprehensive job scraping from {len(JOB_PORTALS['government']) + len(JOB_PORTALS['private'])} portals...")
    
    # Scrape government job portals
    print(f"\n📋 Scraping {len(JOB_PORTALS['government'])} government job portals...")
    for i, url in enumerate(JOB_PORTALS['government'], 1):
        try:
            site_name = url.split('//')[1].split('/')[0]
            print(f"\n[{i}/{len(JOB_PORTALS['government'])}] Government Site: {site_name}")
            
            jobs = scrape_generic_job_site(url, site_name)
            if jobs:
                all_jobs.extend(jobs)
                successful_sites += 1
                print(f"✅ Success! Added {len(jobs)} jobs from {site_name}")
            else:
                print(f"⚠️ No jobs found from {site_name}")
            
            # Delay between requests
            time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
    
    # Scrape private job portals (limit to avoid overload)
    print(f"\n💼 Scraping {min(3, len(JOB_PORTALS['private']))} private job portals...")
    for i, url in enumerate(JOB_PORTALS['private'][:3], 1):  # Limit to 3 for testing
        try:
            site_name = url.split('//')[1].split('/')[0]
            print(f"\n[{i}/3] Private Site: {site_name}")
            
            jobs = scrape_generic_job_site(url, site_name)
            if jobs:
                all_jobs.extend(jobs)
                successful_sites += 1
                print(f"✅ Success! Added {len(jobs)} jobs from {site_name}")
            else:
                print(f"⚠️ No jobs found from {site_name}")
            
            # Delay between requests
            time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
    
    print(f"\n📈 Scraping Summary:")
    print(f"  Successful sites: {successful_sites}")
    print(f"  Total jobs found: {len(all_jobs)}")
    
    return all_jobs

def process_job_content(job):
    """Process individual job content"""
    print(f"🔄 Processing: {job['title'][:50]}...")
    
    job_content_text = ""
    
    try:
        # Check if it's a PDF link
        if job['url'].lower().endswith('.pdf') or '.pdf' in job['url'].lower():
            pdf_filename = os.path.join(JOB_DIR, f"temp_{job['id']}.pdf")
            if download_pdf(job['url'], pdf_filename):
                job_content_text = extract_text_from_pdf(pdf_filename)
                job['pdf_link'] = job['url']
                if os.path.exists(pdf_filename):
                    os.remove(pdf_filename)  # Clean up
            else:
                job_content_text = job['title']
        else:
            # Fetch job page content (with timeout to avoid hanging)
            job_page_content = fetch_page_content(job['url'], timeout=10)
            if job_page_content:
                soup = BeautifulSoup(job_page_content, 'lxml')
                
                # Try to extract main content
                main_content = (soup.find('article') or 
                              soup.find('main') or 
                              soup.find('.job-description') or
                              soup.find('.content') or
                              soup.find('.post-content') or
                              soup.find('body'))
                
                if main_content:
                    job_content_text = main_content.get_text(separator=' ', strip=True)
                else:
                    job_content_text = soup.get_text(separator=' ', strip=True)
                    
                # Limit text length to avoid processing huge pages
                if len(job_content_text) > 5000:
                    job_content_text = job_content_text[:5000]
    
    except Exception as e:
        logger.warning(f"Error processing job content for {job['url']}: {e}")
        job_content_text = job['title']
    
    # Apply AI processing
    if job_content_text:
        job['description'] = summarize_job_description(job_content_text)
        job['important_dates'], job['links'] = extract_important_dates_and_links(job_content_text)
        job['category'] = auto_detect_job_category(job_content_text)
        job['skills'] = extract_trending_skills(job_content_text)
    
    return job

def save_jobs_to_files(jobs):
    """Save jobs to individual files with better error handling"""
    saved_count = 0
    
    print(f"\n💾 Saving {len(jobs)} jobs to files...")
    
    for i, job in enumerate(jobs, 1):
        try:
            job_file_path = os.path.join(JOB_DIR, f"{job['id']}.json")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(job_file_path), exist_ok=True)
            
            with open(job_file_path, 'w', encoding='utf-8') as f:
                json.dump(job, f, indent=2, ensure_ascii=False)
            
            print(f"  [{i}/{len(jobs)}] ✅ Saved: {job['title'][:40]}...")
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving job {job.get('id', 'unknown')}: {e}")
    
    print(f"\n📁 Successfully saved {saved_count}/{len(jobs)} job files to '{JOB_DIR}' directory")
    return saved_count

def delete_expired_jobs():
    """Delete expired jobs based on dates"""
    print("\n🧹 Cleaning up expired jobs...")
    manifest = load_manifest()
    active_jobs = []
    expired_count = 0
    current_date = datetime.now()
    
    for job_entry in manifest.get('jobs', []):
        is_expired = False
        
        # Check if job has expired based on last date
        if 'important_dates' in job_entry and 'last_date' in job_entry['important_dates']:
            try:
                date_str = job_entry['important_dates']['last_date']
                parsed_date = None
                
                # Try different date formats
                for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%d %B %Y', '%d %b %Y', '%Y-%m-%d'):
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date and parsed_date < current_date:
                    is_expired = True
            except Exception as e:
                logger.warning(f"Could not parse date for job {job_entry.get('id', 'unknown')}: {e}")
        
        # Also consider jobs older than 30 days as potentially expired
        if 'scraped_at' in job_entry:
            try:
                scraped_date = datetime.fromisoformat(job_entry['scraped_at'])
                if (current_date - scraped_date).days > 30:
                    is_expired = True
            except Exception:
                pass
        
        if not is_expired:
            active_jobs.append(job_entry)
        else:
            expired_count += 1
            job_file_path = os.path.join(JOB_DIR, f"{job_entry.get('id', 'unknown')}.json")
            if os.path.exists(job_file_path):
                os.remove(job_file_path)
                print(f"🗑️ Deleted expired job file: {job_file_path}")
    
    manifest['jobs'] = active_jobs
    manifest['active_jobs'] = len(active_jobs)
    manifest['expired_jobs'] = expired_count
    save_manifest(manifest)
    
    print(f"✅ Cleanup complete: Deleted {expired_count} expired jobs")

def main():
    """Main function to orchestrate job fetching process"""
    print("=" * 60)
    print("🚀 SarkariSarthi 2.0 Job Fetcher Started")
    print("=" * 60)
    
    # Create jobs directory
    os.makedirs(JOB_DIR, exist_ok=True)
    print(f"📁 Jobs directory ready: {os.path.abspath(JOB_DIR)}")
    
    # Load existing manifest
    manifest = load_manifest()
    existing_job_urls = {job['url'] for job in manifest.get('jobs', [])}
    print(f"📋 Existing jobs in manifest: {len(existing_job_urls)}")
    
    # Scrape all job portals
    all_new_jobs = scrape_all_job_portals()
    
    if not all_new_jobs:
        print("⚠️ WARNING: No jobs were scraped from any portal!")
        print("This could be due to:")
        print("  - Network connectivity issues")
        print("  - Websites blocking requests")
        print("  - Changes in website structure")
        return
    
    print(f"\n🔍 Processing {len(all_new_jobs)} scraped jobs...")
    
    # Filter new jobs and process them
    new_jobs = []
    duplicate_count = 0
    
    for job in all_new_jobs:
        if job['url'] in existing_job_urls:
            duplicate_count += 1
            continue
        
        # Process job content
        processed_job = process_job_content(job)
        new_jobs.append(processed_job)
        existing_job_urls.add(job['url'])  # Add to set to avoid duplicates in this run
    
    print(f"📊 Processing Summary:")
    print(f"  New jobs to save: {len(new_jobs)}")
    print(f"  Duplicates skipped: {duplicate_count}")
    
    if new_jobs:
        # Save jobs to individual files
        saved_count = save_jobs_to_files(new_jobs)
        
        # Update manifest
        manifest['jobs'].extend(new_jobs)
        manifest['last_updated'] = datetime.now().isoformat()
        manifest['total_jobs'] = len(manifest['jobs'])
        manifest['active_jobs'] = len(manifest['jobs'])
        save_manifest(manifest)
        
        print(f"\n✅ Successfully added {saved_count} new jobs to the system!")
    else:
        print("\n📋 No new jobs to add (all were duplicates)")
    
    # Clean up expired jobs
    delete_expired_jobs()
    
    # Final summary
    final_manifest = load_manifest()
    print("\n" + "=" * 60)
    print("📈 FINAL SUMMARY")
    print("=" * 60)
    print(f"✅ SarkariSarthi 2.0 Job Fetcher completed successfully!")
    print(f"📊 Total active jobs in system: {final_manifest.get('active_jobs', 0)}")
    print(f"📁 Jobs directory: {os.path.abspath(JOB_DIR)}")
    print(f"📋 Manifest file: {os.path.abspath(MANIFEST_FILE)}")
    print(f"🕒 Last updated: {final_manifest.get('last_updated', 'Unknown')}")
    print("=" * 60)

# Test function for debugging
def test_single_site():
    """Test function for debugging a single site"""
    test_url = "https://www.freejobalert.com"
    print(f"🧪 Testing single site: {test_url}")
    
    jobs = scrape_generic_job_site(test_url, "freejobalert_test")
    
    if jobs:
        print(f"✅ Test successful! Found {len(jobs)} jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"  {i}. {job['title'][:60]}...")
        return True
    else:
        print("❌ Test failed - no jobs found")
        return False

if __name__ == "__main__":
    # Uncomment the line below to test a single site first
    # test_single_site()
    
    # Run the main function
    main()
