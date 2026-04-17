"use client";

import { useEffect, useState } from "react";
import { getSettings, saveSettings, testSettings } from "@/lib/api";
import { showToast } from "@/components/Toast";

const MODEL_PRESETS = [
  "Qwen/Qwen3-235B-A22B",
  "Qwen/Qwen3-32B",
  "Qwen/Qwen2.5-VL-72B-Instruct",
  "Qwen/Qwen2.5-72B-Instruct",
  "meta-llama/Llama-3.1-70B-Instruct",
  "LGAI-EXAONE/EXAONE-3.5-32B-Instruct",
];

export default function SettingsPage() {
  const [baseUrl, setBaseUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  useEffect(() => {
    getSettings()
      .then((data) => {
        setBaseUrl(data.llm_base_url || "");
        setApiKey(data.llm_api_key || "");
        setModel(data.llm_model || "");
      })
      .catch(() => {
        showToast("설정을 불러올 수 없습니다", "error");
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleSave() {
    setSaving(true);
    try {
      await saveSettings({
        llm_base_url: baseUrl,
        llm_api_key: apiKey,
        llm_model: model,
      });
      showToast("설정이 저장되었습니다", "success");
    } catch (e) {
      showToast(
        "저장 실패: " + (e instanceof Error ? e.message : "오류"),
        "error",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleTest() {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testSettings({
        llm_base_url: baseUrl,
        llm_api_key: apiKey,
        llm_model: model,
      });
      const ok = res.status === "ok" || res.success === true;
      const msg = res.reply || res.message || (ok ? "연결 성공" : "연결 실패");
      setTestResult({ success: ok, message: ok ? `${res.model}: ${msg}` : msg });
      showToast(
        ok ? "연결 성공" : "연결 실패",
        ok ? "success" : "error",
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : "연결 실패";
      setTestResult({ success: false, message: msg });
      showToast("연결 테스트 실패", "error");
    } finally {
      setTesting(false);
    }
  }

  const maskedKey = apiKey
    ? apiKey.slice(0, 4) + "•".repeat(Math.max(0, apiKey.length - 8)) + apiKey.slice(-4)
    : "";

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin w-8 h-8 border-2 border-violet-500/20 border-t-violet-500 rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-2xl mx-auto">
      <section>
        <h1 className="text-2xl font-bold gradient-text">설정</h1>
        <p className="text-sm text-zinc-400 mt-1">
          LLM 연결 정보를 설정합니다. 변경 후 저장 버튼을 눌러주세요.
        </p>
      </section>

      <div className="glass-card p-6 space-y-6">
        {/* LLM Base URL */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">
            LLM Base URL
          </label>
          <input
            type="url"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            placeholder="http://llm-server:8000/v1"
            className="glass-input w-full px-4 py-3 text-sm text-zinc-200 placeholder:text-zinc-500"
          />
          <p className="text-xs text-zinc-500">
            vLLM, Ollama, 또는 OpenAI 호환 API의 Base URL
          </p>
        </div>

        {/* API Key */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">API Key</label>
          <div className="relative">
            <input
              type={showKey ? "text" : "password"}
              value={showKey ? apiKey : maskedKey}
              onChange={(e) => {
                setShowKey(true);
                setApiKey(e.target.value);
              }}
              onFocus={() => setShowKey(true)}
              placeholder="API 키를 입력하세요"
              className="glass-input w-full px-4 py-3 pr-20 text-sm text-zinc-200 placeholder:text-zinc-500 font-mono"
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-zinc-400 hover:text-zinc-200 transition-colors px-2 py-1 rounded-md hover:bg-white/5"
            >
              {showKey ? "숨기기" : "보기"}
            </button>
          </div>
        </div>

        {/* Model */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-zinc-300">모델</label>
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            list="model-presets"
            placeholder="Qwen/Qwen3-235B-A22B"
            className="glass-input w-full px-4 py-3 text-sm text-zinc-200 placeholder:text-zinc-500"
          />
          <datalist id="model-presets">
            {MODEL_PRESETS.map((m) => (
              <option key={m} value={m} />
            ))}
          </datalist>
          <p className="text-xs text-zinc-500">
            직접 입력하거나 프리셋에서 선택하세요
          </p>
          <p className="text-xs text-amber-400/80 mt-1">
            Vision 모델(VL) 사용 시 이미지 직접 분석, 텍스트 모델 사용 시 OCR 자동 전환
          </p>
        </div>

        <div className="divider-glow" />

        {/* 연결 테스트 */}
        <div className="space-y-3">
          <button
            onClick={handleTest}
            disabled={testing}
            className={`w-full py-3 rounded-xl text-sm font-medium transition-all ${
              testing
                ? "bg-zinc-700 text-zinc-400 cursor-wait"
                : "glass-soft hover:bg-white/5 text-zinc-200 border border-violet-500/20 hover:border-violet-500/40"
            }`}
          >
            {testing ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin w-4 h-4 border-2 border-violet-500/20 border-t-violet-500 rounded-full" />
                테스트 중...
              </span>
            ) : (
              "연결 테스트"
            )}
          </button>

          {testResult && (
            <div
              className={`glass-soft p-4 rounded-xl text-sm animate-slide-up ${
                testResult.success
                  ? "border-emerald-500/30 text-emerald-300"
                  : "border-red-500/30 text-red-300"
              }`}
              style={{
                borderColor: testResult.success
                  ? "rgba(16, 185, 129, 0.3)"
                  : "rgba(239, 68, 68, 0.3)",
              }}
            >
              <span className="font-medium">
                {testResult.success ? "✓ 성공" : "✕ 실패"}
              </span>
              <span className="text-zinc-400 ml-2">{testResult.message}</span>
            </div>
          )}
        </div>

        <div className="divider-glow" />

        {/* 저장 */}
        <button
          onClick={handleSave}
          disabled={saving}
          className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${
            saving
              ? "bg-zinc-700 text-zinc-400 cursor-wait"
              : "bg-violet-600 hover:bg-violet-500 text-white shadow-lg shadow-violet-500/20"
          }`}
        >
          {saving ? "저장 중..." : "설정 저장"}
        </button>
      </div>
    </div>
  );
}
