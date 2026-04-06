"use client";

import dynamic from "next/dynamic";
import type { NewsItem } from "@/lib/types";
import { climateCountByDay } from "@/lib/aggregate";
import { plotBg, plotFont, plotGrid } from "@/lib/plotTheme";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading…</p>,
});

export function ChartClimateTimeline({ items }: { items: NewsItem[] }) {
  const { dates, counts } = climateCountByDay(items);
  const data: Data[] = [
    {
      type: "scatter",
      mode: "lines+markers",
      x: dates,
      y: counts,
      line: { color: "#0071e3", shape: "spline", smoothing: 0.35, width: 2 },
      marker: { size: 7, color: "#0071e3" },
    },
  ];
  const layout: Partial<Layout> = {
    paper_bgcolor: plotBg,
    plot_bgcolor: plotBg,
    font: plotFont,
    margin: { t: 20, r: 12, b: 56, l: 44 },
    xaxis: {
      title: { text: "Date", font: plotFont },
      gridcolor: plotGrid,
      linecolor: plotGrid,
      tickfont: plotFont,
    },
    yaxis: {
      title: { text: "Count", font: plotFont },
      gridcolor: plotGrid,
      linecolor: plotGrid,
      tickfont: plotFont,
      rangemode: "tozero",
    },
    showlegend: false,
  };
  const config: Partial<Config> = { displayModeBar: false, responsive: true };
  if (dates.length === 0) {
    return <p className="muted">Nothing dated to plot.</p>;
  }
  return <Plot data={data} layout={layout} config={config} style={{ width: "100%", height: 360 }} />;
}
