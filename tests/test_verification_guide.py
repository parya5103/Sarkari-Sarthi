from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_verification_guide_contains_verified_official_recruitment_portals():
    html = (ROOT / "verification-guide.html").read_text(encoding="utf-8")
    expected_urls = [
        "https://www.ncs.gov.in/",
        "https://upsc.gov.in/",
        "https://ssc.gov.in/",
        "https://www.rrbcdg.gov.in/",
        "https://esb.mp.gov.in/",
        "https://mppsc.mp.gov.in/",
        "https://employmentnews.gov.in/",
        "https://www.ibps.in/",
        "https://nta.ac.in/",
        "https://opportunities.rbi.org.in/Scripts/Vacancies.aspx",
        "https://sbi.bank.in/en/web/careers/current-openings",
        "https://indiapostgdsonline.gov.in/",
        "https://joinindianarmy.nic.in/",
    ]
    for url in expected_urls:
        assert url in html, f"missing official source link: {url}"
    assert "Updated 26 November 2026" in html
    assert "Official Source" in html
    assert "Official Link Pending" in html
    assert "Secondary Source" in html
    assert "Needs Review" in html
    assert "not a government website" in html.lower()


def test_verification_guide_has_search_metadata_and_canonical():
    html = (ROOT / "verification-guide.html").read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    description = re.search(r'<meta name="description" content="([^"]+)"', html, re.I)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html, re.I)
    assert title and 10 <= len(title.group(1)) <= 60
    assert description and 70 <= len(description.group(1)) <= 160
    assert canonical and canonical.group(1) == "https://gogocompany.in/sarkari-sarthi/verification-guide.html"
    assert '<meta name="robots" content="index,follow">' in html


def test_sarkari_sarthi_internal_about_links_use_canonical_about_url():
    for filename in ("index.html", "verification-guide.html"):
        html = (ROOT / filename).read_text(encoding="utf-8")
        assert "https://gogocompany.in/about/" in html
        assert "https://gogocompany.in/about.html" not in html


def test_verification_guide_is_in_the_sitemap_with_current_lastmod():
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    assert "<loc>https://gogocompany.in/sarkari-sarthi/verification-guide.html</loc>" in sitemap
    assert "<lastmod>2026-11-26</lastmod>" in sitemap

def test_sarkari_homepage_heading_hierarchy_does_not_skip_levels():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    levels = [int(level) for level in re.findall(r"<h([1-6])\b[^>]*>", html, re.I)]
    assert levels, "homepage should contain semantic headings"
    for previous, current in zip(levels, levels[1:]):
        assert current <= previous + 1, f"heading hierarchy skips from H{previous} to H{current}"
