from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from tr_climate.bing_news_fetch import fetch_bing_news_site
from tr_climate.history import ROLLING_WINDOW_DAYS, TIMESERIES_SCHEMA_VERSION, row_from_items_for_date
from tr_climate.matcher import load_keywords, match_climate, match_topics
from tr_climate.models import NewsItem, RawItem, finalize_item
from tr_climate.rss_fetch import fetch_rss_feed

# Bing News site: queries (publisher host)
SITE_DOMAIN_BY_SOURCE: dict[str, str] = {
    "trt_haber": "www.trthaber.com",
    "ntv": "www.ntv.com.tr",
    "haberturk": "www.haberturk.com",
    "anadolu_agency": "www.aa.com.tr",
    "yenisafak": "www.yenisafak.com",
    "milliyet": "www.milliyet.com.tr",
    "ahaber": "www.ahaber.com.tr",
    "cnnturk": "www.cnnturk.com",
}


def _norm_host(host: str) -> str:
    h = (host or "").lower()
    if h.startswith("www."):
        return h[4:]
    return h


def _url_matches_source_domain(pub_url: str, domain: str) -> bool:
    h = _norm_host(urlparse(pub_url).netloc or "")
    d = _norm_host(domain)
    return h == d or h.endswith("." + d)


def _load_sources(path: Path) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(raw.get("sources") or [])


def _load_extra_feeds(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: dict[str, list[str]] = {}
    for sid, urls in (raw.get("extra_rss_by_source") or {}).items():
        if isinstance(urls, list):
            out[str(sid)] = [str(u) for u in urls if u]
    return out


def _fetch_source_native(
    cfg: dict[str, Any],
    extra_urls: list[str],
) -> tuple[list[RawItem], list[str]]:
    """Pull native RSS/HTML plus extra RSS URLs; use full feed length (no cap) for RSS."""
    stype = cfg["type"]
    sid = cfg["id"]
    errors: list[str] = []
    merged: list[RawItem] = []
    seen: set[str] = set()

    def add_batch(items: list[RawItem]) -> None:
        for it in items:
            if it.url not in seen:
                seen.add(it.url)
                merged.append(it)

    try:
        if stype == "html_trt":
            pass  # listing scrape has no stable dates; TRT is covered via Bing site:trthaber.com
        elif stype == "rss":
            add_batch(fetch_rss_feed(str(cfg["feed_url"]), sid, max_items=None))
        else:
            errors.append(f"{sid}: unknown type {stype}")
    except Exception as e:  # noqa: BLE001
        errors.append(f"{sid}: {e}")

    for u in extra_urls:
        try:
            add_batch(fetch_rss_feed(u, sid, max_items=None))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{sid} extra {u}: {e}")

    return merged, errors


def _published_utc_date_key(published_at: str | None) -> str | None:
    if not published_at:
        return None
    s = published_at.strip()
    try:
        if s.endswith("Z"):
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(s)
        except (TypeError, ValueError):
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).date().isoformat()


def _utc_day_range(ending: date, n_days: int) -> list[str]:
    start = ending - timedelta(days=n_days - 1)
    out: list[str] = []
    d = start
    while d <= ending:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def run_web_backfill(
    timeseries_path: Path,
    *,
    days: int = ROLLING_WINDOW_DAYS,
    sources_path: Path | None = None,
    extra_feeds_path: Path | None = None,
    keywords_path: Path | None = None,
    bing_pages: int = 22,
    bing_pause: float = 0.35,
) -> dict[str, Any]:
    """
    Build timeseries.json for the last `days` UTC calendar days using native feeds,
    extra RSS URLs, and paginated Bing News RSS per outlet (publisher URLs only).
    Does not write items.json.
    """
    base = Path(__file__).resolve().parent.parent
    sp = sources_path or (base / "config" / "sources.yaml")
    xp = extra_feeds_path or (base / "config" / "web_backfill_feeds.yaml")
    kw_cfg = load_keywords(keywords_path)
    sources = _load_sources(sp)
    extra_by_source = _load_extra_feeds(xp)

    all_raw: list[RawItem] = []
    errors: list[str] = []

    for src in sources:
        sid = src["id"]
        extra = extra_by_source.get(sid, [])
        batch, errs = _fetch_source_native(src, extra)
        all_raw.extend(batch)
        errors.extend(errs)

    for sid, domain in SITE_DOMAIN_BY_SOURCE.items():
        try:
            for it in fetch_bing_news_site(
                domain,
                sid,
                max_pages=bing_pages,
                pause_sec=bing_pause,
            ):
                if _url_matches_source_domain(it.url, domain):
                    all_raw.append(it)
        except Exception as e:  # noqa: BLE001
            errors.append(f"bing {sid}: {e}")

    by_url: dict[str, RawItem] = {}
    for raw in all_raw:
        if raw.url not in by_url:
            by_url[raw.url] = raw

    now = datetime.now(timezone.utc)
    today = now.date()
    window_end = today
    window_start = today - timedelta(days=days - 1)
    day_keys = _utc_day_range(window_end, days)

    collected_iso = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    finalized_by_day: dict[str, list[NewsItem]] = {d: [] for d in day_keys}

    for raw in by_url.values():
        dk = _published_utc_date_key(raw.published_at)
        if dk is None or dk not in finalized_by_day:
            continue
        rel, kws = match_climate(kw_cfg, raw.title, raw.description)
        topics = match_topics(kw_cfg, raw.title, raw.description)
        finalized_by_day[dk].append(
            finalize_item(raw, rel, kws, topics, collected_at=now),
        )

    series = [row_from_items_for_date(finalized_by_day[d], d) for d in day_keys]

    data: dict[str, Any] = {
        "data_schema_version": TIMESERIES_SCHEMA_VERSION,
        "series": series,
        "updated_at": collected_iso,
        "day_count": len(series),
        "source_note_en": (
            "Built by backfill-web: native RSS/HTML, extra feeds from web_backfill_feeds.yaml, "
            "and Bing News RSS (site: publisher) with pagination. Counts are keyword-matched headlines "
            f"in a ~{days}-day UTC window; coverage depends on what those surfaces returned."
        ),
    }
    timeseries_path.parent.mkdir(parents=True, exist_ok=True)
    timeseries_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if errors:
        data["_warnings"] = errors
    return data
