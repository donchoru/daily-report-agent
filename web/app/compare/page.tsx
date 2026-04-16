"use client";

import { useCallback, useEffect, useState } from "react";
import { compareAnalyses, getHistory } from "@/lib/api";
import { showToast } from "@/components/Toast";
import type { HistoryItem, ComparisonResult } from "@/lib/types";
import CompareForm from "@/components/CompareForm";
import ComparisonReport from "@/components/ComparisonReport";

export default function ComparePage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    getHistory({ limit: 50 })
      .then((res) => setItems(res.items))
      .catch(() => {});
  }, []);

  async function handleCompare(ids: string[]) {
    setLoading(true);
    setResult(null);
    try {
      const res = await compareAnalyses({ analysis_ids: ids });
      setResult(res.comparison);
      setElapsed(res.processing_time_sec);
    } catch (e) {
      showToast("비교 분석 실패: " + (e instanceof Error ? e.message : "오류"), "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold gradient-text">비교 분석</h1>
      <p className="text-sm text-zinc-400">
        여러 일보 분석 결과를 비교하여 개선/악화 추이를 파악합니다.
      </p>

      <CompareForm items={items} onCompare={handleCompare} loading={loading} />

      {loading && (
        <div className="glass-card p-8 text-center">
          <div className="animate-spin w-8 h-8 mx-auto border-2 border-indigo-500/20 border-t-indigo-500 rounded-full" />
          <p className="text-sm text-zinc-400 mt-3">AI가 비교 분석 중...</p>
        </div>
      )}

      {result && !loading && (
        <>
          <div className="divider-glow" />
          <ComparisonReport result={result} />
          <p className="text-xs text-zinc-600 text-right">
            처리 시간: {elapsed.toFixed(1)}s
          </p>
        </>
      )}
    </div>
  );
}
