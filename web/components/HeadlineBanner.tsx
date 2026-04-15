import type { Headlines } from "@/lib/types";
import { sentimentColor } from "@/lib/utils";

interface Props {
  headlines: Headlines | null;
  department?: string | null;
  reportDate?: string | null;
}

export default function HeadlineBanner({ headlines, department, reportDate }: Props) {
  if (!headlines) return null;
  const sc = sentimentColor(headlines.sentiment);

  return (
    <div className="glass-card-solid p-6 space-y-3">
      <div className="flex items-center gap-3 flex-wrap">
        {department && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400">
            {department}
          </span>
        )}
        {reportDate && (
          <span className="text-xs text-zinc-500">{reportDate}</span>
        )}
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${sc.bg} ${sc.text}`}
        >
          {headlines.sentiment === "positive"
            ? "긍정"
            : headlines.sentiment === "negative"
              ? "부정"
              : "중립"}
        </span>
      </div>

      <h1 className="text-xl sm:text-2xl font-bold text-zinc-100">
        {headlines.main_headline}
      </h1>

      {headlines.sub_headlines?.length > 0 && (
        <ul className="space-y-1">
          {headlines.sub_headlines.map((s, i) => (
            <li key={i} className="text-sm text-zinc-400 flex items-start gap-2">
              <span className="text-indigo-400 mt-0.5">·</span>
              {s}
            </li>
          ))}
        </ul>
      )}

      {headlines.key_metric && (
        <p className="text-xs text-zinc-500">
          핵심 지표: <span className="text-zinc-300">{headlines.key_metric}</span>
        </p>
      )}
    </div>
  );
}
