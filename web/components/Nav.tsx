"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "대시보드" },
  { href: "/timeline", label: "타임라인" },
  { href: "/compare", label: "비교 분석" },
  { href: "/settings", label: "설정" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <nav className="fixed top-0 inset-x-0 z-50 glass-card-solid border-t-0 rounded-none border-x-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 text-lg font-bold">
          <span className="gradient-text">DRA</span>
          <span className="text-zinc-400 text-sm font-normal hidden sm:inline">
            제조 일보 AI
          </span>
        </Link>
        <div className="flex gap-1">
          {links.map((l) => {
            const active =
              l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`relative px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  active
                    ? "bg-violet-500/15 text-violet-300"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
                }`}
              >
                {l.label}
                {active && (
                  <span
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-0.5 rounded-full"
                    style={{
                      background: "linear-gradient(90deg, #8b5cf6, #6366f1)",
                    }}
                  />
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
