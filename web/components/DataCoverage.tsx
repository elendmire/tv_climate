import type { Manifest } from "@/lib/types";

type Props = { manifest: Manifest };

export function DataCoverage({ manifest }: Props) {
  const c = manifest.coverage;
  if (!c) {
    return (
      <section className="card" aria-label="Dataset">
        <h2 className="card-heading">Dataset</h2>
        <p className="card-note" style={{ marginBottom: 0 }}>
          Last generated <time dateTime={manifest.generated_at}>{manifest.generated_at}</time>. Re-run the
          collector to refresh <code>manifest.json</code> with coverage details.
        </p>
      </section>
    );
  }

  return (
    <section className="card" aria-label="What this file covers">
      <h2 className="card-heading">What you are looking at</h2>
      <ul className="coverage-list">
        <li>
          <strong>Updates:</strong> {c.update_schedule_note_en} Cron:{" "}
          <code>{c.update_schedule_cron_utc}</code>
        </li>
        <li>
          <strong>Time depth:</strong> {c.window_note_en}
        </li>
        <li>
          <strong>Limits:</strong> up to <strong>{c.per_source_item_cap}</strong> rows per outlet per run,
          at most <strong>{c.max_rows_in_file}</strong> rows in the file after deduplication.
        </li>
        <li>
          <strong>Trends:</strong> {c.trends_note_en}
        </li>
      </ul>
      <p className="card-note" style={{ marginBottom: 0 }}>
        Snapshot time: <time dateTime={manifest.generated_at}>{manifest.generated_at}</time>
      </p>
    </section>
  );
}
