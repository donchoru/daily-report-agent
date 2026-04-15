import type { Insights } from "@/lib/types";
import { trendIcon, trendColor } from "@/lib/utils";
import AnomalyCard from "./AnomalyCard";
import SeverityBadge from "./SeverityBadge";

export default function InsightsPanel({ insights }: { insights: Insights }) {
  return (
    <div className="space-y-6">
      {/* 이상 탐지 */}
      {insights.anomalies.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
            <span>⚠️</span> 이상 탐지 ({insights.anomalies.length}건)
          </h3>
          <div className="space-y-2">
            {insights.anomalies.map((a, i) => (
              <AnomalyCard key={i} anomaly={a} />
            ))}
          </div>
        </section>
      )}

      {/* 트렌드 */}
      {insights.trends.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-zinc-300 mb-3">트렌드</h3>
          <div className="space-y-2">
            {insights.trends.map((t, i) => (
              <div key={i} className="glass-card p-3 flex items-center gap-3">
                <span className={`text-lg ${trendColor(t.direction)}`}>
                  {trendIcon(t.direction)}
                </span>
                <div>
                  <span className="text-sm font-medium text-zinc-200">
                    {t.metric}
                  </span>
                  <p className="text-xs text-zinc-400">{t.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 요약 */}
      {insights.summary && (
        <section>
          <h3 className="text-sm font-semibold text-zinc-300 mb-2">종합 요약</h3>
          <div className="glass-card p-4">
            <p className="text-sm text-zinc-300 leading-relaxed">
              {insights.summary}
            </p>
          </div>
        </section>
      )}

      {/* 액션아이템 */}
      {insights.action_items.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-zinc-300 mb-3">
            액션아이템
          </h3>
          <div className="space-y-2">
            {insights.action_items.map((a, i) => (
              <div key={i} className="glass-card p-3 flex items-start gap-3">
                <SeverityBadge severity={a.priority} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-zinc-200">{a.action}</p>
                  {a.responsible && (
                    <p className="text-xs text-zinc-500 mt-0.5">
                      담당: {a.responsible}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
