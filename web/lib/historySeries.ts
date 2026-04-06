import { labelForSource } from "./aggregate";
import type { TimeseriesFile } from "./types";

const LINE_COLORS = [
  "#0071e3",
  "#34c759",
  "#ff9500",
  "#af52de",
  "#ff2d55",
  "#5ac8fa",
  "#ffcc00",
  "#8e8e93",
];

function sourceIds(ts: TimeseriesFile): string[] {
  const s = new Set<string>();
  ts.series.forEach((day) => Object.keys(day.by_source).forEach((k) => s.add(k)));
  return Array.from(s).sort();
}

export function climateCountTraces(ts: TimeseriesFile) {
  const dates = ts.series.map((d) => d.date);
  const ids = sourceIds(ts);
  return ids.map((sid, i) => ({
    type: "scatter" as const,
    mode: "lines+markers" as const,
    name: labelForSource(sid),
    x: dates,
    y: ts.series.map((day) => day.by_source[sid]?.climate ?? 0),
    line: { width: 2, color: LINE_COLORS[i % LINE_COLORS.length], shape: "spline" as const, smoothing: 0.3 },
    marker: { size: 5, color: LINE_COLORS[i % LINE_COLORS.length] },
  }));
}

/** Share of climate-flagged rows in that day's snapshot per outlet (similar to % reportage). */
export function climatePercentTraces(ts: TimeseriesFile) {
  const dates = ts.series.map((d) => d.date);
  const ids = sourceIds(ts);
  return ids.map((sid, i) => ({
    type: "scatter" as const,
    mode: "lines+markers" as const,
    name: labelForSource(sid),
    x: dates,
    y: ts.series.map((day) => {
      const b = day.by_source[sid];
      if (!b || b.items === 0) return null;
      return (100 * b.climate) / b.items;
    }),
    line: { width: 2, color: LINE_COLORS[i % LINE_COLORS.length], shape: "spline" as const, smoothing: 0.3 },
    marker: { size: 5, color: LINE_COLORS[i % LINE_COLORS.length] },
    connectgaps: false,
  }));
}
