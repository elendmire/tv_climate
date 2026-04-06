from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tr_climate.history import ROLLING_WINDOW_DAYS, TIMESERIES_SCHEMA_VERSION, row_from_items_for_date


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _commits_touching_items(repo: Path, since_days: int = 50) -> list[str]:
    """Newest-first commits touching items.json within ~since_days (calendar) for rolling backfill."""
    r = _git(
        repo,
        "log",
        f"--since={since_days} days ago",
        "--format=%H",
        "--",
        "web/public/data/items.json",
    )
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def _git_show(repo: Path, commit: str, path: str) -> str | None:
    r = _git(repo, "show", f"{commit}:{path}")
    if r.returncode != 0:
        return None
    return r.stdout


def _manifest_day_key(manifest: dict[str, Any]) -> str | None:
    raw = manifest.get("generated_at")
    if not raw or not isinstance(raw, str):
        return None
    try:
        # "2026-04-06T21:13:01Z" or with offset
        if raw.endswith("Z"):
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).date().isoformat()
    except ValueError:
        return None


def _commit_day_key(repo: Path, commit: str) -> str:
    r = _git(repo, "log", "-1", "--format=%ct", commit)
    if r.returncode != 0 or not r.stdout.strip():
        return datetime.now(timezone.utc).date().isoformat()
    ts = int(r.stdout.strip())
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()


def backfill_timeseries_from_git(
    repo_root: Path,
    timeseries_path: Path,
    max_days: int = ROLLING_WINDOW_DAYS,
    history_since_days: int = 50,
) -> dict[str, Any]:
    """
    Rebuild timeseries from git history of items.json (newest commit wins per UTC day).
    Scans commits in a recent window, then keeps the last max_days by calendar date.
    Missing calendar days have no row — cannot invent data without a commit.
    """
    commits = _commits_touching_items(repo_root, since_days=history_since_days)
    rows_by_date: dict[str, dict[str, Any]] = {}

    for commit in commits:
        items_txt = _git_show(repo_root, commit, "web/public/data/items.json")
        if not items_txt or not items_txt.strip():
            continue
        try:
            items = json.loads(items_txt)
        except json.JSONDecodeError:
            continue
        if not isinstance(items, list) or not items:
            continue

        man_txt = _git_show(repo_root, commit, "web/public/data/manifest.json")
        date_key: str | None = None
        if man_txt:
            try:
                man = json.loads(man_txt)
                if isinstance(man, dict):
                    date_key = _manifest_day_key(man)
            except json.JSONDecodeError:
                pass
        if not date_key:
            date_key = _commit_day_key(repo_root, commit)

        if date_key in rows_by_date:
            continue

        rows_by_date[date_key] = row_from_items_for_date(items, date_key)

    dates_sorted = sorted(rows_by_date.keys())
    if len(dates_sorted) > max_days:
        dates_sorted = dates_sorted[-max_days:]
    series = [rows_by_date[d] for d in dates_sorted]

    data: dict[str, Any] = {
        "data_schema_version": TIMESERIES_SCHEMA_VERSION,
        "series": series,
        "updated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "day_count": len(series),
        "source_note_en": (
            "Rows rebuilt from git history of web/public/data/items.json "
            f"(commits since ~{history_since_days} days ago; newest commit per UTC day; "
            f"then last {max_days} calendar dates kept)."
        ),
    }
    timeseries_path.parent.mkdir(parents=True, exist_ok=True)
    timeseries_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
