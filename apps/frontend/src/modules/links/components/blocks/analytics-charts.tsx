"use client";

import * as React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";
import { Activity, Smartphone, Globe2, Compass, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AnalyticsOverview } from "../../api/hooks/use-analytics-overview";

const PIE_COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#ec4899",
  "#f59e0b",
  "#10b981",
  "#64748b",
];

const AXIS_TICK = { fontSize: 11, fill: "#94a3b8" };
const GRID_STROKE = "rgba(148,163,184,0.2)";
const PRIMARY = "#6366f1";

interface TooltipEntry {
  name?: string | number;
  value?: number | string;
  color?: string;
}

function ChartTooltip({
  active,
  label,
  payload,
}: {
  active?: boolean;
  label?: string | number;
  payload?: TooltipEntry[];
}) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="rounded-xl border border-border bg-background/95 px-3 py-2 shadow-md backdrop-blur-sm">
      {label !== undefined && (
        <p className="mb-1 text-xs font-semibold text-muted-foreground">
          {label}
        </p>
      )}
      {payload.map((entry, idx) => (
        <p
          key={idx}
          className="flex items-center gap-2 text-sm font-medium text-foreground"
        >
          <span
            className="inline-block size-2 shrink-0 rounded-full"
            style={{ background: entry.color || PIE_COLORS[0] }}
          />
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
}

function ChartEmpty() {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
      <div className="flex items-center justify-center size-10 rounded-full bg-muted/40">
        <Inbox className="size-5 text-muted-foreground/60" />
      </div>
      <p className="text-sm font-semibold text-foreground">No data yet</p>
      <p className="text-xs text-muted-foreground max-w-[200px]">
        Clicks will appear here once your links are shared.
      </p>
    </div>
  );
}

function ChartCard({
  title,
  subtitle,
  icon: Icon,
  className,
  children,
}: {
  title: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "flex flex-col bg-card border border-border/60 rounded-3xl shadow-sm p-6",
        className,
      )}
    >
      <div className="mb-5 flex items-start justify-between gap-3">
        <div className="space-y-0.5">
          <h3 className="text-sm font-bold text-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        </div>
        <div className="flex items-center justify-center size-9 shrink-0 rounded-xl bg-primary-soft/10 text-primary">
          <Icon className="size-4" />
        </div>
      </div>
      {children}
    </div>
  );
}

function ChartsSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 animate-pulse">
      <div className="lg:col-span-2 h-[320px] rounded-3xl border border-border/60 bg-white dark:bg-card p-6">
        <div className="h-4 w-40 rounded-md bg-slate-100 dark:bg-slate-900" />
        <div className="mt-6 h-56 rounded-2xl bg-slate-100 dark:bg-slate-900" />
      </div>
      <div className="h-[320px] rounded-3xl border border-border/60 bg-white dark:bg-card p-6">
        <div className="h-4 w-36 rounded-md bg-slate-100 dark:bg-slate-900" />
        <div className="mt-6 h-56 rounded-2xl bg-slate-100 dark:bg-slate-900" />
      </div>
    </div>
  );
}

export function AnalyticsCharts({
  overview,
  loading,
}: {
  overview?: AnalyticsOverview;
  loading: boolean;
}) {
  if (loading) return <ChartsSkeleton />;
  if (!overview || overview.totalSessions === 0) return null;

  const { clicksPerDay, devices, browsers, countries } = overview;
  const topCountries = countries.slice(0, 6);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Clicks over time */}
      <ChartCard
        title="Clicks Over Time"
        subtitle="Clicks per day across all links"
        icon={Activity}
        className="lg:col-span-2"
      >
        {clicksPerDay.length ? (
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={clicksPerDay}
                margin={{ top: 4, right: 4, left: -18, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="clicksGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={PRIMARY} stopOpacity={0.35} />
                    <stop offset="100%" stopColor={PRIMARY} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={GRID_STROKE}
                  vertical={false}
                />
                <XAxis
                  dataKey="label"
                  tick={AXIS_TICK}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={AXIS_TICK}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  content={<ChartTooltip />}
                  cursor={{ stroke: GRID_STROKE }}
                />
                <Area
                  type="monotone"
                  dataKey="clicks"
                  name="Clicks"
                  stroke={PRIMARY}
                  strokeWidth={2}
                  fill="url(#clicksGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <ChartEmpty />
        )}
      </ChartCard>

      {/* Device breakdown */}
      <ChartCard
        title="Device Breakdown"
        subtitle="Where your clicks come from"
        icon={Smartphone}
      >
        {devices.length ? (
          <>
            <div className="relative h-[180px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={devices}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={58}
                    outerRadius={82}
                    paddingAngle={2}
                    strokeWidth={0}
                  >
                    {devices.map((_, idx) => (
                      <Cell
                        key={idx}
                        fill={PIE_COLORS[idx % PIE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-extrabold text-foreground">
                  {overview.totalSessions}
                </span>
                <span className="text-xs text-muted-foreground">
                  total clicks
                </span>
              </div>
            </div>
            <ul className="mt-5 space-y-2">
              {devices.slice(0, 5).map((device, idx) => (
                <li
                  key={device.name}
                  className="flex items-center gap-2 text-xs"
                >
                  <span
                    className="inline-block size-2.5 shrink-0 rounded-full"
                    style={{
                      background: PIE_COLORS[idx % PIE_COLORS.length],
                    }}
                  />
                  <span className="flex-1 font-medium text-muted-foreground capitalize">
                    {device.name}
                  </span>
                  <span className="font-bold text-foreground">
                    {device.value}
                  </span>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <ChartEmpty />
        )}
      </ChartCard>

      {/* Top countries */}
      <ChartCard
        title="Top Countries"
        subtitle="Clicks grouped by location"
        icon={Globe2}
        className="lg:col-span-2"
      >
        {topCountries.length ? (
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={topCountries}
                layout="vertical"
                margin={{ top: 0, right: 8, left: 0, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={GRID_STROKE}
                  horizontal={false}
                />
                <XAxis
                  type="number"
                  tick={AXIS_TICK}
                  tickLine={false}
                  axisLine={false}
                  allowDecimals={false}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={110}
                  tick={AXIS_TICK}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  content={<ChartTooltip />}
                  cursor={{ fill: GRID_STROKE }}
                />
                <Bar
                  dataKey="value"
                  name="Clicks"
                  fill={PRIMARY}
                  radius={[0, 8, 8, 0]}
                  barSize={16}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <ChartEmpty />
        )}
      </ChartCard>

      {/* Browsers */}
      <ChartCard
        title="Browsers"
        subtitle="Browser usage across sessions"
        icon={Compass}
      >
        {browsers.length ? (
          <div className="space-y-4">
            {browsers.slice(0, 6).map((browser, idx) => {
              const pct = Math.round(
                (browser.value / overview.totalSessions) * 100,
              );
              return (
                <div key={browser.name} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-foreground capitalize">
                      {browser.name}
                    </span>
                    <span className="font-bold text-muted-foreground">
                      {pct}%
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-muted/40">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${pct}%`,
                        background: PIE_COLORS[idx % PIE_COLORS.length],
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <ChartEmpty />
        )}
      </ChartCard>
    </div>
  );
}
