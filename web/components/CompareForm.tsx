"use client";

import { useState } from "react";
import type { HistoryItem } from "@/lib/types";
import { formatDate } from "@/lib/utils";

interface Props {
  items: HistoryItem[];
  onCompare: (ids: string[]) => void;
  loading?: boolean;
}

export default function CompareForm({ items, onCompare, loading }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < 5) {
        next.add(id);
      }
      return next;
    });
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-zinc-400">
          비교할 분석을 2~5개 선택하세요 ({selected.size}개 선택됨)
        </p>
        <button
          onClick={() => onCompare(Array.from(selected))}
          disabled={selected.size < 2 || loading}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
            selected.size < 2 || loading
              ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
              : "bg-indigo-600 hover:bg-indigo-500 text-white"
          }`}
        >
          {loading ? "비교 분석 중..." : "비교 분석"}
        </button>
      </div>

      <div className="space-y-1">
        {items.map((item) => {
          const isSelected = selected.has(item.id);
          return (
            <button
              key={item.id}
              onClick={() => toggle(item.id)}
              className={`w-full text-left glass-card p-3 flex items-center gap-3 transition-all ${
                isSelected
                  ? "border-indigo-500/40 bg-indigo-500/10"
                  : "hover:bg-white/[0.02]"
              }`}
            >
              <span
                className={`w-5 h-5 rounded border flex items-center justify-center text-xs transition-colors ${
                  isSelected
                    ? "bg-indigo-600 border-indigo-600 text-white"
                    : "border-zinc-600"
                }`}
              >
                {isSelected && "✓"}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-zinc-200">
                    {formatDate(item.report_date)}
                  </span>
                  {item.department && (
                    <span className="text-xs text-indigo-400">
                      {item.department}
                    </span>
                  )}
                </div>
                <p className="text-xs text-zinc-500 line-clamp-1">
                  {item.summary || "요약 없음"}
                </p>
              </div>
              <span className="text-xs text-zinc-600">{item.id}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
