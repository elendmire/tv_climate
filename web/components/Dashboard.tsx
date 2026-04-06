"use client";

import { useEffect, useState } from "react";
import type { NewsItem } from "@/lib/types";
import { ChartClimateByChannel } from "@/components/charts/ChartClimateByChannel";
import { ChartClimateTimeline } from "@/components/charts/ChartClimateTimeline";
import { ChartTotalByChannel } from "@/components/charts/ChartTotalByChannel";
import { labelForSource } from "@/lib/aggregate";

export function Dashboard() {
  const [items, setItems] = useState<NewsItem[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/items.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: NewsItem[]) => setItems(data))
      .catch((e: Error) => setErr(e.message));
  }, []);

  if (err) {
    return (
      <div className="card">
        <p>Could not load data: {err}</p>
        <p className="muted">Run the collector to generate web/public/data/items.json.</p>
      </div>
    );
  }

  if (!items) {
    return <p className="muted">Loading dataset…</p>;
  }

  const climate = items.filter((x) => x.climate_related);

  return (
    <>
      <div className="card">
        <h2>Climate-flagged items by outlet</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Count of headlines matching climate keywords in the current snapshot.
        </p>
        <div className="plot-wrap">
          <ChartClimateByChannel items={items} />
        </div>
      </div>

      <div className="card">
        <h2>Climate mentions over time (by published date)</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Daily counts when <code>published_at</code> is available; otherwise items may fall back to
          collection date in the pipeline.
        </p>
        <div className="plot-wrap">
          <ChartClimateTimeline items={items} />
        </div>
      </div>

      <div className="card">
        <h2>All captured headlines by outlet (sample volume)</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Total rows in this run, including non-climate stories.
        </p>
        <div className="plot-wrap">
          <ChartTotalByChannel items={items} />
        </div>
      </div>

      <div className="card">
        <h2>Climate-related headlines</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Showing {climate.length} of {items.length} items. Open the original outlet page for full
          context.
        </p>
        <div style={{ overflowX: "auto" }}>
          <table className="data">
            <thead>
              <tr>
                <th>Outlet</th>
                <th>Title</th>
                <th>Keywords</th>
                <th>Topics</th>
              </tr>
            </thead>
            <tbody>
              {climate.map((it) => (
                <tr key={it.id}>
                  <td>{labelForSource(it.source_id)}</td>
                  <td>
                    <a href={it.url} target="_blank" rel="noopener noreferrer">
                      {it.title}
                    </a>
                  </td>
                  <td className="muted">{it.matched_keywords.join(", ")}</td>
                  <td className="muted">{it.topics.join(", ") || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
