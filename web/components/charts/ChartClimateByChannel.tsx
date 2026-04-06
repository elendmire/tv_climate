"use client";

import dynamic from "next/dynamic";
import type { NewsItem } from "@/lib/types";
import { climateCountBySource } from "@/lib/aggregate";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading chart…</p>,
});

export function ChartClimateByChannel({ items }: { items: NewsItem[] }) {
  const { labels, values } = climateCountBySource(items);
  const data: Data[] = [
    {
      type: "bar",
      x: labels,
      y: values,
      marker: { color: "#3fb950" },
    },
  ];
  const layout: Partial<Layout> = {
    paper_bgcolor: "#161b22",
    plot_bgcolor: "#161b22",
    font: { color: "#e6edf3", size: 12 },
    margin: { t: 32, r: 16, b: 120, l: 48 },
    xaxis: { tickangle: -35, title: { text: "Outlet" } },
    yaxis: { title: { text: "Climate-flagged items" }, gridcolor: "#30363d" },
    showlegend: false,
  };
  const config: Partial<Config> = {
    displayModeBar: false,
    responsive: true,
  };
  if (labels.length === 0) {
    return <p className="muted">No climate-flagged items in this snapshot.</p>;
  }
  return <Plot data={data} layout={layout} config={config} style={{ width: "100%", height: 380 }} />;
}
