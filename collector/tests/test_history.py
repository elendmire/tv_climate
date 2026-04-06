from datetime import datetime, timezone
from pathlib import Path

from tr_climate.history import merge_daily_timeseries
from tr_climate.models import NewsItem, finalize_item
from tr_climate.models import RawItem


def _item(url: str, sid: str, climate: bool) -> NewsItem:
    raw = RawItem(
        source_id=sid,
        title="t",
        description="",
        url=url,
        published_at=None,
    )
    return finalize_item(raw, climate, ["k"] if climate else [], [], collected_at=datetime.now(timezone.utc))


def test_merge_timeseries_two_days(tmp_path: Path) -> None:
    p = tmp_path / "timeseries.json"
    d1 = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)
    d2 = datetime(2026, 4, 2, 12, 0, tzinfo=timezone.utc)
    items1 = [_item("https://a.com/1", "s1", True), _item("https://a.com/2", "s1", False)]
    items2 = [_item("https://a.com/3", "s1", True), _item("https://a.com/4", "s1", True)]
    merge_daily_timeseries(p, items1, d1)
    merge_daily_timeseries(p, items2, d2)
    import json

    data = json.loads(p.read_text(encoding="utf-8"))
    assert len(data["series"]) == 2
    assert data["series"][0]["date"] == "2026-04-01"
    assert data["series"][0]["by_source"]["s1"]["climate"] == 1
    assert data["series"][1]["by_source"]["s1"]["climate"] == 2


def test_same_day_overwrites(tmp_path: Path) -> None:
    p = tmp_path / "ts.json"
    day = datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc)
    merge_daily_timeseries(p, [_item("https://x/1", "a", True)], day)
    merge_daily_timeseries(p, [_item("https://x/2", "a", False), _item("https://x/3", "a", False)], day)
    import json

    data = json.loads(p.read_text(encoding="utf-8"))
    assert len(data["series"]) == 1
    assert data["series"][0]["totals"]["items"] == 2
