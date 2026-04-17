const BASE = "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

// ── 분석 ─────────────────────────────────────────────────────

export async function analyzeImage(formData: FormData) {
  const res = await fetch(`${BASE}/analyze`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

// ── 히스토리 ─────────────────────────────────────────────────

export function getHistory(params?: { department?: string; limit?: number }) {
  const q = new URLSearchParams();
  if (params?.department) q.set("department", params.department);
  if (params?.limit) q.set("limit", String(params.limit));
  return request<{ items: import("./types").HistoryItem[]; count: number }>(
    `/history?${q}`,
  );
}

export function getAnalysisDetail(id: string) {
  return request<import("./types").AnalysisDetail>(`/history/${id}`);
}

// ── 헤드라인 ─────────────────────────────────────────────────

export function getHeadlines(id: string) {
  return request<{
    analysis_id: string;
    headlines: import("./types").Headlines;
  }>(`/headlines/${id}`);
}

// ── 타임라인 ─────────────────────────────────────────────────

export function getTimeline(params?: { department?: string; days?: number }) {
  const q = new URLSearchParams();
  if (params?.department) q.set("department", params.department);
  if (params?.days) q.set("days", String(params.days));
  return request<{
    items: import("./types").TimelineItem[];
    count: number;
    days: number;
  }>(`/timeline?${q}`);
}

// ── 채팅 ─────────────────────────────────────────────────────

export function sendChat(analysisId: string, message: string) {
  return request<import("./types").ChatResponse>(`/chat/${analysisId}`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export function getChatHistory(analysisId: string) {
  return request<{
    analysis_id: string;
    messages: import("./types").ChatMessage[];
  }>(`/chat/${analysisId}/history`);
}

// ── 재분석 ───────────────────────────────────────────────────

export function getPerspectives() {
  return request<{
    presets: import("./types").PerspectivePreset[];
    custom: string;
  }>("/reanalyze/perspectives");
}

export function reanalyze(analysisId: string, perspective: string) {
  return request<{
    analysis_id: string;
    perspective: string;
    result: import("./types").ReanalysisResult;
    drilldown_links: import("./types").DrilldownLink[];
    processing_time_sec: number;
  }>(`/reanalyze/${analysisId}`, {
    method: "POST",
    body: JSON.stringify({ perspective }),
  });
}

// ── 드릴다운 ─────────────────────────────────────────────────

export function getDrilldownLinks(analysisId: string) {
  return request<{
    analysis_id: string;
    drilldown_links: import("./types").DrilldownLink[];
  }>(`/drilldown/${analysisId}`);
}

// ── 비교 ─────────────────────────────────────────────────────

export function compareAnalyses(body: {
  analysis_ids?: string[];
  date_from?: string;
  date_to?: string;
  department?: string;
}) {
  return request<{
    analyses: import("./types").CompareAnalysis[];
    comparison: import("./types").ComparisonResult;
    processing_time_sec: number;
  }>("/compare", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ── 메트릭 ───────────────────────────────────────────────────

export function getMetrics(params?: {
  department?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
}) {
  const q = new URLSearchParams();
  if (params?.department) q.set("department", params.department);
  if (params?.date_from) q.set("date_from", params.date_from);
  if (params?.date_to) q.set("date_to", params.date_to);
  if (params?.limit) q.set("limit", String(params.limit));
  return request<{ items: Record<string, unknown>[]; count: number }>(
    `/metrics?${q}`,
  );
}

export function getMetricsSummary(params?: {
  department?: string;
  days?: number;
}) {
  const q = new URLSearchParams();
  if (params?.department) q.set("department", params.department);
  if (params?.days) q.set("days", String(params.days));
  return request<{ summary: Record<string, number | null>; days: number }>(
    `/metrics/summary?${q}`,
  );
}

export function getMetricsTrend(params?: {
  metric?: string;
  department?: string;
  days?: number;
}) {
  const q = new URLSearchParams();
  if (params?.metric) q.set("metric", params.metric);
  if (params?.department) q.set("department", params.department);
  if (params?.days) q.set("days", String(params.days));
  return request<{
    metric: string;
    data: { report_date: string; department: string; value: number | null }[];
    count: number;
  }>(`/metrics/trend?${q}`);
}

export function backfillMetrics() {
  return request<{
    message: string;
    migrated: number;
    errors: number;
    source_rows: number;
  }>("/metrics/backfill", { method: "POST" });
}

// ── 헬스 ─────────────────────────────────────────────────────

export function getHealth() {
  return request<import("./types").HealthResponse>("/health");
}

// ── 시드 ─────────────────────────────────────────────────────

export function seedDemo() {
  return request<{ message: string; ids: string[] }>("/seed-demo", {
    method: "POST",
  });
}

// ── 설정 ─────────────────────────────────────────────────────

export interface SettingsData {
  llm_base_url: string;
  llm_api_key: string;
  llm_model: string;
}

export function getSettings() {
  return request<SettingsData>("/settings");
}

export function saveSettings(data: SettingsData) {
  return request<{ message: string }>("/settings", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function testSettings(data?: Partial<SettingsData>) {
  return request<{ status?: string; success?: boolean; message?: string; model?: string; reply?: string }>("/settings/test", {
    method: "POST",
    body: JSON.stringify(data ?? {}),
  });
}
