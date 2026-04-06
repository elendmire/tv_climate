# Turkey TV & news — climate mention tracker

Inspired by [television-news-analyser](https://github.com/polomarcus/television-news-analyser): collect recent headlines from major Turkish outlets over **plain HTTP** (HTML + RSS, no API keys), tag climate-related items with Turkish and English keywords, and visualize them in a static **Next.js** site with **Plotly**. UI is English; article titles stay Turkish.

## Layout

- `collector/` — Python 3.11+ scraper and data pipeline
- `web/` — Next.js static export for [Vercel](https://vercel.com/) (set project root to `web`)
- `web/public/data/` — generated `items.json`, `manifest.json` (committed by CI)

## Local development

### Collector

```bash
cd collector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m tr_climate collect --output ../web/public/data
python -m tr_climate quality --data ../web/public/data/items.json
pytest -q
```

### Web

```bash
cd web
npm install
npm run dev
```

Build static export:

```bash
npm run build
```

Open `out/` or deploy the `web` folder to Vercel.

## GitHub Actions

Workflow [`.github/workflows/collect.yml`](.github/workflows/collect.yml) runs on a schedule, refreshes `web/public/data/`, commits if changed, and runs a data-quality check. Grant **Settings → Actions → Workflow permissions → Read and write** so `GITHUB_TOKEN` can push. If `main` is branch-protected against the default token, add a PAT secret and use it in the workflow (tokens are free; see plan notes).

## Methodology

See the in-app **Methodology** page. Keyword list version is defined in [`collector/keywords.yaml`](collector/keywords.yaml).

## Schema

News items follow `collector/schema/news-item.schema.json` (`data_schema_version` currently `1`).

## Sources (8)

Configured in [`collector/config/sources.yaml`](collector/config/sources.yaml): TRT Haber (HTML listings), NTV, Habertürk, Anadolu Agency, Yeni Şafak, Milliyet, A Haber, CNN Türk (RSS/Atom over HTTP). Sites change; adapters may need updates.

## License

MIT (add your name/year as needed).
