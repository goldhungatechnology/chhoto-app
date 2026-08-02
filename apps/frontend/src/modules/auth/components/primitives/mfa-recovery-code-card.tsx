"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface MfaRecoveryCodeCardProps {
  code: string;
  className?: string;
}

export function MfaRecoveryCodeCard({ code, className }: MfaRecoveryCodeCardProps) {
  return (
    <div
      className={cn(
        "h-11 rounded-xl border border-slate-200/80 bg-slate-50/60 dark:border-zinc-800 dark:bg-zinc-900/60 px-3.5 flex items-center justify-center font-mono text-sm tracking-widest text-slate-700 dark:text-zinc-300 font-semibold select-all shadow-2xs transition-colors hover:border-slate-300 dark:hover:border-zinc-700",
        className
      )}
    >
      {code}
    </div>
  );
}
