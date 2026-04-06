export type NewsItem = {
  data_schema_version: number;
  id: string;
  source_id: string;
  published_at: string | null;
  title: string;
  description: string;
  url: string;
  language: string;
  climate_related: boolean;
  matched_keywords: string[];
  topics: string[];
  collected_at: string;
};

export type TimeseriesDay = {
  date: string;
  by_source: Record<string, { items: number; climate: number }>;
  totals: { items: number; climate: number };
};

export type TimeseriesFile = {
  data_schema_version: number;
  updated_at?: string;
  day_count?: number;
  series: TimeseriesDay[];
};

export type ManifestCoverage = {
  update_schedule_cron_utc: string;
  update_schedule_note_en: string;
  snapshot_mode: boolean;
  per_source_item_cap: number;
  max_rows_in_file: number;
  window_note_en: string;
  trends_note_en: string;
};

export type ManifestTimeseries = {
  path: string;
  description_en: string;
  day_count?: number;
};

export type Manifest = {
  generated_at: string;
  keyword_list_version: string;
  data_schema_version: number;
  item_count: number;
  climate_related_count: number;
  per_source_counts: Record<string, number>;
  errors: string[];
  coverage?: ManifestCoverage;
  timeseries?: ManifestTimeseries;
};
