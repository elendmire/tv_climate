"use client";

import dynamic from "next/dynamic";
import type { NewsItem } from "@/lib/types";
import { totalBySource } from "@/lib/aggregate";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading chart…</p>,
});

export function ChartTotalByChannel({ items }: { items: NewsItem[] }) {
  const { labels, values } = totalBySource(items);
  const data: Data[] = [
    {
      type: "bar",
      orientation: "h",
      y: labels,
      x: values,
      marker: { color: "#8b949e" },
    },
  ];
  const layout: Partial<Layout> = {
    paper_bgcolor: "#161b22",
    plot_bgcolor: "#161b22",
    font: { color: "#e6edf3", size: 12 },
    margin: { t: 24, r: 24, b: 48, l: 120 },
    xaxis: { title: { text: "Headlines captured" }, gridcolor: "#30363d" },
    yaxis: { automargin: true },
    showlegend: false,
  };
  const config: Partial<Config> = { displayModeBar: false, responsive: true };
  return <Plot data={data} layout={layout} config={config} style={{ width: "100%", height: 400 }} />;
}
