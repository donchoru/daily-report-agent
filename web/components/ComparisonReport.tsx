import type { ComparisonResult } from "@/lib/types";

export default function ComparisonReport({
  result,
}: {
  result: ComparisonResult;
}) {
  return (
    <div className="space-y-6">
      {/* 개선 */}
      {result.improvements?.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center gap-2">
            <span>📈</span> 개선 항목 ({result.improvements.length})
          </h3>
          <div className="space-y-2">
            {result.improvements.map((item, i) => (
              <div
                key={i}
                className="glass-card p-3 border-l-2 border-l-emerald-500/40"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-zinc-200">
                    {item.metric}
                  </span>
                  <span className="text-xs text-emerald-400">{item.change}</span>
                </div>
                <p className="text-xs text-zinc-400 mt-1">{item.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 악화 */}
      {result.deteriorations?.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
            <span>📉</span> 악화 항목 ({result.deteriorations.length})
          </h3>
          <div className="space-y-2">
            {result.deteriorations.map((item, i) => (
              <div
                key={i}
                className="glass-card p-3 border-l-2 border-l-red-500/40"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-zinc-200">
                    {item.metric}
                  </span>
                  <span className="text-xs text-red-400">{item.change}</span>
                </div>
                <p className="text-xs text-zinc-400 mt-1">{item.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 안정 */}
      {result.stable?.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-zinc-400 mb-3 flex items-center gap-2">
            <span>➡️</span> 안정 항목 ({result.stable.length})
          </h3>
          <div className="space-y-2">
            {result.stable.map((item, i) => (
              <div key={i} className="glass-card p-3">
                <span className="text-sm font-medium text-zinc-200">
                  {item.metric}
                </span>
                <p className="text-xs text-zinc-400 mt-1">{item.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 종합 평가 */}
      {result.overall_assessment && (
        <section>
          <h3 className="text-sm font-semibold text-zinc-300 mb-2">
            종합 평가
          </h3>
          <div className="glass-card-solid p-4">
            <p className="text-sm text-zinc-300 leading-relaxed">
              {result.overall_assessment}
            </p>
          </div>
        </section>
      )}

      {/* 권고사항 */}
      {result.key_recommendations?.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-zinc-300 mb-2">
            핵심 권고사항
          </h3>
          <ul className="space-y-1">
            {result.key_recommendations.map((rec, i) => (
              <li
                key={i}
                className="text-sm text-emerald-300 flex items-start gap-2"
              >
                <span className="text-emerald-500 mt-0.5">→</span>
                {rec}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
