interface Stat {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
}

export default function StatsCards({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {stats.map((s) => (
        <div key={s.label} className="glass-card p-5">
          <p className="text-zinc-500 text-sm">{s.label}</p>
          <p className={`text-2xl font-bold mt-1 ${s.color || "text-zinc-100"}`}>
            {s.value}
          </p>
          {s.sub && <p className="text-xs text-zinc-500 mt-1">{s.sub}</p>}
        </div>
      ))}
    </div>
  );
}
