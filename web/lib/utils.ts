import type { Anomaly } from "./types";

export function severityColor(severity: string) {
  switch (severity) {
    case "HIGH":
      return { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30" };
    case "MEDIUM":
      return { bg: "bg-amber-500/15", text: "text-amber-400", border: "border-amber-500/30" };
    case "LOW":
      return { bg: "bg-blue-500/15", text: "text-blue-400", border: "border-blue-500/30" };
    default:
      return { bg: "bg-zinc-500/15", text: "text-zinc-400", border: "border-zinc-500/30" };
  }
}

export function trendIcon(direction: string) {
  switch (direction) {
    case "up":
      return "↑";
    case "down":
      return "↓";
    case "stable":
      return "→";
    default:
      return "·";
  }
}

export function trendColor(direction: string) {
  switch (direction) {
    case "up":
      return "text-emerald-400";
    case "down":
      return "text-red-400";
    case "stable":
      return "text-zinc-400";
    default:
      return "text-zinc-500";
  }
}

export function sentimentColor(sentiment: string) {
  switch (sentiment) {
    case "positive":
      return { bg: "bg-emerald-500/15", text: "text-emerald-400" };
    case "negative":
      return { bg: "bg-red-500/15", text: "text-red-400" };
    default:
      return { bg: "bg-zinc-500/15", text: "text-zinc-400" };
  }
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    const d = new Date(dateStr);
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
  } catch {
    return dateStr;
  }
}

export function formatShortDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "-";
  try {
    const d = new Date(dateStr);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  } catch {
    return dateStr;
  }
}

export function maxSeverity(anomalies: Anomaly[]): string {
  if (anomalies.some((a) => a.severity === "HIGH")) return "HIGH";
  if (anomalies.some((a) => a.severity === "MEDIUM")) return "MEDIUM";
  if (anomalies.length > 0) return "LOW";
  return "NONE";
}

export function numericValue(data: Record<string, unknown>, ...keys: string[]): number | null {
  for (const key of keys) {
    const v = data[key];
    if (typeof v === "number") return v;
    if (typeof v === "string") {
      const n = parseFloat(v.replace(/[^0-9.-]/g, ""));
      if (!isNaN(n)) return n;
    }
  }
  return null;
}

export function categoryLabel(key: string): string {
  const map: Record<string, string> = {
    production: "생산",
    quality: "품질",
    equipment: "설비",
    workforce: "인력",
    other: "기타",
    metadata: "메타",
  };
  return map[key] || key;
}

export function categoryIcon(key: string): string {
  const map: Record<string, string> = {
    production: "📦",
    quality: "🔍",
    equipment: "⚙️",
    workforce: "👷",
    other: "📋",
    metadata: "📊",
  };
  return map[key] || "📄";
}
