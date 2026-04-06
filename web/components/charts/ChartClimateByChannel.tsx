"use client";

import dynamic from "next/dynamic";
import type { NewsItem } from "@/lib/types";
import { climateCountBySource } from "@/lib/aggregate";
import { plotBg, plotFont, plotGrid } from "@/lib/plotTheme";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading…</p>,
});

export function ChartClimateByChannel({ items }: { items: NewsItem[] }) {
  const { labels, values } = climateCountBySource(items);
  const data: Data[] = [
    {
      type: "bar",
      x: labels,
      y: values,
      marker: { color: "#34c759" },
    },
  ];
  const layout: Partial<Layout> = {
    paper_bgcolor: plotBg,
    plot_bgcolor: plotBg,
    font: plotFont,
    margin: { t: 28, r: 12, b: 112, l: 44 },
    xaxis: {
      tickangle: -35,
      title: { text: "Outlet", font: plotFont },
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
  const config: Partial<Config> = {
    displayModeBar: false,
    responsive: true,
  };
  if (labels.length === 0) {
    return <p className="muted">No matches in this file.</p>;
  }
  return <Plot data={data} layout={layout} config={config} style={{ width: "100%", height: 380 }} />;
}
