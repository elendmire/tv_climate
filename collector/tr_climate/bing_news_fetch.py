from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import feedparser

from tr_climate.http_client import client
from tr_climate.models import RawItem
from tr_climate.rss_fetch import _entry_link, _entry_summary, _entry_title


def unwrap_news_redirect_url(href: str) -> str:
    """Resolve Bing News apiclick wrapper to the publisher URL when present."""
    if not href:
        return href
    low = href.lower()
    if "bing.com/news/apiclick" not in low:
        return href
    q = parse_qs(urlparse(href).query)
    for key in ("url", "u"):
        if key in q and q[key]:
            return unquote(q[key][0])
    return href


def _parse_entry_published(entry: dict[str, Any]) -> str | None:
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
    if entry.get("published"):
        return str(entry["published"]).strip()
    if entry.get("updated"):
        return str(entry["updated"]).strip()
    return None


def fetch_bing_news_site(
    domain: str,
    source_id: str,
    *,
    max_pages: int = 22,
    per_page: int = 10,
    pause_sec: float = 0.35,
) -> list[RawItem]:
    """
    Page Bing News RSS for site:domain. Publisher links are taken from apiclick url=… when needed.
    """
    from urllib.parse import quote

    q = quote(f"site:{domain}")
    out: list[RawItem] = []
    seen: set[str] = set()

    with client(timeout=45.0) as c:
        for page in range(max_pages):
            first = page * per_page + 1
            url = (
                f"https://www.bing.com/news/search?q={q}&format=rss"
                f"&count={per_page}&first={first}"
            )
            r = c.get(url)
            if r.status_code != 200:
                break
            parsed = feedparser.parse(r.content)
            if not parsed.entries:
                break
            page_new = 0
            for entry in parsed.entries:
                e = dict(entry)
                link = _entry_link(e)
                if not link:
                    continue
                real = unwrap_news_redirect_url(link)
                if not real or real in seen:
                    continue
                seen.add(real)
                title = _entry_title(e)
                if not title:
                    continue
                out.append(
                    RawItem(
                        source_id=source_id,
                        title=title,
                        description=_entry_summary(e),
                        url=real,
                        published_at=_parse_entry_published(e),
                    )
                )
                page_new += 1
            if page_new == 0:
                break
            if page < max_pages - 1:
                time.sleep(pause_sec)
    return out
