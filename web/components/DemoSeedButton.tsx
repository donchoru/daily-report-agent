"use client";

import { useState } from "react";
import { seedDemo } from "@/lib/api";

export default function DemoSeedButton({ onSeeded }: { onSeeded?: () => void }) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSeed() {
    setLoading(true);
    try {
      await seedDemo();
      setDone(true);
      onSeeded?.();
    } catch (e) {
      alert("시딩 실패: " + (e instanceof Error ? e.message : "알 수 없는 오류"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleSeed}
      disabled={loading || done}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        done
          ? "bg-emerald-500/15 text-emerald-400 cursor-default"
          : loading
            ? "bg-zinc-700 text-zinc-400 cursor-wait"
            : "bg-indigo-500/15 text-indigo-400 hover:bg-indigo-500/25 border border-indigo-500/20"
      }`}
    >
      {done ? "데모 데이터 생성 완료" : loading ? "생성 중..." : "데모 데이터 생성 (7일)"}
    </button>
  );
}
