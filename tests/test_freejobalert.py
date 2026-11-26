from datetime import date
from pathlib import Path

import pytest

from freejobalert import (
    FREEJOBALERT_SOURCE_NAME,
    LISTING_URL,
    fetch_freejobalert_jobs,
    parse_freejobalert_html,
)
from source_metrics import SourceMetrics


FIXTURE = Path(__file__).parent / "fixtures" / "freejobalert_latest_notifications.html"
HTML = FIXTURE.read_bytes()
TODAY = date(2026, 11, 26)


def test_parser_extracts_table_fields_and_only_future_same_site_jobs():
    jobs = parse_freejobalert_html(HTML, now=TODAY)
    assert len(jobs) == 3
    first = jobs[0]
    assert first["title"] == "Administrative Member – 4 Posts"
    assert first["department"] == "DoPT"
    assert first["recruitment_board"] == "DoPT"
    assert first["qualification"] == "Graduate"
    assert first["advertisement_no"] == "A-11013/1/2025-41"
    assert first["vacancies"] == 4
    assert first["important_dates"]["last_date"] == "2026-12-20"
    assert first["published_date"] == "2026-11-05"
    assert first["source"] == FREEJOBALERT_SOURCE_NAME
    assert first["url"].startswith("https://www.freejobalert.com/")
    assert first["official_notification_url"] is None
    assert first["official_application_url"] is None


def test_parser_skips_expired_missing_deadline_and_offsite_detail_links():
    jobs = parse_freejobalert_html(HTML, now=TODAY)
    urls = {job["url"] for job in jobs}
    assert not any("expired-recruitment" in url for url in urls)
    assert not any("no-date-recruitment" in url for url in urls)
    assert not any("evil.example" in url for url in urls)


def test_fetch_records_success_and_robots_permission(monkeypatch):
    import freejobalert

    metrics = SourceMetrics()
    monkeypatch.setattr(freejobalert, "robots_access", lambda *args, **kwargs: (True, "allowed"))
    jobs = fetch_freejobalert_jobs(
        fetch=lambda url, timeout=30: HTML,
        now=TODAY,
        metrics=metrics,
    )
    assert len(jobs) == 3
    entry = metrics.sources[FREEJOBALERT_SOURCE_NAME]
    assert entry["status"] == "ok"
    assert entry["permission"] == "allowed"
    assert entry["discovered"] == 3


def test_fetch_stops_when_robots_disallows(monkeypatch):
    import freejobalert

    metrics = SourceMetrics()
    calls = []
    monkeypatch.setattr(freejobalert, "robots_access", lambda *args, **kwargs: (False, "disallowed"))

    def should_not_fetch(*args, **kwargs):
        calls.append(args[0])
        raise AssertionError("listing must not be fetched after robots disallow")

    assert fetch_freejobalert_jobs(fetch=should_not_fetch, now=TODAY, metrics=metrics) == []
    assert calls == []
    entry = metrics.sources[FREEJOBALERT_SOURCE_NAME]
    assert entry["status"] == "robots-disallowed"
    assert entry["permission"] == "disallowed"


def test_fetch_records_parse_error_when_table_layout_changes(monkeypatch):
    import freejobalert

    metrics = SourceMetrics()
    monkeypatch.setattr(freejobalert, "robots_access", lambda *args, **kwargs: (True, "allowed"))
    assert fetch_freejobalert_jobs(
        fetch=lambda url, timeout=30: b"<html><body>layout changed</body></html>",
        now=TODAY,
        metrics=metrics,
    ) == []
    entry = metrics.sources[FREEJOBALERT_SOURCE_NAME]
    assert entry["status"] == "parse-error"
    assert entry["parser_errors"] == 1


def test_fetch_records_network_failure_separately(monkeypatch):
    import freejobalert

    metrics = SourceMetrics()
    monkeypatch.setattr(freejobalert, "robots_access", lambda *args, **kwargs: (True, "unverified"))

    def timeout(*args, **kwargs):
        raise TimeoutError("listing timeout")

    assert fetch_freejobalert_jobs(fetch=timeout, now=TODAY, metrics=metrics) == []
    entry = metrics.sources[FREEJOBALERT_SOURCE_NAME]
    assert entry["status"] == "fetch-failed"
    assert entry["permission"] == "unverified"
    assert "timeout" in entry["notes"].lower()
