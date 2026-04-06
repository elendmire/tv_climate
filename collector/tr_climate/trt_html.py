from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from tr_climate.http_client import client
from tr_climate.models import RawItem

_ARTICLE_RE = re.compile(
    r"^https://www\.trthaber\.com/haber/[\w-]+/[\w-]+-\d+\.html$",
)


def fetch_trt_listing(url: str, source_id: str, max_items: int) -> list[RawItem]:
    out: list[RawItem] = []
    seen: set[str] = set()
    with client() as c:
        r = c.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.select("a.site-url[href]"):
        href = (a.get("href") or "").strip()
        if not _ARTICLE_RE.match(href):
            continue
        if href in seen:
            continue
        seen.add(href)
        title = (a.get("title") or a.get_text(strip=True) or "").strip()
        if not title:
            continue
        out.append(
            RawItem(
                source_id=source_id,
                title=title,
                description="",
                url=href,
                published_at=None,
            )
        )
        if len(out) >= max_items:
            break
    return out


def fetch_trt_pages(listing_urls: list[str], source_id: str, max_items: int) -> list[RawItem]:
    merged: list[RawItem] = []
    seen: set[str] = set()
    for page in listing_urls:
        abs_url = urljoin("https://www.trthaber.com/", page)
        for item in fetch_trt_listing(abs_url, source_id, max_items):
            if item.url in seen:
                continue
            seen.add(item.url)
            merged.append(item)
            if len(merged) >= max_items:
                return merged
    return merged
