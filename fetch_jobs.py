#!/usr/bin/env python3
"""
SarkariSarthi 2.0 - Job Fetcher
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
        'https://www.ncs.gov.in',
        'https://services.india.gov.in/service/listing?ln=en&cat_id=2',
        'https://www.mysarkarinaukri.com',
        'https://bharatsarkarijob.com',
        'https://allgovernmentjobs.in',
        'https://www.sarkariexam.com',
        'https://www.rojgarresult.com',
        'https://www.jobriya.com',
        'https://www.sarkari-naukri.info',
        'https://www.govtjobsportal.in',
        'https://www.freshersworld.com/government-jobs',
        'https://www.jagranjosh.com/government-jobs',
        'https://www.bankersadda.com',
        'https://www.oliveboard.in',
        'https://www.adda247.com',
        'https://www.gradeup.co',
        'https://www.testbook.com'
    ],
    # Private Job Portals
    'private': [
        'https://www.naukri.com',
        'https://www.indeed.co.in',
        'https://www.linkedin.com/jobs',
        'https://www.monster.com',
        'https://www.shine.com',
        'https://www.timesjobs.com',
        'https://www.glassdoor.co.in',
        'https://www.foundit.in',
        'https://www.freshersworld.com',
        'https://www.internshala.com',
        'https://www.cutshort.io',
        'https://www.instahyre.com',
        'https://www.hirist.com',
        'https://www.angellist.com',
        'https://www.workindia.in',
        'https://www.apnacircle.com',
        'https://www.babajob.com',
        'https://www.quikr.com/jobs',
        'https://www.clickjobs.com',
        'https://www.placementindia.com'
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
        with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving manifest: {e}")

def fetch_page_content(url, timeout=10, retries=3):
    """Fetch page content with retry logic and proper headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(retries):
        try:
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == retries - 1:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
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
    """Summarize job description using AI (placeholder implementation)"""
    if not text:
        return "No description available"
    
    # Simple truncation for now - can be replaced with actual AI summarization
    if len(text) > 300:
        return text[:297] + "..."
    return text

def extract_important_dates_and_links(text):
    """Extract important dates and links from job text"""
    dates = {}
    links = []
    
    if not text:
        return dates, links
    
    # Date patterns
    date_patterns = [
        r'(?:Last Date|Application Deadline|Closing Date|Apply Before):\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(?:Exam Date|Test Date):\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
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
        'Finance': ['finance', 'accountant', 'ca', 'chartered accountant', 'audit', 'tax'],
        'Legal': ['lawyer', 'legal', 'advocate', 'judge', 'court', 'law'],
        'Sales': ['sales', 'marketing', 'business development', 'relationship manager'],
        'HR': ['hr', 'human resource', 'recruitment', 'talent acquisition'],
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
    
    # Comprehensive skills database
    skill_keywords = {
        # Technical Skills
        'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
        'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'machine learning', 'ai', 'data science', 'deep learning',
        'html', 'css', 'bootstrap', 'tailwind',
        'git', 'github', 'gitlab', 'svn',
        
        # Business Skills
        'project management', 'agile', 'scrum', 'kanban',
        'excel', 'powerpoint', 'word', 'outlook',
        'sap', 'erp', 'crm', 'salesforce',
        'digital marketing', 'seo', 'sem', 'social media',
        'data analysis', 'business intelligence', 'tableau', 'power bi',
        
        # Government Job Skills
        'typing', 'computer knowledge', 'ms office',
        'general knowledge', 'current affairs', 'reasoning',
        'quantitative aptitude', 'english', 'hindi',
        'communication skills', 'leadership', 'teamwork',
        'problem solving', 'analytical thinking',
        
        # Soft Skills
        'communication', 'leadership', 'teamwork', 'problem solving',
        'time management', 'adaptability', 'creativity', 'critical thinking'
    }
    
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title())
    
    return list(set(skills))  # Remove duplicates

def scrape_generic_job_site(url, site_name):
    """Generic job site scraper with common patterns"""
    logger.info(f"Scraping {site_name}...")
    html_content = fetch_page_content(url)
    jobs = []
    
    if not html_content:
        return jobs
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Common job listing selectors
        job_selectors = [
            'a[href*="job"]',
            'a[href*="recruitment"]',
            'a[href*="vacancy"]',
            'a[href*="notification"]',
            '.job-title a',
            '.job-link',
            '.vacancy-link',
            'h3 a',
            'h4 a',
            '.post-title a'
        ]
        
        for selector in job_selectors:
            links = soup.select(selector)
            for link in links[:10]:  # Limit to 10 jobs per site to avoid overload
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if not title or not href:
                        continue
                    
                    # Filter relevant job titles
                    if any(keyword in title.lower() for keyword in ['job', 'recruitment', 'vacancy', 'notification', 'exam', 'apply']):
                        full_url = urljoin(url, href)
                        job_id = hashlib.md5(full_url.encode()).hexdigest()
                        
                        jobs.append({
                            'id': job_id,
                            'title': title,
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
                    logger.warning(f"Error processing link in {site_name}: {e}")
                    continue
            
            if jobs:  # If we found jobs with this selector, break
                break
    
    except Exception as e:
        logger.error(f"Error scraping {site_name}: {e}")
    
    logger.info(f"Found {len(jobs)} jobs from {site_name}")
    return jobs

def scrape_all_job_portals():
    """Scrape all configured job portals"""
    all_jobs = []
    
    # Scrape government job portals
    logger.info("Scraping government job portals...")
    for url in JOB_PORTALS['government']:
        try:
            site_name = url.split('//')[1].split('/')[0]
            jobs = scrape_generic_job_site(url, site_name)
            all_jobs.extend(jobs)
            
            # Add delay between requests
            time.sleep(random.uniform(2, 5))
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
    
    # Scrape private job portals
    logger.info("Scraping private job portals...")
    for url in JOB_PORTALS['private']:
        try:
            site_name = url.split('//')[1].split('/')[0]
            jobs = scrape_generic_job_site(url, site_name)
            all_jobs.extend(jobs)
            
            # Add delay between requests
            time.sleep(random.uniform(2, 5))
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
    
    return all_jobs

def process_job_content(job):
    """Process individual job content with AI analysis"""
    job_content_text = ""
    
    try:
        # Check if it's a PDF link
        if job['url'].lower().endswith('.pdf') or '.pdf' in job['url'].lower():
            pdf_filename = os.path.join(JOB_DIR, f"temp_{job['id']}.pdf")
            if download_pdf(job['url'], pdf_filename):
                job_content_text = extract_text_from_pdf(pdf_filename)
                job['pdf_link'] = job['url']
                os.remove(pdf_filename)  # Clean up
            else:
                job_content_text = job['title']
        else:
            # Fetch job page content
            job_page_content = fetch_page_content(job['url'])
            if job_page_content:
                soup = BeautifulSoup(job_page_content, 'lxml')
                
                # Try to extract main content
                main_content = (soup.find('article') or 
                              soup.find('main') or 
                              soup.find('.job-description') or
                              soup.find('.content') or
                              soup.find('body'))
                
                if main_content:
                    job_content_text = main_content.get_text(separator=' ', strip=True)
                else:
                    job_content_text = soup.get_text(separator=' ', strip=True)
    
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

def delete_expired_jobs():
    """Delete expired jobs based on dates"""
    logger.info("Deleting expired jobs...")
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
                logger.info(f"Deleted expired job file: {job_file_path}")
    
    manifest['jobs'] = active_jobs
    manifest['active_jobs'] = len(active_jobs)
    manifest['expired_jobs'] = expired_count
    save_manifest(manifest)
    logger.info(f"Deleted {expired_count} expired jobs.")

def main():
    """Main function to orchestrate job fetching process"""
    logger.info("SarkariSarthi 2.0 Job Fetcher started.")
    
    # Create jobs directory
    os.makedirs(JOB_DIR, exist_ok=True)
    
    # Load existing manifest
    manifest = load_manifest()
    existing_job_urls = {job['url'] for job in manifest.get('jobs', [])}
    
    # Scrape all job portals
    logger.info("Starting comprehensive job scraping...")
    all_new_jobs = scrape_all_job_portals()
    
    # Process and filter new jobs
    new_jobs_added = 0
    for job in all_new_jobs:
        if job['url'] in existing_job_urls:
            logger.debug(f"Skipping existing job: {job['title']}")
            continue
        
        logger.info(f"Processing new job: {job['title']} from {job['source']}")
        
        # Process job content with AI
        processed_job = process_job_content(job)
        
        # Save individual job file
        job_file_path = os.path.join(JOB_DIR, f"{processed_job['id']}.json")
        try:
            with open(job_file_path, 'w', encoding='utf-8') as f:
                json.dump(processed_job, f, indent=2, ensure_ascii=False)
            
            manifest['jobs'].append(processed_job)
            new_jobs_added += 1
            
        except Exception as e:
            logger.error(f"Error saving job {processed_job['id']}: {e}")
    
    # Update manifest
    manifest['last_updated'] = datetime.now().isoformat()
    manifest['total_jobs'] = len(manifest['jobs'])
    manifest['active_jobs'] = len(manifest['jobs'])
    save_manifest(manifest)
    
    # Clean up expired jobs
    delete_expired_jobs()
    
    logger.info(f"SarkariSarthi 2.0 Job Fetcher completed. Added {new_jobs_added} new jobs.")
    logger.info(f"Total active jobs: {len(manifest['jobs'])}")

if __name__ == "__main__":
    main()

