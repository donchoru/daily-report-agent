// ── 백엔드 모델 미러 ─────────────────────────────────────────

export interface ExtractedData {
  production: Record<string, unknown>;
  quality: Record<string, unknown>;
  equipment: Record<string, unknown>;
  workforce: Record<string, unknown>;
  other: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface Anomaly {
  metric: string;
  value: string;
  expected: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  description: string;
}

export interface Trend {
  metric: string;
  direction: "up" | "down" | "stable";
  description: string;
}

export interface ActionItem {
  priority: "HIGH" | "MEDIUM" | "LOW";
  action: string;
  responsible: string;
}

export interface Insights {
  anomalies: Anomaly[];
  trends: Trend[];
  summary: string;
  action_items: ActionItem[];
}

export interface Headlines {
  main_headline: string;
  sub_headlines: string[];
  sentiment: "positive" | "negative" | "neutral";
  key_metric: string;
}

export interface DrilldownLink {
  category: string;
  name: string;
  url: string;
  description: string;
  reason: string;
}

// ── API 응답 ─────────────────────────────────────────────────

export interface AnalysisResponse {
  id: string;
  report_date: string | null;
  report_type: string | null;
  department: string | null;
  extracted_data: ExtractedData;
  insights: Insights;
  headlines: Headlines;
  drilldown_links: DrilldownLink[];
  processing_time_sec: number;
}

export interface AnalysisDetail {
  id: string;
  report_date: string | null;
  report_type: string | null;
  department: string | null;
  extracted_data: ExtractedData;
  insights: Insights;
  processing_time_sec: number;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  report_date: string | null;
  report_type: string | null;
  department: string | null;
  summary: string;
  processing_time_sec: number;
  created_at: string;
}

export interface TimelineItem {
  id: string;
  report_date: string;
  department: string | null;
  extracted_data: ExtractedData;
  insights: Insights;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  created_at?: string;
}

export interface ChatResponse {
  response: string;
  memories_extracted: { id: number; category: string; content: string }[];
}

export interface PerspectivePreset {
  key: string;
  description: string;
}

export interface ReanalysisResult {
  perspective: string;
  summary: string;
  charts: { title: string; type: string; data: Record<string, unknown>[] }[];
  insights: string[];
  recommendations: string[];
}

export interface ComparisonResult {
  improvements: { metric: string; change: string; description: string }[];
  deteriorations: { metric: string; change: string; description: string }[];
  stable: { metric: string; description: string }[];
  overall_assessment: string;
  key_recommendations: string[];
}

export interface CompareAnalysis {
  id: string;
  report_date: string | null;
  department: string | null;
  summary: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  db_stats: Record<string, number>;
}
