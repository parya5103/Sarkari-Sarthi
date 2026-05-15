import pytest
from fetch_jobs import extract_important_dates_and_links, auto_detect_job_category, summarize_job_description

def test_extract_important_dates_and_links():
    text1 = "The application deadline is 15-08-2024. Exam date will be 01-10-2024. Visit https://example.com/apply"
    dates1, links1 = extract_important_dates_and_links(text1)

    assert dates1.get('last_date') == '15-08-2024'
    assert dates1.get('exam_date') == '01-10-2024'
    assert 'https://example.com/apply' in links1

    text2 = "Last date to apply 12/12/2023. Exam on 15/01/2024"
    dates2, links2 = extract_important_dates_and_links(text2)

    assert dates2.get('last_date') == '12/12/2023'
    assert dates2.get('exam_date') == '15/01/2024'

def test_auto_detect_job_category():
    assert auto_detect_job_category("SBI PO Recruitment 2024") == "Banking"
    assert auto_detect_job_category("SSC CGL 2024 Notification") == "SSC"
    assert auto_detect_job_category("Indian Railways Group D") == "Railway"
    assert auto_detect_job_category("Delhi Police Constable") == "Police"
    assert auto_detect_job_category("Indian Army Agniveer") == "Defence"
    assert auto_detect_job_category("Primary School Teacher Vacancy") == "Teaching"
    assert auto_detect_job_category("UPSC Civil Services Exam") == "UPSC"
    assert auto_detect_job_category("Random unknown job") == "General"

def test_summarize_job_description():
    short_text = "This is a short description."
    assert summarize_job_description(short_text) == short_text

    long_text = "A" * 600
    summary = summarize_job_description(long_text)
    assert len(summary) == 500
    assert summary.endswith("...")
