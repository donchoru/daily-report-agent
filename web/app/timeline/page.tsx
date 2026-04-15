"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTimeline } from "@/lib/api";
import type { TimelineItem } from "@/lib/types";
import { formatDate, maxSeverity } from "@/lib/utils";
import TimelineChart from "@/components/TimelineChart";
import SeverityBadge from "@/components/SeverityBadge";

const PERIOD_OPTIONS = [
  { label: "7일", days: 7 },
  { label: "14일", days: 14 },
  { label: "30일", days: 30 },
];

export default function TimelinePage() {
  const router = useRouter();
  const [items, setItems] = useState<TimelineItem[]>([]);
  const [days, setDays] = useState(7);
  const [department, setDepartment] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getTimeline({
        days,
        department: department || undefined,
      });
      setItems(res.items);
    } catch {
      // 백엔드 미실행
    } finally {
      setLoading(false);
    }
  }, [days, department]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold gradient-text">타임라인</h1>

      {/* 필터 */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex gap-1">
          {PERIOD_OPTIONS.map((p) => (
            <button
              key={p.days}
              onClick={() => setDays(p.days)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                days === p.days
                  ? "bg-indigo-500/15 text-indigo-300"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="부서/라인 필터"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="glass-input px-3 py-1.5 text-sm text-zinc-200 placeholder:text-zinc-500 w-40"
        />
      </div>

      {/* 차트 */}
      {loading ? (
        <div className="glass-card h-80 animate-pulse bg-white/[0.03]" />
      ) : items.length > 0 ? (
        <TimelineChart
          items={items}
          onDateClick={(id) => router.push(`/analysis?id=${id}`)}
        />
      ) : (
        <div className="glass-card p-8 text-center text-zinc-500">
          해당 기간에 데이터가 없습니다.
        </div>
      )}

      {/* 일별 카드 리스트 */}
      {items.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold text-zinc-400">일별 요약</h2>
          {items.map((item) => {
            const sev = maxSeverity(item.insights.anomalies || []);
            return (
              <button
                key={item.id}
                onClick={() => router.push(`/analysis/${item.id}`)}
                className="glass-card hover-glow-subtle w-full text-left p-4 flex items-center justify-between gap-4"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-zinc-200">
                      {formatDate(item.report_date)}
                    </span>
                    {item.department && (
                      <span className="text-xs text-indigo-400">
                        {item.department}
                      </span>
                    )}
                    {sev !== "NONE" && <SeverityBadge severity={sev} />}
                  </div>
                  <p className="text-sm text-zinc-400 mt-1 line-clamp-1">
                    {item.insights.summary || "요약 없음"}
                  </p>
                </div>
                <span className="text-zinc-600 text-sm shrink-0">→</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
