import type { Anomaly } from "@/lib/types";
import SeverityBadge from "./SeverityBadge";

export default function AnomalyCard({ anomaly }: { anomaly: Anomaly }) {
  return (
    <div className="glass-card p-4 space-y-2 border-l-2 border-l-red-500/40">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-zinc-200">
          {anomaly.metric}
        </span>
        <SeverityBadge severity={anomaly.severity} />
      </div>
      <div className="flex gap-4 text-sm">
        <span className="text-red-400">
          실측: <span className="font-semibold">{anomaly.value}</span>
        </span>
        {anomaly.expected && (
          <span className="text-zinc-500">
            기준: {anomaly.expected}
          </span>
        )}
      </div>
      {anomaly.description && (
        <p className="text-xs text-zinc-400">{anomaly.description}</p>
      )}
    </div>
  );
}
