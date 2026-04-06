from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def run_quality(data_path: Path) -> list[str]:
    """Return warning messages (duplicates, empty sources, zero climate hits)."""
    warnings: list[str] = []
    if not data_path.is_file():
        warnings.append(f"Missing data file: {data_path}")
        return warnings

    items: list[dict[str, Any]] = json.loads(data_path.read_text(encoding="utf-8"))
    ids = [x.get("id") for x in items]
    id_counts = Counter(ids)
    dupes = [i for i, c in id_counts.items() if c > 1]
    if dupes:
        warnings.append(f"Duplicate ids detected: {len(dupes)} id(s)")

    urls = [x.get("url") for x in items]
    url_counts = Counter(urls)
    if any(c > 1 for c in url_counts.values()):
        warnings.append("Duplicate URLs in items.json")

    manifest_path = data_path.parent / "manifest.json"
    if manifest_path.is_file():
        man = json.loads(manifest_path.read_text(encoding="utf-8"))
        per = man.get("per_source_counts") or {}
        for sid, n in per.items():
            if n == 0:
                warnings.append(f"Source returned zero items: {sid}")
        errs = man.get("errors") or []
        for e in errs:
            warnings.append(f"Collector error: {e}")
        if man.get("climate_related_count") == 0 and man.get("item_count", 0) > 0:
            warnings.append("No climate-related items in this run (keywords may need tuning).")

    return warnings
