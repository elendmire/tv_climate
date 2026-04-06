from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import feedparser

from tr_climate.http_client import client
from tr_climate.models import RawItem
from tr_climate.textnorm import strip_html_to_text


def _parse_date(entry: dict[str, Any]) -> str | None:
    if entry.get("published"):
        return str(entry["published"]).strip()
    if entry.get("updated"):
        return str(entry["updated"]).strip()
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        try:
            dt = datetime(
                t.tm_year,
                t.tm_mon,
                t.tm_mday,
                t.tm_hour,
                t.tm_min,
                t.tm_sec,
                tzinfo=timezone.utc,
            )
            return dt.isoformat().replace("+00:00", "Z")
        except (TypeError, ValueError):
            pass
    return None


def _entry_link(entry: dict[str, Any]) -> str | None:
    if entry.get("link"):
        return str(entry["link"]).strip()
    links = entry.get("links") or []
    for link in links:
        if link.get("rel") == "alternate" and link.get("href"):
            return str(link["href"]).strip()
    if links and links[0].get("href"):
        return str(links[0]["href"]).strip()
    return None


def _entry_title(entry: dict[str, Any]) -> str:
    title = entry.get("title") or ""
    return str(title).strip()


def _entry_summary(entry: dict[str, Any]) -> str:
    s = entry.get("summary") or entry.get("description") or ""
    return strip_html_to_text(str(s), max_len=800)


def fetch_rss_feed(feed_url: str, source_id: str, max_items: int) -> list[RawItem]:
    with client() as c:
        r = c.get(feed_url)
        r.raise_for_status()
        body = r.content
    parsed = feedparser.parse(body)
    out: list[RawItem] = []
    for entry in parsed.entries[:max_items]:
        e = dict(entry)
        link = _entry_link(e)
        if not link:
            continue
        title = _entry_title(e)
        if not title:
            continue
        out.append(
            RawItem(
                source_id=source_id,
                title=title,
                description=_entry_summary(e),
                url=link,
                published_at=_parse_date(e),
            )
        )
    return out
