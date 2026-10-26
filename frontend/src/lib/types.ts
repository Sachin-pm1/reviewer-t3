// ---------------------------------------------------------------------------
// API response types — mirrors the Pydantic schemas in the FastAPI backend.
// ---------------------------------------------------------------------------

export interface Timestamped {
  id: string;
  created_at: string;
  updated_at: string;
}

// --- Projects & Sources ---

export interface ProjectRead extends Timestamped {
  name: string;
  product_name: string;
  description: string | null;
}

export interface ProductRead extends Timestamped {
  name: string;
}

export interface SourceRead extends Timestamped {
  project_id: string;
  source_type: string;
  config: Record<string, unknown>;
  status: string;
  review_count: number;
  last_collected_at: string | null;
}

export interface ProjectDetail extends ProjectRead {
  products: ProductRead[];
  sources: SourceRead[];
}

// --- Jobs ---

export type JobStatus = "pending" | "running" | "completed" | "failed";

export interface JobRead extends Timestamped {
  project_id: string;
  type: string;
  status: JobStatus;
  stage: string;
  processed: number;
  total: number;
  progress: number;
  error: string | null;
  result: Record<string, unknown>;
}

// --- Reviews ---

export interface ReviewRead extends Timestamped {
  project_id: string;
  source_type: string;
  external_id: string | null;
  author: string | null;
  rating: number | null;
  text: string;
  analyzed: boolean;
}

// --- Insights ---

export type Sentiment = "positive" | "neutral" | "negative" | "mixed";

export interface CountedItem {
  label: string;
  count: number;
  examples: string[];
}

export interface PainPointSummary extends CountedItem {
  severity_mix: Record<string, number>;
}

export interface PersonaSummary extends CountedItem {
  top_pain_points: string[];
}

export interface OpportunitySummary extends CountedItem {
  impact_mix: Record<string, number>;
}

export interface InsightsOverview {
  project_id: string;
  total_reviews: number;
  analyzed_reviews: number;
  sentiment_distribution: Record<string, number>;
  top_topics: CountedItem[];
  pain_points: PainPointSummary[];
  personas: PersonaSummary[];
  opportunities: OpportunitySummary[];
}

// --- Chat ---

export interface ChatSource {
  index: number;
  text: string;
  score: number;
  review_id: string;
  source_type: string;
  rating: number | null;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: ChatSource[];
}

export interface ChatHistoryItem {
  id: string;
  created_at: string;
  updated_at: string;
  question: string;
  answer: string;
  sources: ChatSource[];
}

// --- Reports ---

export interface ReportSummary extends Timestamped {
  project_id: string;
  report_type: string;
  title: string;
  model: string;
}

export interface ReportRead extends ReportSummary {
  content_markdown: string;
  data: Record<string, unknown>;
}

// --- Error envelope ---

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}
