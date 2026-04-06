from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


DATA_SCHEMA_VERSION = 1


def stable_id(url: str) -> str:
  return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


@dataclass
class RawItem:
  source_id: str
  title: str
  description: str
  url: str
  published_at: str | None


@dataclass
class NewsItem:
  data_schema_version: int
  id: str
  source_id: str
  published_at: str | None
  title: str
  description: str
  url: str
  language: str
  climate_related: bool
  matched_keywords: list[str]
  topics: list[str]
  collected_at: str

  def to_json_dict(self) -> dict[str, Any]:
    d = asdict(self)
    return d


def finalize_item(
  raw: RawItem,
  climate_related: bool,
  matched_keywords: list[str],
  topics: list[str],
  collected_at: datetime | None = None,
) -> NewsItem:
  when = collected_at or datetime.now(timezone.utc)
  return NewsItem(
    data_schema_version=DATA_SCHEMA_VERSION,
    id=stable_id(raw.url),
    source_id=raw.source_id,
    published_at=raw.published_at,
    title=raw.title.strip(),
    description=(raw.description or "").strip()[:2000],
    url=raw.url,
    language="tr",
    climate_related=climate_related,
    matched_keywords=matched_keywords,
    topics=topics,
    collected_at=when.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
  )
