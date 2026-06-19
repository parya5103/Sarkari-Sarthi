import logging
import os
import requests
import fitz # PyMuPDF
import pdfplumber
import re
from bs4 import BeautifulSoup
from scraper import fetch_page_content

logger = logging.getLogger(__name__)

JOB_DIR = 'jobs'

# Pre-compiled regex patterns for better performance
# Optimization: Associate patterns with predefined tags to eliminate redundant string checking in loops
COMPILED_DATE_PATTERNS = [
    (re.compile(r'(?:Last Date|Application Deadline|Closing Date|Apply Before)\s*[:-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', re.IGNORECASE), 'last_date'),
    (re.compile(r'(?:Exam Date|Test Date)\s*[:-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', re.IGNORECASE), 'exam_date'),
    (re.compile(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', re.IGNORECASE), 'found_date')
]
COMPILED_LINK_PATTERN = re.compile(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

def download_pdf(url, save_path, max_size_bytes=10 * 1024 * 1024):
    """Download PDF file from URL with size limit."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        content_length = response.headers.get('Content-Length')
        if content_length:
            if int(content_length) > max_size_bytes:
                logger.warning(f"PDF too large ({content_length} bytes) from {url}. Skipping.")
                return False

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        downloaded_size = 0
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded_size += len(chunk)
                    if downloaded_size > max_size_bytes:
                        logger.warning(f"PDF exceeded size limit ({max_size_bytes} bytes) during download from {url}. Aborting.")
                        f.close()
                        os.remove(save_path)
                        return False
                    f.write(chunk)

        logger.info(f"Downloaded PDF from {url} to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return False

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"fitz failed to extract text from {pdf_path}: {e}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"pdfplumber failed to extract text from {pdf_path}: {e}")
    return text

def summarize_job_description(text):
    if not text:
        return "No description available"
    if len(text) > 500:
        return text[:497] + "..."
    return text

def extract_important_dates_and_links(text):
    dates = {}
    links = []
    if not text:
        return dates, links

    for pattern, date_type in COMPILED_DATE_PATTERNS:
        matches = pattern.findall(text)
        for match in matches:
            if date_type == 'found_date':
                if 'found_date' not in dates:
                    dates['found_date'] = match
            else:
                dates[date_type] = match

    links = COMPILED_LINK_PATTERN.findall(text)
    links = list(set(links))
    return dates, links

# Pre-allocate large keyword sets to avoid constant re-allocation per-function call
COMPILED_CATEGORIES = {
    'Banking': ('bank', 'banking', 'sbi', 'pnb', 'icici', 'hdfc', 'axis', 'clerk', 'po', 'probationary officer', 'rbi'),
    'SSC': ('ssc', 'staff selection commission', 'cgl', 'chsl', 'mts', 'stenographer'),
    'Railway': ('railway', 'rrb', 'ntpc', 'group d', 'alp', 'technician', 'loco pilot'),
    'Police': ('police', 'constable', 'sub inspector', 'asi', 'head constable', 'security'),
    'Defence': ('defence', 'defense', 'army', 'navy', 'air force', 'bsf', 'crpf', 'cisf', 'itbp', 'agniveer'),
    'Teaching': ('teacher', 'teaching', 'education', 'professor', 'lecturer', 'principal', 'school', 'college', 'ctet', 'ugc'),
    'UPSC': ('upsc', 'ias', 'ips', 'ifs', 'civil services', 'union public service'),
    'Medical': ('doctor', 'nurse', 'medical', 'hospital', 'aiims', 'mbbs', 'pharmacist', 'health'),
    'Engineering': ('engineer', 'engineering', 'technical', 'je', 'junior engineer', 'assistant engineer', 'psu'),
    'IT': ('software', 'developer', 'programmer', 'it', 'computer', 'data analyst', 'web developer', 'cybersecurity', 'ai', 'ml'),
    'Administrative': ('clerk', 'assistant', 'officer', 'administrative', 'data entry', 'section officer', 'patwari', 'lekpal')
}

SKILL_KEYWORDS = (
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'excel', 'powerpoint', 'word',
    'communication skills', 'computer knowledge', 'ms office', 'typing',
    'general knowledge', 'reasoning', 'english', 'hindi', 'mathematics', 'aptitude',
    'leadership', 'teamwork', 'problem solving', 'data entry', 'analyst', 'cloud', 'aws', 'azure', 'gcp',
    'machine learning', 'artificial intelligence', 'data science', 'big data', 'devops', 'automation',
    'networking', 'cyber security', 'project management', 'agile', 'scrum'
)

def auto_detect_job_category(text):
    if not text:
        return "General"
    text_lower = text.lower()
    for category, keywords in COMPILED_CATEGORIES.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "General"

def extract_trending_skills(text):
    if not text:
        return []
    text_lower = text.lower()
    return [skill.title() for skill in SKILL_KEYWORDS if skill in text_lower]

def process_job_content(job):
    job_content_text = ""
    try:
        if job['url'].lower().endswith('.pdf') or '.pdf' in job['url'].lower():
            safe_id = os.path.basename(str(job['id']))
            pdf_filename = os.path.join(JOB_DIR, f"temp_{safe_id}.pdf")
            if download_pdf(job['url'], pdf_filename):
                job_content_text = extract_text_from_pdf(pdf_filename)
                job['pdf_link'] = job['url']
            else:
                job_content_text = job['title']
            if os.path.exists(pdf_filename):
                try:
                    os.remove(pdf_filename)
                except OSError:
                    pass
        else:
            job_page_content = fetch_page_content(job['url'], timeout=15)
            if job_page_content:
                soup = BeautifulSoup(job_page_content, 'lxml')
                main_content_elements = soup.find_all(['article', 'main', 'div', 'section'],
                                                     class_=['job-description', 'content', 'post-content', 'entry-content', 'detail-body'])
                text_parts = []
                if main_content_elements:
                    for element in main_content_elements:
                        text_parts.append(element.get_text(separator=' ', strip=True))
                    job_content_text = " ".join(text_parts)
                else:
                    if soup.body:
                        job_content_text = soup.body.get_text(separator=' ', strip=True)
                    else:
                        job_content_text = soup.get_text(separator=' ', strip=True)
                if len(job_content_text) > 10000:
                    job_content_text = job_content_text[:10000] + "..."
            else:
                job_content_text = job['title']
    except Exception as e:
        job_content_text = job['title']

    if job_content_text:
        job['description'] = summarize_job_description(job_content_text)
        job['important_dates'], job['links'] = extract_important_dates_and_links(job_content_text)
        job['category'] = auto_detect_job_category(job_content_text)
        job['skills'] = extract_trending_skills(job_content_text)

    return job
