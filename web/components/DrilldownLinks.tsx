import type { DrilldownLink } from "@/lib/types";

const categoryColors: Record<string, string> = {
  production: "text-blue-400 bg-blue-500/10",
  quality: "text-amber-400 bg-amber-500/10",
  equipment: "text-purple-400 bg-purple-500/10",
  workforce: "text-emerald-400 bg-emerald-500/10",
  inventory: "text-cyan-400 bg-cyan-500/10",
  energy: "text-orange-400 bg-orange-500/10",
  cost: "text-pink-400 bg-pink-500/10",
};

export default function DrilldownLinks({ links }: { links: DrilldownLink[] }) {
  if (!links || links.length === 0) return null;

  return (
    <section>
      <h3 className="text-sm font-semibold text-zinc-300 mb-3">
        연계 시스템 바로가기
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {links.map((link, i) => {
          const color = categoryColors[link.category] || "text-zinc-400 bg-zinc-500/10";
          return (
            <div
              key={i}
              className="glass-card p-3 hover-glow-subtle cursor-pointer group"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${color}`}
                >
                  {link.category}
                </span>
                <span className="text-sm font-medium text-zinc-200 group-hover:text-indigo-300 transition-colors">
                  {link.name}
                </span>
              </div>
              <p className="text-xs text-zinc-500 mt-1">{link.description}</p>
              {link.reason && (
                <p className="text-xs text-zinc-600 mt-0.5">
                  사유: {link.reason}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
