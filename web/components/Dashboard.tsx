"use client";

import { useEffect, useState } from "react";
import { ChartHistoryClimate } from "@/components/charts/ChartHistoryClimate";
import { ChartHistoryPercent } from "@/components/charts/ChartHistoryPercent";
import { ChartClimateByChannel } from "@/components/charts/ChartClimateByChannel";
import { ChartClimateTimeline } from "@/components/charts/ChartClimateTimeline";
import { ChartTotalByChannel } from "@/components/charts/ChartTotalByChannel";
import { labelForSource } from "@/lib/aggregate";
import type { NewsItem, TimeseriesFile } from "@/lib/types";

export function Dashboard() {
  const [items, setItems] = useState<NewsItem[] | null>(null);
  const [ts, setTs] = useState<TimeseriesFile | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetch("/data/items.json").then((r) => {
        if (!r.ok) throw new Error(`items.json HTTP ${r.status}`);
        return r.json();
      }),
      fetch("/data/timeseries.json").then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([itemData, tsData]) => {
        if (cancelled) return;
        setItems(itemData as NewsItem[]);
        setTs(tsData as TimeseriesFile | null);
      })
      .catch((e: Error) => {
        if (!cancelled) setErr(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (err) {
    return (
      <div className="card">
        <p>Could not load data ({err}).</p>
        <p className="muted">
          Run <code>python -m tr_climate collect</code> in <code>collector/</code>.
        </p>
      </div>
    );
  }

  if (!items) {
    return <p className="muted">Loading…</p>;
  }

  const climate = items.filter((x) => x.climate_related);
  const historyDays = ts?.series?.length ?? 0;
  const showHistory = ts && historyDays > 0;

  return (
    <>
      {showHistory ? (
        <>
          <div className="card">
            <h2>Daily history — climate counts by outlet</h2>
            <p className="card-note">
              One point per outlet per UTC day. The file keeps a rolling window of up to 30 UTC days;
              each run adds or replaces today.{" "}
              {historyDays < 2
                ? "Run the collector on more calendar days (or use daily CI) to see a line across days."
                : `${historyDays} day(s) in the current series.`}
            </p>
            <div className="plot-wrap">
              <ChartHistoryClimate ts={ts} />
            </div>
          </div>
          <div className="card">
            <h2>Daily history — share of climate-flagged rows</h2>
            <p className="card-note">
              Climate rows ÷ all rows that day in the snapshot, per outlet (depends on feed depth each day).
            </p>
            <div className="plot-wrap">
              <ChartHistoryPercent ts={ts} />
            </div>
          </div>
        </>
      ) : (
        <div className="card">
          <h2>Daily history</h2>
          <p className="card-note" style={{ marginBottom: 0 }}>
            <code>timeseries.json</code> appears after the collector runs. Daily GitHub Actions adds one row
            per UTC day and trims to the last 30 days. Until several distinct days exist in the file, charts
            stay empty or show a single point.
          </p>
        </div>
      )}

      <div className="card">
        <h2>Latest snapshot — by outlet</h2>
        <p className="card-note">Climate-flagged headlines in the current file.</p>
        <div className="plot-wrap">
          <ChartClimateByChannel items={items} />
        </div>
      </div>

      <div className="card">
        <h2>Latest snapshot — by published date</h2>
        <p className="card-note">When <code>published_at</code> exists on the row.</p>
        <div className="plot-wrap">
          <ChartClimateTimeline items={items} />
        </div>
      </div>

      <div className="card">
        <h2>Latest snapshot — volume</h2>
        <p className="card-note">All rows in this file.</p>
        <div className="plot-wrap">
          <ChartTotalByChannel items={items} />
        </div>
      </div>

      <div className="card">
        <h2>Climate-flagged rows</h2>
        <p className="card-note">
          {climate.length} of {items.length}
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
