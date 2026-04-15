import type { ExtractedData } from "@/lib/types";
import { categoryLabel, categoryIcon } from "@/lib/utils";

const categories = ["production", "quality", "equipment", "workforce"] as const;

export default function ExtractedDataGrid({ data }: { data: ExtractedData }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {categories.map((cat) => {
        const entries = Object.entries(data[cat] || {});
        if (entries.length === 0) return null;
        return (
          <div key={cat} className="glass-card p-4 space-y-3">
            <div className="flex items-center gap-2">
              <span>{categoryIcon(cat)}</span>
              <h3 className="text-sm font-semibold text-zinc-200">
                {categoryLabel(cat)}
              </h3>
            </div>
            <div className="space-y-1.5">
              {entries.map(([k, v]) => (
                <div
                  key={k}
                  className="flex justify-between items-center text-sm"
                >
                  <span className="text-zinc-400">{k}</span>
                  <span className="text-zinc-200 font-medium">
                    {typeof v === "object" ? JSON.stringify(v) : String(v)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
