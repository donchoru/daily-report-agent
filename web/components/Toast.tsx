"use client";

import { useEffect, useState, useCallback } from "react";

type ToastType = "success" | "error" | "info";

interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
  exiting?: boolean;
}

let toastId = 0;
let addToastFn: ((message: string, type: ToastType) => void) | null = null;

export function showToast(message: string, type: ToastType = "info") {
  addToastFn?.(message, type);
}

const COLORS: Record<ToastType, { bg: string; border: string; icon: string }> = {
  success: {
    bg: "rgba(16, 185, 129, 0.12)",
    border: "rgba(16, 185, 129, 0.3)",
    icon: "✓",
  },
  error: {
    bg: "rgba(239, 68, 68, 0.12)",
    border: "rgba(239, 68, 68, 0.3)",
    icon: "✕",
  },
  info: {
    bg: "rgba(99, 102, 241, 0.12)",
    border: "rgba(99, 102, 241, 0.3)",
    icon: "ℹ",
  },
};

const TEXT_COLORS: Record<ToastType, string> = {
  success: "text-emerald-300",
  error: "text-red-300",
  info: "text-indigo-300",
};

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = useCallback((message: string, type: ToastType) => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);

    const duration = type === "error" ? 5000 : 3000;
    setTimeout(() => {
      setToasts((prev) =>
        prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)),
      );
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 300);
    }, duration);
  }, []);

  useEffect(() => {
    addToastFn = addToast;
    return () => {
      addToastFn = null;
    };
  }, [addToast]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none">
      {toasts.map((toast) => {
        const color = COLORS[toast.type];
        return (
          <div
            key={toast.id}
            className={`pointer-events-auto glass-card-solid px-5 py-3 flex items-center gap-3 min-w-[280px] max-w-[420px] ${
              toast.exiting ? "animate-fade-out" : "animate-slide-up"
            }`}
            style={{
              background: color.bg,
              borderColor: color.border,
            }}
          >
            <span className={`text-lg font-bold ${TEXT_COLORS[toast.type]}`}>
              {color.icon}
            </span>
            <span className="text-sm text-zinc-200 flex-1">{toast.message}</span>
          </div>
        );
      })}

      <style jsx>{`
        @keyframes fade-out {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(8px); }
        }
        .animate-fade-out {
          animation: fade-out 0.3s ease-in forwards;
        }
      `}</style>
    </div>
  );
}
