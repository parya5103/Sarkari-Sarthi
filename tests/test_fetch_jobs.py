import pytest
from fetch_jobs import extract_important_dates_and_links, auto_detect_job_category, summarize_job_description, extract_trending_skills

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

def test_extract_trending_skills_empty_or_none():
    """Test with empty string or None."""
    assert extract_trending_skills("") == []
    assert extract_trending_skills(None) == []

def test_extract_trending_skills_no_match():
    """Test with text containing no keywords."""
    text = "This is a random text about gardening and cooking."
    assert extract_trending_skills(text) == []

def test_extract_trending_skills_single_match():
    """Test with a single keyword match."""
    text = "We are looking for a Python developer."
    assert extract_trending_skills(text) == ["Python"]

def test_extract_trending_skills_multiple_matches():
    """Test with multiple keyword matches."""
    text = "Required skills: Python, Java, and SQL."
    result = extract_trending_skills(text)
    assert sorted(result) == sorted(["Python", "Java", "Sql"])

def test_extract_trending_skills_case_insensitivity():
    """Test case insensitivity."""
    text = "python, JAVA, sQl"
    result = extract_trending_skills(text)
    assert sorted(result) == sorted(["Python", "Java", "Sql"])

def test_extract_trending_skills_multi_word_match():
    """Test multi-word keyword match."""
    text = "He has great communication skills."
    assert extract_trending_skills(text) == ["Communication Skills"]

def test_extract_trending_skills_uniqueness():
    """Test that duplicate keywords in text result in unique skills list."""
    text = "Python and more Python with some python."
    assert extract_trending_skills(text) == ["Python"]

def test_extract_trending_skills_mixed_content():
    """Test text with various skills including multi-word and overlapping."""
    text = """
    We need a candidate with Cloud experience, specifically AWS or Azure.
    Strong Communication Skills and leadership are must-haves.
    Knowledge of Artificial Intelligence and Machine Learning is a plus.
    """
    result = extract_trending_skills(text)
    expected = ["Cloud", "Aws", "Azure", "Communication Skills", "Leadership", "Artificial Intelligence", "Machine Learning"]
    assert sorted(result) == sorted(expected)
