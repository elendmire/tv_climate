from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from tr_climate.history import ROLLING_WINDOW_DAYS, merge_daily_timeseries
from tr_climate.matcher import KeywordConfig, load_keywords, match_climate, match_topics
from tr_climate.models import NewsItem, finalize_item
from tr_climate.rss_fetch import fetch_rss_feed
from tr_climate.trt_html import fetch_trt_pages


def _load_sources(path: Path) -> list[dict[str, Any]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(raw.get("sources") or [])


def _fetch_source(cfg: dict[str, Any]) -> list:
    stype = cfg["type"]
    sid = cfg["id"]
    mx = int(cfg.get("max_items") or 30)
    if stype == "html_trt":
        urls = list(cfg.get("listing_urls") or [])
        return fetch_trt_pages(urls, sid, mx)
    if stype == "rss":
        return fetch_rss_feed(str(cfg["feed_url"]), sid, mx)
    raise ValueError(f"Unknown source type: {stype}")


def run_collect(
    output_dir: Path,
    sources_path: Path | None = None,
    keywords_path: Path | None = None,
) -> tuple[list[NewsItem], KeywordConfig]:
    base = Path(__file__).resolve().parent.parent
    sp = sources_path or (base / "config" / "sources.yaml")
    kw_cfg = load_keywords(keywords_path)
    sources = _load_sources(sp)
    raws: list = []
    per_source_counts: dict[str, int] = {}
    errors: list[str] = []
    for src in sources:
        sid = src["id"]
        try:
            items = _fetch_source(src)
            raws.extend(items)
            per_source_counts[sid] = len(items)
        except Exception as e:  # noqa: BLE001 — collect best-effort per outlet
            errors.append(f"{sid}: {e}")
            per_source_counts[sid] = 0

    by_url: dict[str, Any] = {}
    for raw in raws:
        if raw.url not in by_url:
            by_url[raw.url] = raw

    finalized: list[NewsItem] = []
    now = datetime.now(timezone.utc)
    for raw in by_url.values():
        rel, kws = match_climate(kw_cfg, raw.title, raw.description)
        topics = match_topics(kw_cfg, raw.title, raw.description)
        finalized.append(finalize_item(raw, rel, kws, topics, collected_at=now))

    finalized.sort(key=lambda x: (x.published_at or "", x.url), reverse=True)
    finalized = finalized[:2500]

    output_dir.mkdir(parents=True, exist_ok=True)
    items_path = output_dir / "items.json"
    per_cap = max(int(s.get("max_items") or 0) for s in sources) if sources else 40
    manifest = {
        "generated_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "keyword_list_version": kw_cfg.version,
        "data_schema_version": 1,
        "item_count": len(finalized),
        "climate_related_count": sum(1 for x in finalized if x.climate_related),
        "per_source_counts": per_source_counts,
        "errors": errors,
        "coverage": {
            "update_schedule_cron_utc": "30 6 * * *",
            "update_schedule_note_en": "GitHub Actions runs daily around 06:30 UTC (see .github/workflows/collect.yml).",
            "snapshot_mode": True,
            "per_source_item_cap": per_cap,
            "max_rows_in_file": 2500,
            "window_note_en": (
                "Each run replaces items.json with a new snapshot from current listing pages and RSS/Atom "
                "feeds. Rows are whatever those surfaces show at fetch time—usually the last hours to a "
                "few days per outlet, not a curated multi-year archive."
            ),
            "trends_note_en": (
                f"timeseries.json keeps a rolling window of {ROLLING_WINDOW_DAYS} UTC days; each collect adds "
                "or updates today and drops older days."
            ),
            "timeseries_rolling_days": ROLLING_WINDOW_DAYS,
        },
        "timeseries": {
            "path": "data/timeseries.json",
            "description_en": "Daily counts per outlet (items + climate-flagged) for trend charts.",
            "rolling_window_days": ROLLING_WINDOW_DAYS,
        },
    }
    ts_path = output_dir / "timeseries.json"
    ts_data = merge_daily_timeseries(ts_path, finalized, now, max_days=ROLLING_WINDOW_DAYS)
    manifest["timeseries"]["day_count"] = ts_data.get("day_count", 0)
    items_path.write_text(
        json.dumps([x.to_json_dict() for x in finalized], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return finalized, kw_cfg
