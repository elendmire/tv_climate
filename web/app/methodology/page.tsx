import type { Manifest } from "@/lib/types";
import manifest from "../../public/data/manifest.json";

const m = manifest as Manifest;

export default function MethodologyPage() {
  return (
    <>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "0.75rem" }}>Methodology</h1>

      <div className="card">
        <h2>What this measures</h2>
        <p>
          We periodically fetch public listing pages and RSS/Atom feeds from eight large Turkish
          outlets (see the main dashboard). Each item is a <strong>headline</strong> (plus short
          description when the feed provides it). We do <strong>not</strong> download full article
          bodies or broadcast transcripts.
        </p>
        <p>
          An item is flagged <strong>climate-related</strong> if its title or description contains
          any phrase from our Turkish and English keyword list (version{" "}
          <code>{m.keyword_list_version}</code>), after Unicode normalization and case-folding.
        </p>
        <p>
          <strong>Topics</strong> (energy, transport, disasters, diplomacy) are separate,
          rule-based tags using smaller keyword subsets. They are independent of the climate flag
          and are meant for coarse grouping only.
        </p>
      </div>

      <div className="card">
        <h2>Limitations</h2>
        <ul className="muted">
          <li>Keyword matching misses nuance and synonyms; counts are a lower bound on attention.</li>
          <li>Outlet homepages and feeds change; collectors need occasional maintenance.</li>
          <li>This is not a sentiment or accuracy analysis — only mention frequency.</li>
        </ul>
      </div>

      <div className="card">
        <h2>Current dataset snapshot</h2>
        <ul className="muted" style={{ margin: 0, paddingLeft: "1.25rem" }}>
          <li>
            Last ingest: <code>{m.generated_at}</code>
          </li>
          <li>
            Items in file: <strong>{m.item_count}</strong> (climate-flagged:{" "}
            <strong>{m.climate_related_count}</strong>)
          </li>
          <li>
            Schema version: <code>{m.data_schema_version}</code>
          </li>
        </ul>
        <p className="muted" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
          Full keyword YAML lives in the repository at <code>collector/keywords.yaml</code>.
        </p>
      </div>
    </>
  );
}
