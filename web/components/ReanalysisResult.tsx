"use client";

import type { ReanalysisResult } from "@/lib/types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function ReanalysisResultView({
  result,
}: {
  result: ReanalysisResult;
}) {
  return (
    <div className="glass-card-solid p-5 space-y-5">
      <div className="flex items-center gap-2">
        <span className="text-xs px-2 py-0.5 rounded-full bg-violet-500/15 text-violet-400">
          {result.perspective}
        </span>
        <h4 className="text-sm font-semibold text-zinc-200">재분석 결과</h4>
      </div>

      {/* 요약 */}
      {result.summary && (
        <p className="text-sm text-zinc-300 leading-relaxed">{result.summary}</p>
      )}

      {/* 차트 */}
      {result.charts?.length > 0 &&
        result.charts.map((chart, ci) => (
          <div key={ci} className="space-y-2">
            <p className="text-xs text-zinc-400">{chart.title}</p>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chart.data}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.05)"
                  />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#71717a", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "#71717a", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#18181b",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: 12,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}

      {/* 인사이트 */}
      {result.insights?.length > 0 && (
        <div>
          <p className="text-xs text-zinc-400 mb-2">인사이트</p>
          <ul className="space-y-1">
            {result.insights.map((insight, i) => (
              <li
                key={i}
                className="text-sm text-zinc-300 flex items-start gap-2"
              >
                <span className="text-indigo-400 mt-0.5">·</span>
                {insight}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 권고 */}
      {result.recommendations?.length > 0 && (
        <div>
          <p className="text-xs text-zinc-400 mb-2">권고사항</p>
          <ul className="space-y-1">
            {result.recommendations.map((rec, i) => (
              <li
                key={i}
                className="text-sm text-emerald-300 flex items-start gap-2"
              >
                <span className="text-emerald-500 mt-0.5">→</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
