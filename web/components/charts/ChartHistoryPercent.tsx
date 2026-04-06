"use client";

import dynamic from "next/dynamic";
import { climatePercentTraces } from "@/lib/historySeries";
import { plotBg, plotFont, plotGrid } from "@/lib/plotTheme";
import type { TimeseriesFile } from "@/lib/types";
import type { Config, Data, Layout } from "plotly.js";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p className="muted">Loading…</p>,
});

type Props = { ts: TimeseriesFile };

export function ChartHistoryPercent({ ts }: Props) {
  const traces = climatePercentTraces(ts) as Data[];
  const layout: Partial<Layout> = {
    paper_bgcolor: plotBg,
    plot_bgcolor: plotBg,
    font: plotFont,
    margin: { t: 28, r: 12, b: 56, l: 52 },
    xaxis: {
      title: { text: "Day (UTC)", font: plotFont },
      gridcolor: plotGrid,
      linecolor: plotGrid,
      tickfont: plotFont,
    },
    yaxis: {
      title: { text: "% of rows climate-flagged", font: plotFont },
      gridcolor: plotGrid,
      linecolor: plotGrid,
      tickfont: plotFont,
      rangemode: "tozero",
      ticksuffix: "%",
    },
    legend: {
      orientation: "v",
      yanchor: "top",
      y: 1,
      xanchor: "left",
      x: 1.02,
      font: plotFont,
    },
    showlegend: true,
  };
  const config: Partial<Config> = { displayModeBar: true, responsive: true, displaylogo: false };
  return <Plot data={traces} layout={layout} config={config} style={{ width: "100%", height: 420 }} />;
}
