"use client";

import { useState } from "react";
import { reanalyze } from "@/lib/api";
import { showToast } from "@/components/Toast";
import type { ReanalysisResult } from "@/lib/types";
import ReanalysisResultView from "./ReanalysisResult";

const PRESETS = [
  { key: "cost", label: "원가", icon: "💰" },
  { key: "bottleneck", label: "병목", icon: "🔗" },
  { key: "trend", label: "추세", icon: "📈" },
  { key: "risk", label: "리스크", icon: "⚠️" },
  { key: "efficiency", label: "효율", icon: "⚡" },
  { key: "comparison", label: "비교", icon: "📊" },
];

export default function PerspectiveReanalyzer({
  analysisId,
}: {
  analysisId: string;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const [custom, setCustom] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReanalysisResult | null>(null);

  async function handleReanalyze(perspective: string) {
    setSelected(perspective);
    setLoading(true);
    setResult(null);
    try {
      const res = await reanalyze(analysisId, perspective);
      setResult(res.result);
    } catch {
      showToast("재분석 실패", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-zinc-300">관점 전환 재분석</h3>

      {/* 프리셋 버튼 */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.key}
            onClick={() => handleReanalyze(p.key)}
            disabled={loading}
            className={`glass-card p-3 text-center hover-glow-subtle transition-all ${
              selected === p.key
                ? "border-indigo-500/40 bg-indigo-500/10"
                : ""
            } ${loading ? "opacity-50 cursor-wait" : ""}`}
          >
            <div className="text-xl">{p.icon}</div>
            <div className="text-xs text-zinc-300 mt-1">{p.label}</div>
          </button>
        ))}
      </div>

      {/* 커스텀 입력 */}
      <div className="flex gap-2">
        <input
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          placeholder="직접 관점 입력 (예: 에너지 비용 관점에서)"
          className="glass-input flex-1 px-3 py-2 text-sm text-zinc-200 placeholder:text-zinc-500"
        />
        <button
          onClick={() => {
            if (custom.trim()) handleReanalyze(custom.trim());
          }}
          disabled={!custom.trim() || loading}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
            !custom.trim() || loading
              ? "bg-zinc-700 text-zinc-500"
              : "bg-indigo-600 hover:bg-indigo-500 text-white"
          }`}
        >
          분석
        </button>
      </div>

      {/* 로딩 */}
      {loading && (
        <div className="glass-card p-6 text-center">
          <div className="animate-spin w-8 h-8 mx-auto border-2 border-indigo-500/20 border-t-indigo-500 rounded-full" />
          <p className="text-sm text-zinc-400 mt-3">
            {selected} 관점으로 재분석 중...
          </p>
        </div>
      )}

      {/* 결과 */}
      {result && !loading && <ReanalysisResultView result={result} />}
    </div>
  );
}
