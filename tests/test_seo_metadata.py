"""SEO metadata regression tests for the Sarkari Sarthi portal."""
from pathlib import Path
from detail_pages import render_detail_page


def test_homepage_targets_supported_job_searches_without_keyword_stuffing():
    html = Path("index.html").read_text(encoding="utf-8")
    title = html.split("<title>", 1)[1].split("</title>", 1)[0]
    description = html.split('<meta name="description" content="', 1)[1].split('"', 1)[0]
    assert len(title) <= 60
    assert 70 <= len(description) <= 160
    assert "government jobs" in title.lower()
    assert "sarkari naukri" in html.lower()
    assert 'name="keywords"' not in html.lower()
    assert "admit card" not in description.lower()
    assert "examination results" not in description.lower()
    for category in ("Medical", "Engineering", "Administrative"):
        assert f'value="{category}"' in html
        assert f'data-category="{category}"' in html
    assert "verification status" in html.lower()
    assert "collected from official sources" not in html.lower()


def test_generated_job_page_has_concise_metadata_and_full_visible_title():
    full_title = "A Very Long Government Recruitment Notification Title With Several Extra Words"
    job = {"id":"seo_test_001","title":full_title,"description":"Government recruitment notification with eligibility, dates, vacancies, and official source information. " * 3,"category":"General","status":"active","verification_status":"secondary_source_only","source":"Example recruitment source"}
    html = render_detail_page(job, [])
    title = html.split("<title>", 1)[1].split("</title>", 1)[0]
    description = html.split('<meta name="description" content="', 1)[1].split('"', 1)[0]
    assert len(title) <= 60
    assert 70 <= len(description) <= 140
    assert "<h1>" + full_title + "</h1>" in html
    assert "Sarkari Sarthi" in title
