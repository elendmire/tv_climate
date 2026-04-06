"use client";

import dynamic from "next/dynamic";
import type { NewsItem } from "@/lib/types";
import { totalBySource } from "@/lib/aggregate";
import { plotBg, plotFont, plotGrid } from "@/lib/plotTheme";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading…</p>,
});

export function ChartTotalByChannel({ items }: { items: NewsItem[] }) {
  const { labels, values } = totalBySource(items);
  const data: Data[] = [
    {
      type: "bar",
      orientation: "h",
      y: labels,
      x: values,
      marker: { color: "#aeaeb2" },
    },
  ];
  const layout: Partial<Layout> = {
    paper_bgcolor: plotBg,
    plot_bgcolor: plotBg,
    font: plotFont,
    margin: { t: 20, r: 20, b: 44, l: 112 },
    xaxis: {
      title: { text: "Headlines", font: plotFont },
      gridcolor: plotGrid,
      linecolor: plotGrid,
      tickfont: plotFont,
      rangemode: "tozero",
    },
    yaxis: {
      automargin: true,
      gridcolor: plotGrid,
      tickfont: plotFont,
    },
    showlegend: false,
  };
  const config: Partial<Config> = { displayModeBar: false, responsive: true };
  return <Plot data={data} layout={layout} config={config} style={{ width: "100%", height: 400 }} />;
}
