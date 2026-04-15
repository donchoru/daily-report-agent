"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceDot,
} from "recharts";
import type { TimelineItem } from "@/lib/types";
import { numericValue, formatShortDate } from "@/lib/utils";

interface ChartPoint {
  date: string;
  dateLabel: string;
  달성률: number | null;
  불량률: number | null;
  가동률: number | null;
  hasAnomaly: boolean;
  id: string;
}

function buildChartData(items: TimelineItem[]): ChartPoint[] {
  return items.map((item) => ({
    date: item.report_date,
    dateLabel: formatShortDate(item.report_date),
    달성률: numericValue(item.extracted_data.production, "달성률", "achievement_rate"),
    불량률: numericValue(item.extracted_data.quality, "불량률", "defect_rate"),
    가동률: numericValue(item.extracted_data.equipment, "가동률", "utilization_rate"),
    hasAnomaly: (item.insights.anomalies?.length || 0) > 0,
    id: item.id,
  }));
}

interface Props {
  items: TimelineItem[];
  onDateClick?: (id: string) => void;
}

export default function TimelineChart({ items, onDateClick }: Props) {
  const data = buildChartData(items);
  const anomalyPoints = data.filter((d) => d.hasAnomaly);

  return (
    <div className="glass-card-solid p-5">
      <h3 className="text-sm font-semibold text-zinc-300 mb-4">
        주요 지표 트렌드
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            onClick={(e) => {
              if (e?.activePayload?.[0]?.payload?.id) {
                onDateClick?.(e.activePayload[0].payload.id);
              }
            }}
          >
            <defs>
              <linearGradient id="grad-green" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="grad-red" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="grad-blue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.05)"
            />
            <XAxis
              dataKey="dateLabel"
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                background: "#18181b",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 12,
                padding: "8px 12px",
                fontSize: 12,
              }}
              formatter={(value: number, name: string) => [
                `${value}%`,
                name,
              ]}
              labelFormatter={(label) => `날짜: ${label}`}
            />
            <Area
              type="monotone"
              dataKey="달성률"
              stroke="#10b981"
              fill="url(#grad-green)"
              strokeWidth={2}
              dot={false}
              connectNulls
            />
            <Area
              type="monotone"
              dataKey="불량률"
              stroke="#ef4444"
              fill="url(#grad-red)"
              strokeWidth={2}
              dot={false}
              connectNulls
            />
            <Area
              type="monotone"
              dataKey="가동률"
              stroke="#6366f1"
              fill="url(#grad-blue)"
              strokeWidth={2}
              dot={false}
              connectNulls
            />
            {/* 이상 감지일 마커 */}
            {anomalyPoints.map((p) => (
              <ReferenceDot
                key={p.date}
                x={p.dateLabel}
                y={p.불량률 ?? 0}
                r={5}
                fill="#ef4444"
                stroke="#18181b"
                strokeWidth={2}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-4 mt-3 justify-center">
        <span className="flex items-center gap-1 text-xs text-emerald-400">
          <span className="w-3 h-0.5 bg-emerald-400 rounded" /> 달성률
        </span>
        <span className="flex items-center gap-1 text-xs text-red-400">
          <span className="w-3 h-0.5 bg-red-400 rounded" /> 불량률
        </span>
        <span className="flex items-center gap-1 text-xs text-indigo-400">
          <span className="w-3 h-0.5 bg-indigo-400 rounded" /> 가동률
        </span>
        <span className="flex items-center gap-1 text-xs text-red-400">
          ● 이상 감지
        </span>
      </div>
    </div>
  );
}
