import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib
from datetime import datetime
import time
import random
import concurrent.futures

logger = logging.getLogger(__name__)

JOB_PORTALS = {
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
        "https://linkingsky.com/ "
    ]
}

def fetch_page_content(url, timeout=15, retries=3):
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
            time.sleep(random.uniform(2, 4))
            response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            response.raise_for_status()
            logger.info(f"✅ Successfully fetched: {url} (Status: {response.status_code})")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
            if attempt == retries - 1:
                logger.error(f"❌ Failed to fetch {url} after {retries} attempts")
                return None
    return None

# Pre-allocate static sets/tuples to prevent re-allocation per inner loop iteration
VALID_JOB_KEYWORDS = (
    'job', 'recruitment', 'vacancy', 'notification', 'exam',
    'apply', 'bharti', 'posts', 'officer', 'clerk', 'assistant',
    'manager', 'engineer', 'teacher', 'constable', 'govt',
    'government', 'sarkari', 'admission form', 'eligibility',
    'syllabus', 'result', 'admit card', 'walk-in', 'interview', 'selection', 'merit list'
)
VALID_URL_KEYWORDS = ('job', 'recruitment', 'vacancy', 'notification', 'apply')
EXCLUDE_URL_WORDS = ('login', 'register', 'contact', 'about', 'privacy', 'terms')

def _is_valid_job_link(title, full_url):
    """Validate if a given link is a job link based on its title and URL."""
    u_lower = full_url.lower()

    if any(exclude_word in u_lower for exclude_word in EXCLUDE_URL_WORDS):
        return False

    if len(title) > 30:
        return True

    t_lower = title.lower()
    return (
        any(keyword in t_lower for keyword in VALID_JOB_KEYWORDS) or
        any(word in u_lower for word in VALID_URL_KEYWORDS)
    )

def _extract_jobs_from_selector(links, url, site_name, found_links_overall):
    """Extract job links from a list of BeautifulSoup elements."""
    extracted_jobs = []
    for link in links[:20]:
        try:
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if not title or not href or len(title) < 5:
                continue

            full_url = urljoin(url, href).split('#')[0]
            if not full_url.startswith('http') or full_url in found_links_overall:
                continue

            if _is_valid_job_link(title, full_url):
                job_id = hashlib.md5(full_url.encode()).hexdigest()
                extracted_jobs.append({
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
                found_links_overall.add(full_url)
        except Exception as e_link:
            continue
    return extracted_jobs

def scrape_generic_job_site(url, site_name):
    logger.info(f"\n🔍 Scraping {site_name}...")
    html_content = fetch_page_content(url)
    jobs = []

    if not html_content:
        logger.warning(f"❌ No content fetched from {site_name}. Skipping.")
        return jobs

    try:
        soup = BeautifulSoup(html_content, 'lxml')
        job_selectors = [
            '.job-title a', '.vacancy-link', '.post-title a', '.job-link',
            'a[href*="jobs"]', 'a[href*="notification"]', 'a[href*="vacancy"]',
            'a[href*="recruitment"]', 'a[href*="bharti"]', 'a[href*="apply-online"]',
            'h3 a', 'h2 a', 'h1 a',
            'a[title*="job" i]', 'a[title*="recruitment" i]', 'a[class*="job" i]', 'a[id*="job" i]'
        ]

        logger.info(f"🔎 Trying {len(job_selectors)} different selectors for {site_name}...")
        found_links_overall = set()

        for i, selector in enumerate(job_selectors):
            try:
                links = soup.select(selector)
                current_selector_links = _extract_jobs_from_selector(links, url, site_name, found_links_overall)

                if current_selector_links:
                    jobs.extend(current_selector_links)
                    logger.info(f"  ✅ Found {len(current_selector_links)} potentially valid jobs with selector '{selector}'.")
            except Exception as e_selector:
                continue
    except Exception as e_soup:
        logger.error(f"❌ Error parsing HTML content for {site_name}: {e_soup}")

    return jobs

def _scrape_single_portal(url, index, total, category_name):
    try:
        site_name = url.split('//')[1].split('/')[0]
        logger.info(f"\n[{index}/{total}] {category_name} Site: {site_name}")
        jobs = scrape_generic_job_site(url, site_name)
        return jobs
    except Exception as e:
        logger.error(f"❌ Unhandled error during scraping of {url}: {e}")
        return []

def scrape_all_job_portals():
    all_jobs = []
    successful_sites = 0

    portals_to_scrape = []
    gov_portals = JOB_PORTALS['government']
    for i, url in enumerate(gov_portals, 1):
        portals_to_scrape.append((url, i, len(gov_portals), "Government"))

    priv_portals = JOB_PORTALS['private'][:3]
    for i, url in enumerate(priv_portals, 1):
        portals_to_scrape.append((url, i, len(priv_portals), "Private"))

    if not portals_to_scrape:
        return []

    max_workers = min(10, len(portals_to_scrape))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_scrape_single_portal, url, index, total, category): url for url, index, total, category in portals_to_scrape}
        for future in concurrent.futures.as_completed(futures):
            try:
                jobs = future.result()
                if jobs:
                    all_jobs.extend(jobs)
                    successful_sites += 1
            except Exception as exc:
                pass
    return all_jobs
