from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tr_climate.textnorm import normalize_text


@dataclass
class KeywordConfig:
  version: str
  climate_keywords: dict[str, list[str]]
  topic_rules: dict[str, dict[str, list[str]]]


def load_keywords(path: Path | None = None) -> KeywordConfig:
  base = Path(__file__).resolve().parent.parent
  p = path or (base / "keywords.yaml")
  raw: dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8"))
  return KeywordConfig(
    version=str(raw.get("version", "0")),
    climate_keywords=raw.get("climate_keywords") or {},
    topic_rules=raw.get("topic_rules") or {},
  )


def find_substring_matches(norm_text: str, phrases: list[str]) -> list[str]:
  found: list[str] = []
  seen: set[str] = set()
  for phrase in phrases:
    p = normalize_text(phrase)
    if not p:
      continue
    if p in norm_text and phrase not in seen:
      found.append(phrase)
      seen.add(phrase)
  return found


def match_climate(cfg: KeywordConfig, title: str, description: str) -> tuple[bool, list[str]]:
  blob = normalize_text(f"{title} {description}")
  hits: list[str] = []
  for lang in cfg.climate_keywords:
    hits.extend(find_substring_matches(blob, cfg.climate_keywords[lang]))
  # de-dupe preserving order
  out: list[str] = []
  s: set[str] = set()
  for h in hits:
    if h not in s:
      out.append(h)
      s.add(h)
  return (len(out) > 0, out)


def match_topics(cfg: KeywordConfig, title: str, description: str) -> list[str]:
  blob = normalize_text(f"{title} {description}")
  topics: list[str] = []
  for topic_id, langs in cfg.topic_rules.items():
    phrases: list[str] = []
    for _lang, plist in langs.items():
      phrases.extend(plist)
    if find_substring_matches(blob, phrases):
      topics.append(topic_id)
  return topics
