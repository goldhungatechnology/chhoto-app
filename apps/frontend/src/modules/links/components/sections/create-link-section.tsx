"use client";

import * as React from "react";
import {
  Lightbulb,
  ExternalLink,
  Copy,
  Check,
  BarChart2,
  Link2,
} from "lucide-react";
import { useLinks } from "../../api/hooks/use-links";
import { CreateLinkCard } from "../blocks/create-link-card";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Alert } from "@/shared/components/ui/alert";

export function CreateLinkSection() {
  const { links, isLoadingLinks, linksError, refetchLinks } = useLinks();
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 w-full max-w-6xl px-4 py-8">
      {/* Left side: Main form */}
      <div className="lg:col-span-7 flex flex-col gap-6 items-center">
        <CreateLinkCard />
      </div>

      {/* Right side: Pro tip & Recent Links */}
      <div className="lg:col-span-5 flex flex-col gap-6">
        {/* Pro Tip Card */}
        <Card className="bg-gradient-brand-rich/10 border border-primary-border/20 p-6 rounded-3xl relative overflow-hidden">
          <div className="absolute -right-6 -bottom-6 text-primary/10 opacity-30 select-none pointer-events-none">
            <Lightbulb className="size-32 rotate-12" />
          </div>
          <div className="flex gap-4 relative z-10">
            <div className="flex items-center justify-center size-10 rounded-2xl bg-amber-500/10 text-amber-500 shrink-0">
              <Lightbulb className="size-5 fill-amber-500/20" />
            </div>
            <div className="space-y-1.5 text-left">
              <h4 className="text-sm font-bold text-foreground flex items-center gap-1.5">
                Pro Tip
              </h4>
              <p className="text-xs leading-relaxed text-muted-foreground">
                Using custom domains can increase click-through rate by up to{" "}
                <span className="font-semibold text-primary">34%</span>.
                Configure your custom domains in settings.
              </p>
            </div>
          </div>
        </Card>

        {/* Recent Links Card */}
        <Card className="flex-1 border border-border/60 p-6 rounded-3xl flex flex-col min-h-[350px]">
          <div className="flex items-center justify-between border-b border-border/40 pb-4 mb-4">
            <h3 className="font-bold text-foreground flex items-center gap-2">
              <Link2 className="size-4.5 text-primary" />
              <span>Recent Short Links</span>
            </h3>
            <span className="text-[10px] font-bold text-primary bg-primary-soft/20 dark:bg-primary-soft/10 px-2 py-0.5 rounded-full">
              {links.length} Active
            </span>
          </div>

          <div className="flex-1 flex flex-col gap-3 overflow-y-auto max-h-[450px] pr-1">
            {isLoadingLinks ? (
              // Loading Skeleton
              Array.from({ length: 3 }).map((_, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-border/40 rounded-2xl flex flex-col gap-2"
                >
                  <div className="flex justify-between items-center">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-4 w-10" />
                  </div>
                  <Skeleton className="h-3.5 w-2/3" />
                  <div className="flex gap-2 mt-1">
                    <Skeleton className="h-7 w-16 rounded-lg" />
                    <Skeleton className="h-7 w-16 rounded-lg" />
                  </div>
                </div>
              ))
            ) : linksError ? (
              // Error State
              <div className="py-8 text-center space-y-3">
                <Alert className="bg-destructive/10 text-destructive border-destructive/20 text-xs">
                  Failed to fetch recent links. Please try again.
                </Alert>
                <Button
                  size="sm"
                  variant="outline"
                  className="rounded-xl border border-border bg-background"
                  onClick={() => refetchLinks()}
                >
                  Retry Fetch
                </Button>
              </div>
            ) : links.length === 0 ? (
              // Empty State
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-muted-foreground gap-3">
                <div className="p-3 rounded-full bg-muted/40">
                  <Link2 className="size-6 text-muted-foreground/60" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground">
                    No short links yet
                  </p>
                  <p className="text-[11px] max-w-[200px] mt-1 mx-auto">
                    Create your first short link using the creation panel.
                  </p>
                </div>
              </div>
            ) : (
              // Links List
              links.map((link) => {
                const fullShortUrl = `${window.location.origin.replace("3000", "8000")}/api/v1/links/redirect/${link.short_url}`;
                const platformTag =
                  link.tags
                    ?.find((t) => t.startsWith("platform:"))
                    ?.split(":")[1] || "web";

                return (
                  <div
                    key={link.uuid}
                    className="p-3.5 border border-border/40 hover:border-primary-border/40 hover:bg-muted/5 rounded-2xl transition-all duration-200 flex flex-col gap-1 text-left relative group/link-item"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-xs truncate max-w-[180px] text-foreground">
                        {link.title || "Untitled Link"}
                      </span>
                      <span className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground bg-muted px-1.5 py-0.5 rounded-md">
                        {platformTag}
                      </span>
                    </div>

                    <p className="text-[11px] font-mono text-primary truncate select-all">
                      {fullShortUrl}
                    </p>

                    <p className="text-[10px] text-muted-foreground truncate mb-1">
                      Dest: {link.destination_url}
                    </p>

                    <div className="flex items-center justify-between gap-2 mt-1">
                      <div className="flex items-center gap-1 text-[10px] text-muted-foreground bg-muted/40 px-2 py-0.5 rounded-full font-semibold">
                        <BarChart2 className="size-3 text-primary" />
                        <span>{link.total_clicks} Clicks</span>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          size="xs"
                          variant="ghost"
                          className="size-7 rounded-lg p-0 text-muted-foreground hover:text-foreground"
                          onClick={() =>
                            copyToClipboard(fullShortUrl, link.uuid)
                          }
                        >
                          {copiedId === link.uuid ? (
                            <Check className="size-3.5 text-emerald-500" />
                          ) : (
                            <Copy className="size-3.5" />
                          )}
                        </Button>
                        <Button
                          size="xs"
                          variant="ghost"
                          className="size-7 rounded-lg p-0 text-muted-foreground hover:text-foreground"
                          asChild
                        >
                          <a
                            href={fullShortUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <ExternalLink className="size-3.5" />
                          </a>
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
