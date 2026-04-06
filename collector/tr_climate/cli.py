from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tr_climate.collect import run_collect
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

    args = p.parse_args(argv)
    if args.cmd == "collect":
        out = args.output.resolve()
        run_collect(out, sources_path=args.sources, keywords_path=args.keywords)
        print(f"Wrote {out / 'items.json'} and manifest.json")
        return 0
    if args.cmd == "quality":
        path = args.data.resolve()
        warns = run_quality(path)
        for w in warns:
            print(f"WARNING: {w}", file=sys.stderr)
        return 0 if not warns else 0  # warnings are non-fatal for CI
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
