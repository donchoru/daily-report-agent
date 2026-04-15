"use client";

import { useEffect, useRef, useState } from "react";
import { sendChat, getChatHistory } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

const SUGGESTIONS = [
  "불량률 원인 분석해줘",
  "개선 액션 우선순위 정리해줘",
  "이 데이터에서 놓친 포인트 있어?",
];

export default function ChatPanel({ analysisId }: { analysisId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [memories, setMemories] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getChatHistory(analysisId)
      .then((res) => setMessages(res.messages))
      .catch(() => {});
  }, [analysisId]);

  useEffect(() => {
    if (expanded) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, expanded]);

  async function send(msg: string) {
    if (!msg.trim() || sending) return;
    const userMsg: ChatMessage = { role: "user", content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);
    setExpanded(true);

    try {
      const res = await sendChat(analysisId, msg);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.response },
      ]);
      if (res.memories_extracted?.length > 0) {
        setMemories((prev) => [
          ...prev,
          ...res.memories_extracted.map((m) => m.content),
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "응답 실패. 백엔드 연결을 확인하세요." },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="glass-card-solid overflow-hidden">
      {/* 헤더 */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-5 py-3 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-xs">
            💬
          </span>
          <span className="text-sm font-semibold text-zinc-200">
            후속 대화
          </span>
          {messages.length > 0 && (
            <span className="text-xs text-zinc-500">
              ({messages.length}개 메시지)
            </span>
          )}
        </div>
        <span className="text-zinc-500 text-sm">
          {expanded ? "▲" : "▼"}
        </span>
      </button>

      {/* 본문 */}
      <div className={expanded ? "" : "hidden"}>
        {/* 메시지 목록 */}
        {messages.length > 0 && (
          <div className="max-h-80 overflow-y-auto px-5 py-3 space-y-3">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-xl text-sm ${
                    m.role === "user"
                      ? "bg-indigo-600 text-white rounded-br-md"
                      : "bg-white/[0.05] text-zinc-200 rounded-bl-md"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-white/[0.05] px-4 py-2 rounded-xl rounded-bl-md flex gap-1">
                  <span className="w-2 h-2 bg-zinc-400 rounded-full bounce-dot" />
                  <span className="w-2 h-2 bg-zinc-400 rounded-full bounce-dot" />
                  <span className="w-2 h-2 bg-zinc-400 rounded-full bounce-dot" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}

        {/* 메모리 추출 알림 */}
        {memories.length > 0 && (
          <div className="mx-5 mb-2 px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <p className="text-xs text-emerald-400 font-medium mb-1">
              자동 추출된 도메인 지식 ({memories.length}건)
            </p>
            {memories.slice(-3).map((m, i) => (
              <p key={i} className="text-xs text-emerald-300/70 truncate">
                · {m}
              </p>
            ))}
          </div>
        )}

        {/* 추천 질문 */}
        {messages.length === 0 && (
          <div className="px-5 pb-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="text-left px-3 py-2 rounded-lg bg-indigo-500/10 text-indigo-300 text-xs hover:bg-indigo-500/20 transition-colors border border-indigo-500/15"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* 입력 */}
        <div className="px-5 pb-4 pt-2">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              placeholder="분석 결과에 대해 질문하세요..."
              disabled={sending}
              className="glass-input flex-1 px-3 py-2 text-sm text-zinc-200 placeholder:text-zinc-500"
            />
            <button
              onClick={() => send(input)}
              disabled={!input.trim() || sending}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                !input.trim() || sending
                  ? "bg-zinc-700 text-zinc-500"
                  : "bg-indigo-600 hover:bg-indigo-500 text-white"
              }`}
            >
              전송
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
