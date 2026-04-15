"use client";

import { useCallback, useRef, useState } from "react";

interface Props {
  onUpload: (formData: FormData) => void;
  loading?: boolean;
}

export default function ImageUploader({ onUpload, loading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [department, setDepartment] = useState("");
  const [reportDate, setReportDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [context, setContext] = useState("");

  const handleFile = useCallback((f: File) => {
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      if (f && f.type.startsWith("image/")) handleFile(f);
    },
    [handleFile],
  );

  function handleSubmit() {
    if (!file) return;
    const fd = new FormData();
    fd.append("image", file);
    if (reportDate) fd.append("report_date", reportDate);
    if (department) fd.append("department", department);
    if (context) fd.append("context", context);
    onUpload(fd);
  }

  return (
    <div className="glass-card-solid p-6 space-y-4">
      <h2 className="text-lg font-semibold text-zinc-100">일보 이미지 분석</h2>

      {/* 드래그 앤 드롭 영역 */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          dragOver
            ? "drag-active border-indigo-500/60"
            : preview
              ? "border-indigo-500/30 bg-indigo-500/5"
              : "border-zinc-700 hover:border-zinc-500"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
          }}
        />
        {preview ? (
          <div className="space-y-3">
            <img
              src={preview}
              alt="미리보기"
              className="max-h-48 mx-auto rounded-lg object-contain"
            />
            <p className="text-sm text-zinc-400">{file?.name}</p>
            <p className="text-xs text-indigo-400">클릭하여 다른 이미지 선택</p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-4xl">📄</div>
            <p className="text-zinc-300">
              일보 이미지를 드래그하거나 클릭하여 업로드
            </p>
            <p className="text-xs text-zinc-500">PNG, JPEG, WebP (최대 10MB)</p>
          </div>
        )}
      </div>

      {/* 부가 입력 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div>
          <label className="text-xs text-zinc-500 mb-1 block">날짜</label>
          <input
            type="date"
            value={reportDate}
            onChange={(e) => setReportDate(e.target.value)}
            className="glass-input w-full px-3 py-2 text-sm text-zinc-200"
          />
        </div>
        <div>
          <label className="text-xs text-zinc-500 mb-1 block">부서/라인</label>
          <input
            type="text"
            placeholder="예: SMT-1라인"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="glass-input w-full px-3 py-2 text-sm text-zinc-200"
          />
        </div>
        <div>
          <label className="text-xs text-zinc-500 mb-1 block">추가 맥락</label>
          <input
            type="text"
            placeholder="목표치, 특이사항 등"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="glass-input w-full px-3 py-2 text-sm text-zinc-200"
          />
        </div>
      </div>

      {/* 분석 버튼 */}
      <button
        onClick={handleSubmit}
        disabled={!file || loading}
        className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${
          !file || loading
            ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
            : "bg-indigo-600 hover:bg-indigo-500 text-white"
        }`}
      >
        {loading ? "분석 중..." : "AI 분석 시작"}
      </button>
    </div>
  );
}
