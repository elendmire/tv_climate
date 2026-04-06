from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tr_climate.models import NewsItem

TIMESERIES_SCHEMA_VERSION = 1
ROLLING_WINDOW_DAYS = 30
DEFAULT_MAX_DAYS = ROLLING_WINDOW_DAYS


def _aggregate_by_source(items: list) -> tuple[dict[str, dict[str, int]], int, int]:
    """Items: NewsItem or dict with source_id, climate_related."""
    by_source: dict[str, dict[str, int]] = {}
    for it in items:
        if hasattr(it, "source_id"):
            sid = it.source_id
            is_climate = bool(it.climate_related)
        else:
            sid = str(it.get("source_id", ""))
            is_climate = bool(it.get("climate_related"))
        if not sid:
            continue
        if sid not in by_source:
            by_source[sid] = {"items": 0, "climate": 0}
        by_source[sid]["items"] += 1
        if is_climate:
            by_source[sid]["climate"] += 1
    climate_n = sum(b["climate"] for b in by_source.values())
    total_items = sum(b["items"] for b in by_source.values())
    return by_source, total_items, climate_n


def row_from_items_for_date(items: list, date_key: str) -> dict[str, Any]:
    by_source, total_items, climate_n = _aggregate_by_source(items)
    return {
        "date": date_key,
        "by_source": by_source,
        "totals": {"items": total_items, "climate": climate_n},
    }


def _row_for_day(items: list[NewsItem], date_key: str) -> dict[str, Any]:
    return row_from_items_for_date(items, date_key)


def merge_daily_timeseries(
    path: Path,
    items: list[NewsItem],
    now: datetime,
    max_days: int = DEFAULT_MAX_DAYS,
) -> dict[str, Any]:
    """
    Append or replace one row per UTC calendar day. Same-day re-runs overwrite that day.
    """
    date_key = now.astimezone(timezone.utc).date().isoformat()
    new_row = _row_for_day(items, date_key)

    data: dict[str, Any] = {
        "data_schema_version": TIMESERIES_SCHEMA_VERSION,
        "series": [],
    }
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))

    series_list: list[dict[str, Any]] = list(data.get("series") or [])
    by_date = {row["date"]: row for row in series_list if "date" in row}
    by_date[date_key] = new_row
    dates_sorted = sorted(by_date.keys())
    if len(dates_sorted) > max_days:
        dates_sorted = dates_sorted[-max_days:]
    data["series"] = [by_date[d] for d in dates_sorted]
    data["data_schema_version"] = TIMESERIES_SCHEMA_VERSION
    data["updated_at"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    data["day_count"] = len(data["series"])
    data.pop("source_note_en", None)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
