"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ShieldCheck, ShieldOff } from "lucide-react";

interface MfaStatusBadgeProps {
  enabled: boolean;
  className?: string;
}

export function MfaStatusBadge({ enabled, className }: MfaStatusBadgeProps) {
  if (enabled) {
    return (
      <div
        className={cn(
          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400 border border-emerald-500/20",
          className
        )}
      >
        <ShieldCheck className="size-3.5" />
        <span>Enabled</span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 dark:bg-zinc-800 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700",
        className
      )}
    >
      <ShieldOff className="size-3.5" />
      <span>Not Configured</span>
    </div>
  );
}
