"use client";

import Link from "next/link";
import type { HistoryItem } from "@/lib/types";
import { formatDate, maxSeverity } from "@/lib/utils";
import SeverityBadge from "./SeverityBadge";

export default function HistoryList({ items }: { items: HistoryItem[] }) {
  if (items.length === 0) {
    return (
      <div className="glass-card p-8 text-center text-zinc-500">
        분석 이력이 없습니다. 이미지를 업로드하거나 데모 데이터를 생성하세요.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <Link
          key={item.id}
          href={`/analysis/${item.id}`}
          className="glass-card hover-glow-subtle block p-4 cursor-pointer"
        >
          <div className="flex items-center justify-between gap-4">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-zinc-200">
                  {formatDate(item.report_date)}
                </span>
                {item.department && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400">
                    {item.department}
                  </span>
                )}
                {item.report_type && (
                  <span className="text-xs text-zinc-500">{item.report_type}</span>
                )}
              </div>
              <p className="text-sm text-zinc-400 mt-1 line-clamp-1">
                {item.summary || "요약 없음"}
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <span className="text-xs text-zinc-600">
                {item.processing_time_sec.toFixed(1)}s
              </span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
