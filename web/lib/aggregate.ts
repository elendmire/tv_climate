import type { NewsItem } from "./types";

const SOURCE_LABELS: Record<string, string> = {
  trt_haber: "TRT Haber",
  ntv: "NTV",
  haberturk: "Habertürk",
  anadolu_agency: "Anadolu Agency",
  yenisafak: "Yeni Şafak",
  milliyet: "Milliyet",
  ahaber: "A Haber",
  cnnturk: "CNN Türk",
};

export function labelForSource(id: string): string {
  return SOURCE_LABELS[id] ?? id;
}

function dayKey(iso: string | null): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString().slice(0, 10);
}

export function climateCountBySource(items: NewsItem[]): { labels: string[]; values: number[] } {
  const map = new Map<string, number>();
  for (const it of items) {
    if (!it.climate_related) continue;
    map.set(it.source_id, (map.get(it.source_id) ?? 0) + 1);
  }
  const entries = [...map.entries()].sort((a, b) => b[1] - a[1]);
  return {
    labels: entries.map(([k]) => labelForSource(k)),
    values: entries.map(([, v]) => v),
  };
}

export function climateCountByDay(items: NewsItem[]): { dates: string[]; counts: number[] } {
  const map = new Map<string, number>();
  for (const it of items) {
    if (!it.climate_related) continue;
    const k = dayKey(it.published_at) ?? dayKey(it.collected_at);
    if (!k) continue;
    map.set(k, (map.get(k) ?? 0) + 1);
  }
  const dates = [...map.keys()].sort();
  return {
    dates,
    counts: dates.map((d) => map.get(d) ?? 0),
  };
}

export function totalBySource(items: NewsItem[]): { labels: string[]; values: number[] } {
  const map = new Map<string, number>();
  for (const it of items) {
    map.set(it.source_id, (map.get(it.source_id) ?? 0) + 1);
  }
  const entries = [...map.entries()].sort((a, b) => b[1] - a[1]);
  return {
    labels: entries.map(([k]) => labelForSource(k)),
    values: entries.map(([, v]) => v),
  };
}
