import { DataCoverage } from "@/components/DataCoverage";
import type { Manifest } from "@/lib/types";
import manifest from "../../public/data/manifest.json";

const m = manifest as Manifest;

export default function MethodologyPage() {
  return (
    <div className="methodology-page">
      <h1>Methodology</h1>

      <DataCoverage manifest={m} />

      <div className="card">
        <h2>Trend file</h2>
        <p>
          <code>timeseries.json</code> stores one row per UTC day: per-outlet counts of all rows and
          climate-flagged rows from that collector run. Each scheduled run adds or replaces today (UTC)
          and keeps a rolling window of the last 30 days; older days are removed from the file (but
          remain in Git history if you need to rebuild via <code>tr_climate backfill-git</code>). For an initial
          chart without git history, <code>tr_climate backfill-web</code> can rebuild the file from RSS plus Bing
          News (see README); methodology and coverage differ slightly from the daily snapshot run.
        </p>
      </div>

      <div className="card">
        <h2>Data</h2>
        <p>
          Headlines (and short blurbs when RSS provides them) from eight outlets, via public listing
          pages and feeds. Full articles and TV transcripts are not ingested.
        </p>
        <p>
          <strong>Climate-related</strong> if title or description matches any phrase in the keyword
          list (version <code>{m.keyword_list_version}</code>), after Unicode normalization and
          case-folding.
        </p>
        <p>
          <strong>Topics</strong> (energy, transport, disasters, diplomacy) use smaller keyword
          sets; they are separate from the climate flag.
        </p>
      </div>

      <div className="card">
        <h2>Caveats</h2>
        <ul className="muted">
          <li>String matching only — not exhaustive for nuance or synonyms.</li>
          <li>Feeds and HTML layouts change; adapters need maintenance.</li>
          <li>Counts are mentions, not sentiment or fact-checking.</li>
        </ul>
      </div>

      <div className="card">
        <h2>Snapshot</h2>
        <ul className="muted" style={{ margin: 0, paddingLeft: "1.25rem" }}>
          <li>
            Generated: <code>{m.generated_at}</code>
          </li>
          <li>
            Items: <strong>{m.item_count}</strong> · climate-flagged:{" "}
            <strong>{m.climate_related_count}</strong>
          </li>
          <li>
            Schema: <code>{m.data_schema_version}</code>
          </li>
        </ul>
        <p className="muted" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
          Keywords: <code>collector/keywords.yaml</code>
        </p>
      </div>
    </div>
  );
}
