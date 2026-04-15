import { severityColor } from "@/lib/utils";

export default function SeverityBadge({ severity }: { severity: string }) {
  const c = severityColor(severity);
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${c.bg} ${c.text} ${c.border} border`}
    >
      {severity}
    </span>
  );
}
