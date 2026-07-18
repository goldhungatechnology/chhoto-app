"use client";

import * as React from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/shared/components/ui/sheet";
import { useLinkSessions } from "../../api/hooks/use-link-sessions";
import { LinkData } from "../../types";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Monitor, Smartphone, Tablet, Globe } from "lucide-react";

interface LinkSessionsDrawerProps {
  link: LinkData | null;
  isOpen: boolean;
  onClose: () => void;
}

export function LinkSessionsDrawer({ link, isOpen, onClose }: LinkSessionsDrawerProps) {
  const { sessions, isLoadingSessions, sessionsError } = useLinkSessions(
    link?.uuid || "",
    isOpen
  );

  const getDeviceIcon = (device: string | null) => {
    const dev = device?.toLowerCase();
    if (dev === "mobile") return <Smartphone className="size-4 text-muted-foreground" />;
    if (dev === "tablet") return <Tablet className="size-4 text-muted-foreground" />;
    return <Monitor className="size-4 text-muted-foreground" />;
  };

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent
        side="right"
        className="data-[side=right]:sm:max-w-[70vw] data-[side=right]:w-[70vw] w-full bg-background border-l border-border flex flex-col h-full p-0 transition-all duration-300"
      >
        <SheetHeader className="p-6 border-b border-border/40 space-y-1">
          <SheetTitle className="text-xl font-bold text-slate-900 dark:text-zinc-50">Click Details</SheetTitle>
          {link && (
            <SheetDescription className="text-xs text-muted-foreground break-all">
              Sessions for <span className="font-semibold text-primary">{link.title || "Untitled Link"}</span>
            </SheetDescription>
          )}
        </SheetHeader>

        <div className="flex-1 overflow-auto">
          {isLoadingSessions ? (
            <div className="p-6 space-y-4">
              {Array.from({ length: 5 }).map((_, idx) => (
                <div key={idx} className="flex gap-4 animate-pulse py-3 border-b border-border/20">
                  <Skeleton className="h-4 w-1/5" />
                  <Skeleton className="h-4 w-1/5" />
                  <Skeleton className="h-4 w-1/5" />
                  <Skeleton className="h-4 w-1/5" />
                  <Skeleton className="h-4 w-1/5" />
                </div>
              ))}
            </div>
          ) : sessionsError ? (
            <div className="text-center py-8 text-xs text-destructive">
              Failed to load click details. Please try again.
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground space-y-3">
              <div className="inline-flex items-center justify-center size-12 rounded-full bg-muted/40">
                <Globe className="size-6 text-muted-foreground/60" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground">No clicks recorded yet</p>
                <p className="text-xs mt-1 max-w-[200px] mx-auto">
                  Share your link to start collecting statistics.
                </p>
              </div>
            </div>
          ) : (
            <div className="w-full overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[700px]">
                <thead>
                  <tr className="border-b border-border/50 bg-slate-50/50 dark:bg-slate-900/10 text-xs font-bold text-muted-foreground uppercase select-none">
                    <th className="py-3.5 px-6">IP Address</th>
                    <th className="py-3.5 px-6">Browser</th>
                    <th className="py-3.5 px-6">Device</th>
                    <th className="py-3.5 px-6">Referrer</th>
                    <th className="py-3.5 px-6">Date & Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30 text-sm text-foreground">
                  {sessions.map((session) => {
                    const dateStr = new Date(session.created_at).toLocaleString(undefined, {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    });
                    const referrerText = session.referral_source || "Direct / Organic";

                    return (
                      <tr key={session.uuid} className="hover:bg-slate-50/30 dark:hover:bg-slate-900/10 transition-colors">
                        {/* IP Address */}
                        <td className="py-3.5 px-6 font-mono text-xs text-muted-foreground select-all">
                          {session.ip_address || "Unknown"}
                        </td>

                        {/* Browser */}
                        <td className="py-3.5 px-6 text-slate-800 dark:text-slate-200 capitalize font-semibold">
                          {session.browser || "Unknown"}
                        </td>

                        {/* Device */}
                        <td className="py-3.5 px-6">
                          <div className="flex items-center gap-1.5 capitalize text-slate-700 dark:text-slate-300 font-medium">
                            {getDeviceIcon(session.device)}
                            <span>{session.device || "Unknown"}</span>
                          </div>
                        </td>

                        {/* Referrer */}
                        <td className="py-3.5 px-6 text-xs text-muted-foreground max-w-[180px] truncate" title={referrerText}>
                          {referrerText}
                        </td>

                        {/* Date & Time */}
                        <td className="py-3.5 px-6 text-xs text-muted-foreground font-medium whitespace-nowrap">
                          {dateStr}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
