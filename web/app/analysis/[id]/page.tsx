"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getAnalysisDetail, getHeadlines, getDrilldownLinks } from "@/lib/api";
import type { AnalysisDetail, Headlines, DrilldownLink } from "@/lib/types";
import HeadlineBanner from "@/components/HeadlineBanner";
import ExtractedDataGrid from "@/components/ExtractedDataGrid";
import InsightsPanel from "@/components/InsightsPanel";
import DrilldownLinks from "@/components/DrilldownLinks";
import ChatPanel from "@/components/ChatPanel";
import PerspectiveReanalyzer from "@/components/PerspectiveReanalyzer";

export default function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [headlines, setHeadlines] = useState<Headlines | null>(null);
  const [drilldown, setDrilldown] = useState<DrilldownLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      getAnalysisDetail(id),
      getHeadlines(id).catch(() => null),
      getDrilldownLinks(id).catch(() => null),
    ])
      .then(([detail, hdl, ddl]) => {
        setData(detail);
        if (hdl) setHeadlines(hdl.headlines);
        if (ddl) setDrilldown(ddl.drilldown_links);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="glass-card h-32 animate-pulse bg-white/[0.03]"
          />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="text-red-400">{error || "분석 결과를 찾을 수 없습니다."}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤드라인 */}
      <HeadlineBanner
        headlines={headlines}
        department={data.department}
        reportDate={data.report_date}
      />

      {/* 추출 데이터 */}
      <section>
        <h2 className="text-sm font-semibold text-zinc-300 mb-3">
          추출 데이터
        </h2>
        <ExtractedDataGrid data={data.extracted_data} />
      </section>

      <div className="divider-glow" />

      {/* 인사이트 */}
      <InsightsPanel insights={data.insights} />

      <div className="divider-glow" />

      {/* 드릴다운 */}
      <DrilldownLinks links={drilldown} />

      <div className="divider-glow" />

      {/* 관점 전환 재분석 */}
      <PerspectiveReanalyzer analysisId={id} />

      <div className="divider-glow" />

      {/* 후속 대화 */}
      <ChatPanel analysisId={id} />

      {/* 메타 */}
      <div className="text-xs text-zinc-600 text-right">
        분석 ID: {data.id} · 처리 시간: {data.processing_time_sec.toFixed(1)}s ·{" "}
        {data.created_at}
      </div>
    </div>
  );
}
