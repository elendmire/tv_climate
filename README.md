# Turkey TV / news — climate mention tracker

Tracks climate-related keywords in headlines from eight Turkish outlets. Data is fetched over HTTP (HTML + RSS), no paid APIs. Dashboard: Next.js, Plotly, static export.

## Repo layout

- `collector/` — Python scraper and pipeline
- `web/` — Next.js app (deploy root for Vercel)
- `web/public/data/` — `items.json` (latest snapshot), `timeseries.json` (daily aggregates for charts), `manifest.json` (updated by CI)

## Collector

```bash
cd collector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m tr_climate collect --output ../web/public/data
python -m tr_climate quality --data ../web/public/data/items.json
pytest -q
```

**Trends (`timeseries.json`):** Each `collect` appends or replaces the current UTC day and keeps a rolling window of the last **30** days (older days are dropped). The file is committed like `items.json`, so history lives in Git. To rebuild the series from past snapshots of `items.json`, run from `collector/`:

`python -m tr_climate backfill-git --repo .. --output ../web/public/data/timeseries.json`

That only recovers days that actually appear in `git log` for `web/public/data/items.json` (e.g. one point until daily CI has run for many days).

**One-time web backfill (no git history needed):** pulls native RSS (full feed), optional extra feeds in `collector/config/web_backfill_feeds.yaml`, and paginated Bing News RSS per publisher (`site:`), then rebuilds `timeseries.json` for the last 30 UTC days. Publisher links are taken from Bing’s redirect URL when needed. Respect Bing’s terms; use for research / personal dashboards.

```bash
cd collector
python -m tr_climate backfill-web --output ../web/public/data/timeseries.json --days 30
```

Daily `collect` still updates today’s row and trims to 30 days; it clears the backfill `source_note_en` when it runs.

## Web

```bash
cd web
npm install
npm run dev
npm run build
```

Static files land in `web/out/`.

## Vercel

- **Root Directory:** `web` (Framework: Next.js). If the repo root is used instead, the root `vercel.json` builds `web/` and outputs `web/out`.
- After changing settings, redeploy from the Deployments tab.

## GitHub Actions

[`.github/workflows/collect.yml`](.github/workflows/collect.yml) runs on a schedule, refreshes `web/public/data/`, commits when files change, and runs quality checks. Under **Settings → Actions → General → Workflow permissions**, allow read/write for contents so `GITHUB_TOKEN` can push. Branch protection may require a PAT.

## Methodology & config

- In-app: `/methodology`
- Keywords: [`collector/keywords.yaml`](collector/keywords.yaml)
- Schema: [`collector/schema/news-item.schema.json`](collector/schema/news-item.schema.json)
- Sources: [`collector/config/sources.yaml`](collector/config/sources.yaml) — TRT Haber (HTML), NTV, Habertürk, Anadolu Agency, Yeni Şafak, Milliyet, A Haber, CNN Türk (RSS/Atom)

## License

MIT
