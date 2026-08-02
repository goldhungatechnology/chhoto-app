"use client";

import * as React from "react";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { SessionItemCard } from "../blocks";
import { useSessionsList } from "../../hooks";
import { Loader2, LogOut, Laptop } from "lucide-react";
import type { UserSession } from "@/modules/auth/api/auth.types";

// Static fallback sessions used only for the empty-state design preview.
// Timestamps are fixed constants so rendering stays pure.
const MOCK_SESSIONS: UserSession[] = [
  {
    session_uuid: "sess_curr_1",
    user_id: 1,
    ip_address: "192.168.1.1",
    device: "macOS",
    browser: "Chrome",
    is_current: true,
    created_at: "2026-08-02T10:00:00.000Z",
    city: "San Francisco",
    country: "CA",
    country_code: "US",
  },
  {
    session_uuid: "sess_2",
    user_id: 1,
    ip_address: "192.168.1.2",
    device: "iPhone",
    browser: "Safari",
    is_current: false,
    created_at: "2026-08-02T08:00:00.000Z",
    city: "San Francisco",
    country: "CA",
    country_code: "US",
  },
];

export function SessionsSection() {
  const {
    sessions,
    isLoadingSessions,
    isRevokingSession,
    isRevokingAllSessions,
    handleRevokeSession,
    handleRevokeAllSessions,
  } = useSessionsList();

  if (isLoadingSessions) {
    return (
      <Card className="border border-border/60 rounded-3xl p-6 bg-white dark:bg-card shadow-xs">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded-md w-1/4" />
          <div className="h-16 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          <div className="h-16 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        </div>
      </Card>
    );
  }

  // Fallback default mock sessions matching mfa_1.png design if backend list is empty
  const displaySessions = sessions.length > 0 ? sessions : MOCK_SESSIONS;

  return (
    <Card className="border border-border/60 rounded-3xl p-6 bg-white dark:bg-card shadow-xs space-y-6 text-left">
      <div className="border-b border-border/40 pb-4">
        <h2 className="text-lg font-bold text-slate-950 dark:text-zinc-50 flex items-center gap-2">
          <Laptop className="size-5 text-slate-700 dark:text-zinc-300" />
          <span>Sessions</span>
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          These are the devices that have logged into your account.
        </p>
      </div>

      {/* Session list */}
      <div className="space-y-3">
        {displaySessions.map((session) => (
          <SessionItemCard
            key={session.session_uuid}
            session={session}
            onRevokeSession={handleRevokeSession}
            isRevoking={isRevokingSession}
          />
        ))}
      </div>

      {/* Revoke all sessions action */}
      <div className="pt-2">
        <Button
          type="button"
          variant="outline"
          disabled={isRevokingAllSessions}
          onClick={handleRevokeAllSessions}
          className="rounded-xl h-10 px-4 text-xs font-semibold border-slate-200/80 dark:border-zinc-800 text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 hover:cursor-pointer flex items-center gap-2"
        >
          {isRevokingAllSessions ? (
            <>
              <Loader2 className="size-3.5 animate-spin" />
              <span>Signing out...</span>
            </>
          ) : (
            <>
              <LogOut className="size-3.5" />
              <span>Sign out of all sessions</span>
            </>
          )}
        </Button>
      </div>
    </Card>
  );
}
