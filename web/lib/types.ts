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

export type Manifest = {
  generated_at: string;
  keyword_list_version: string;
  data_schema_version: number;
  item_count: number;
  climate_related_count: number;
  per_source_counts: Record<string, number>;
  errors: string[];
};
