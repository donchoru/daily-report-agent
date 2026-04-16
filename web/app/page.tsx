"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { analyzeImage, getHistory, getHealth } from "@/lib/api";
import { showToast } from "@/components/Toast";
import type { HistoryItem } from "@/lib/types";
import ImageUploader from "@/components/ImageUploader";
import AnalysisLoading from "@/components/AnalysisLoading";
import StatsCards from "@/components/StatsCards";
import HistoryList from "@/components/HistoryList";
import DemoSeedButton from "@/components/DemoSeedButton";

export default function DashboardPage() {
  const router = useRouter();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [stats, setStats] = useState({ total: 0, today: 0, anomalies: 0 });
  const [uploading, setUploading] = useState(false);
  const [step, setStep] = useState(0);

  const loadData = useCallback(async () => {
    try {
      const [histRes, healthRes] = await Promise.all([
        getHistory({ limit: 20 }),
        getHealth(),
      ]);
      setItems(histRes.items);

      const todayStr = new Date().toISOString().slice(0, 10);
      const todayCount = histRes.items.filter(
        (i) => i.report_date === todayStr || i.created_at?.startsWith(todayStr),
      ).length;
      setStats({
        total: healthRes.db_stats?.analyses || histRes.count,
        today: todayCount,
        anomalies: healthRes.db_stats?.anomalies || 0,
      });
    } catch {
      // 백엔드 미실행 시 무시
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleUpload(formData: FormData) {
    setUploading(true);
    setStep(0);

    const interval = setInterval(() => {
      setStep((s) => Math.min(s + 1, 4));
    }, 2000);

    try {
      const result = await analyzeImage(formData);
      clearInterval(interval);
      router.push(`/analysis?id=${result.id}`);
    } catch (e) {
      clearInterval(interval);
      setUploading(false);
      showToast("분석 실패: " + (e instanceof Error ? e.message : "오류"), "error");
    }
  }

  return (
    <div className="space-y-8">
      {uploading && <AnalysisLoading step={step} />}

      {/* 히어로 */}
      <section className="hero-bg rounded-2xl p-8 text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-bold gradient-text">
          제조 일보 AI 분석
        </h1>
        <p className="text-zinc-400 max-w-lg mx-auto">
          일보 이미지를 업로드하면 Gemini Vision이 데이터를 추출하고
          이상탐지, 트렌드, 액션아이템을 자동으로 분석합니다.
        </p>
      </section>

      {/* 업로드 */}
      <ImageUploader onUpload={handleUpload} loading={uploading} />

      {/* 통계 */}
      <StatsCards
        stats={[
          { label: "총 분석", value: stats.total, color: "text-indigo-300" },
          { label: "오늘 분석", value: stats.today, color: "text-emerald-300" },
          {
            label: "이상 감지",
            value: stats.anomalies,
            color: stats.anomalies > 0 ? "text-red-400" : "text-zinc-300",
          },
        ]}
      />

      {/* 히스토리 */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-zinc-200">최근 분석</h2>
          <DemoSeedButton onSeeded={loadData} />
        </div>
        <HistoryList items={items} />
      </section>
    </div>
  );
}
