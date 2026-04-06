from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tr_climate.collect import run_collect
from tr_climate.git_backfill import backfill_timeseries_from_git
from tr_climate.quality import run_quality

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = _REPO_ROOT / "web" / "public" / "data"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tr_climate")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("collect", help="Fetch sources and write web/public/data")
    c.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_DATA,
        help="Output directory for items.json and manifest.json",
    )
    c.add_argument("--sources", type=Path, default=None)
    c.add_argument("--keywords", type=Path, default=None)

    q = sub.add_parser("quality", help="Check items.json + manifest for issues")
    q.add_argument(
        "--data",
        type=Path,
        default=_DEFAULT_DATA / "items.json",
        help="Path to items.json",
    )

    b = sub.add_parser(
        "backfill-git",
        help="Rebuild timeseries.json from git history of items.json (max 30 UTC days)",
    )
    b.add_argument(
        "--repo",
        type=Path,
        default=_REPO_ROOT,
        help="Git repository root",
    )
    b.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_DATA / "timeseries.json",
        help="Path to timeseries.json",
    )
    b.add_argument("--max-days", type=int, default=30, help="Keep last N calendar dates after merge")
    b.add_argument(
        "--history-since-days",
        type=int,
        default=50,
        help="Only scan git commits to items.json newer than this many days",
    )

    args = p.parse_args(argv)
    if args.cmd == "collect":
        out = args.output.resolve()
        run_collect(out, sources_path=args.sources, keywords_path=args.keywords)
        print(f"Wrote {out / 'items.json'}, manifest.json, timeseries.json")
        return 0
    if args.cmd == "quality":
        path = args.data.resolve()
        warns = run_quality(path)
        for w in warns:
            print(f"WARNING: {w}", file=sys.stderr)
        return 0 if not warns else 0  # warnings are non-fatal for CI
    if args.cmd == "backfill-git":
        repo = args.repo.resolve()
        outp = args.output.resolve()
        data = backfill_timeseries_from_git(
            repo,
            outp,
            max_days=args.max_days,
            history_since_days=args.history_since_days,
        )
        print(f"Wrote {outp} with {data.get('day_count', 0)} day(s) from git history.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
