"use client";

import * as React from "react";
import { Lock } from "lucide-react";
import { MfaStatusBadge } from "../primitives";

interface MfaMethodCardProps {
  enabled: boolean;
  onToggleMfa: () => void;
  isLoading?: boolean;
}

export function MfaMethodCard({
  enabled,
  onToggleMfa,
  isLoading = false,
}: MfaMethodCardProps) {
  return (
    <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-50/70 dark:bg-zinc-900/50 border border-slate-200/60 dark:border-zinc-800/60 transition-all">
      <div className="flex items-center gap-3.5 min-w-0">
        <div className="size-10 rounded-xl bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400 flex items-center justify-center border border-purple-500/20 shrink-0">
          <Lock className="size-5" />
        </div>
        <div className="space-y-0.5 min-w-0">
          <h4 className="text-sm font-bold text-slate-900 dark:text-zinc-100 truncate">
            Authenticator App
          </h4>
          <p className="text-xs text-muted-foreground truncate">
            {enabled ? "Using Google Authenticator or Authy" : "Not configured"}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <MfaStatusBadge enabled={enabled} />

        <button
          type="button"
          onClick={onToggleMfa}
          disabled={isLoading}
          className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
            enabled ? "bg-emerald-500" : "bg-slate-300 dark:bg-zinc-700"
          }`}
          role="switch"
          aria-checked={enabled}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${
              enabled ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
      </div>
    </div>
  );
}
