"use client";

import dynamic from "next/dynamic";
import type { NewsItem } from "@/lib/types";
import { climateCountByDay } from "@/lib/aggregate";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading chart…</p>,
});

export function ChartClimateTimeline({ items }: { items: NewsItem[] }) {
  const { dates, counts } = climateCountByDay(items);
  const data: Data[] = [
    {
      type: "scatter",
      mode: "lines+markers",
      x: dates,
      y: counts,
      line: { color: "#58a6ff", shape: "spline", smoothing: 0.35 },
      marker: { size: 8, color: "#58a6ff" },
    },
  ];
  const layout: Partial<Layout> = {
    paper_bgcolor: "#161b22",
    plot_bgcolor: "#161b22",
    font: { color: "#e6edf3", size: 12 },
    margin: { t: 24, r: 16, b: 64, l: 48 },
    xaxis: { title: { text: "Date" }, gridcolor: "#30363d" },
    yaxis: { title: { text: "Climate items" }, gridcolor: "#30363d", rangemode: "tozero" },
    showlegend: false,
  };
  const config: Partial<Config> = { displayModeBar: false, responsive: true };
  if (dates.length === 0) {
    return <p className="muted">No dated climate items to plot.</p>;
  }
  return <Plot data={data} layout={layout} config={config} style={{ width: "100%", height: 360 }} />;
}
