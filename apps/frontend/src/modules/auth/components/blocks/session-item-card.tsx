"use client";

import * as React from "react";
import { UserSession } from "@/modules/auth/api/auth.types";
import { SessionDeviceIcon } from "../primitives";
import { Button } from "@/shared/components/ui/button";
import { LogOut } from "lucide-react";

interface SessionItemCardProps {
  session: UserSession;
  onRevokeSession?: (sessionUuid: string) => void;
  isRevoking?: boolean;
}

export function SessionItemCard({
  session,
  onRevokeSession,
  isRevoking = false,
}: SessionItemCardProps) {
  const deviceName = session.device || "Unknown Device";
  const browserName = session.browser || "";
  const title = browserName ? `${browserName} on ${deviceName}` : deviceName;

  const locationText = [session.city, session.country]
    .filter(Boolean)
    .join(", ") || "Unknown Location";

  return (
    <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-50/70 dark:bg-zinc-900/50 border border-slate-200/60 dark:border-zinc-800/60 transition-all hover:bg-slate-100/60 dark:hover:bg-zinc-900/80">
      <div className="flex items-center gap-3.5 min-w-0">
        <SessionDeviceIcon device={session.device} browser={session.browser} />
        <div className="space-y-0.5 truncate">
          <h4 className="text-sm font-bold text-slate-900 dark:text-zinc-100 truncate">
            {title}
          </h4>
          <p className="text-xs text-muted-foreground truncate">
            {locationText}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {session.is_current ? (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400 border border-emerald-500/20">
            ACTIVE NOW
          </span>
        ) : (
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground hidden sm:inline-block">
              Last active
            </span>
            {onRevokeSession && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                disabled={isRevoking}
                onClick={() => onRevokeSession(session.session_uuid || session.uuid || "")}
                className="h-8 px-2.5 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg hover:cursor-pointer"
                title="Revoke session"
              >
                <LogOut className="size-3.5 mr-1" />
                <span>Revoke</span>
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
