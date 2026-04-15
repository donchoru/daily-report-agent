"use client";

const steps = [
  { label: "이미지 전송", icon: "📤" },
  { label: "OCR 추출", icon: "🔍" },
  { label: "데이터 구조화", icon: "📊" },
  { label: "인사이트 분석", icon: "🧠" },
  { label: "헤드라인 생성", icon: "📰" },
];

export default function AnalysisLoading({ step = 0 }: { step?: number }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass-card-solid p-8 max-w-sm w-full text-center space-y-6">
        {/* 스피너 */}
        <div className="relative w-20 h-20 mx-auto">
          <div className="absolute inset-0 rounded-full border-2 border-indigo-500/20" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-indigo-500 animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center text-2xl">
            {steps[Math.min(step, steps.length - 1)]?.icon}
          </div>
        </div>

        {/* 진행 단계 */}
        <div className="space-y-2">
          {steps.map((s, i) => (
            <div
              key={s.label}
              className={`flex items-center gap-2 text-sm transition-colors ${
                i < step
                  ? "text-emerald-400"
                  : i === step
                    ? "text-indigo-300 animate-pulse-glow"
                    : "text-zinc-600"
              }`}
            >
              <span className="w-5 text-center">
                {i < step ? "✓" : i === step ? "●" : "○"}
              </span>
              {s.label}
            </div>
          ))}
        </div>

        <p className="text-xs text-zinc-500">
          Gemini Vision이 일보를 분석하고 있습니다...
        </p>
      </div>
    </div>
  );
}
