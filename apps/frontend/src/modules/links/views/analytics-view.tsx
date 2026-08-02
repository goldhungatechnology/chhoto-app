"use client";

import * as React from "react";
import Link from "next/link";
import {
  MoreVertical,
  Edit2,
  BarChart2,
  Copy,
  ExternalLink,
  Search,
  Link2,
  MousePointerClick,
  Trophy,
  TrendingUp,
  Globe,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/shared/components/ui/button";
import { useLinks } from "../api/hooks";
import { LinkData } from "../types";
import { toast } from "@/shared/components/custom/snackbar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { EditTitleModal, LinkSessionsDrawer } from "../components/blocks";
import { REDIRECT_DOMAIN } from "@/core/config";

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  sub?: string;
  iconClass?: string;
}

function StatCard({ icon: Icon, label, value, sub, iconClass }: StatCardProps) {
  return (
    <div className="flex items-center gap-4 p-5 bg-card border border-border/60 rounded-3xl shadow-sm">
      <div
        className={cn(
          "flex items-center justify-center size-11 shrink-0 rounded-2xl",
          iconClass,
        )}
      >
        <Icon className="size-5" />
      </div>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-muted-foreground">{label}</p>
        <p className="text-xl font-extrabold tracking-tight text-foreground truncate">
          {value}
        </p>
        {sub && <p className="text-xs text-muted-foreground truncate">{sub}</p>}
      </div>
    </div>
  );
}

export function AnalyticsView() {
  const { links, isLoadingLinks } = useLinks();
  const [searchTerm, setSearchTerm] = React.useState("");

  // Modals / Drawer state
  const [selectedLink, setSelectedLink] = React.useState<LinkData | null>(null);
  const [isEditOpen, setIsEditOpen] = React.useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = React.useState(false);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Link copied to clipboard!");
    } catch (err) {
      console.error(err);
    }
  };

  const filteredLinks = links.filter((link) => {
    const search = searchTerm.toLowerCase();
    return (
      (link.title || "").toLowerCase().includes(search) ||
      link.short_url.toLowerCase().includes(search) ||
      link.destination_url.toLowerCase().includes(search)
    );
  });

  const totalLinks = links.length;
  const totalClicks = links.reduce((sum, link) => sum + link.total_clicks, 0);
  const bestLink = links.reduce<LinkData | null>(
    (best, link) =>
      best === null || link.total_clicks > best.total_clicks ? link : best,
    null,
  );
  const avgClicks = totalLinks ? Math.round(totalClicks / totalLinks) : 0;

  const getHostname = (url: string) => {
    try {
      return new URL(url).hostname.replace(/^www\./, "");
    } catch {
      return url;
    }
  };

  const getPlatformBadgeColor = (platform: string) => {
    const plat = platform.toLowerCase();
    if (plat === "instagram") {
      return "bg-pink-50 text-pink-700 dark:bg-pink-950/20 dark:text-pink-400";
    }
    if (plat === "youtube") {
      return "bg-red-50 text-red-700 dark:bg-red-950/20 dark:text-red-400";
    }
    if (plat === "tiktok") {
      return "bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300";
    }
    if (plat === "web") {
      return "bg-blue-50 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400";
    }
    if (plat === "ads") {
      return "bg-purple-50 text-purple-700 dark:bg-purple-950/20 dark:text-purple-400";
    }
    return "bg-slate-100 text-slate-600 dark:bg-slate-900 dark:text-slate-400";
  };

  const getClicksBadgeColor = (clicks: number) => {
    if (clicks === 0) {
      return "bg-slate-100 text-slate-500 dark:bg-slate-900 dark:text-slate-400";
    }
    if (clicks < 10) {
      return "bg-blue-50 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400";
    }
    if (clicks < 100) {
      return "bg-amber-50 text-amber-700 dark:bg-amber-950/20 dark:text-amber-400";
    }
    return "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400";
  };

  return (
    <div className="flex flex-col flex-1 bg-zinc-50/50 dark:bg-black/50 font-sans w-full min-h-[calc(100vh-64px)] py-8 px-4 md:px-8">
      <div className="max-w-7xl w-full mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-950 dark:text-zinc-50">
              Analytics
            </h1>
            <p className="text-sm text-muted-foreground">
              Track clicks, platforms, and locations across your short links.
            </p>
          </div>

          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search links..."
              className="h-10 w-full pl-9 pr-4 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:outline-none focus:border-slate-400"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={Link2}
            label="Total Links"
            value={totalLinks}
            iconClass="bg-primary-soft/15 text-primary"
          />
          <StatCard
            icon={MousePointerClick}
            label="Total Clicks"
            value={totalClicks.toLocaleString()}
            iconClass="bg-blue-50 text-blue-600 dark:bg-blue-950/20 dark:text-blue-400"
          />
          <StatCard
            icon={Trophy}
            label="Best Performing"
            value={bestLink?.title || "—"}
            sub={
              bestLink
                ? `${bestLink.total_clicks.toLocaleString()} clicks`
                : "No clicks yet"
            }
            iconClass="bg-amber-50 text-amber-600 dark:bg-amber-950/20 dark:text-amber-400"
          />
          <StatCard
            icon={TrendingUp}
            label="Avg Clicks / Link"
            value={avgClicks.toLocaleString()}
            iconClass="bg-emerald-50 text-emerald-600 dark:bg-emerald-950/20 dark:text-emerald-400"
          />
        </div>

        {/* Table card */}
        <div className="border border-border/60 rounded-3xl overflow-hidden shadow-sm bg-white dark:bg-card">
          <div className="flex items-center justify-between px-6 py-5 border-b border-border/50">
            <div className="space-y-0.5">
              <h2 className="text-sm font-bold text-foreground">All Links</h2>
              <p className="text-xs text-muted-foreground">
                {filteredLinks.length} {filteredLinks.length === 1 ? "link" : "links"}
              </p>
            </div>
            <Button size="sm" className="rounded-xl" asChild>
              <Link href="/links">
                <Link2 className="size-3.5" />
                New Link
              </Link>
            </Button>
          </div>

          <div className="w-full overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[860px]">
              <thead>
                <tr className="border-b border-border/50 bg-slate-50/50 dark:bg-slate-900/10 text-xs font-bold text-muted-foreground uppercase select-none">
                  <th className="py-3.5 px-6">Link</th>
                  <th className="py-3.5 px-6">Platform</th>
                  <th className="py-3.5 px-6">Clicks</th>
                  <th className="py-3.5 px-6">Created</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30 text-sm text-foreground">
                {isLoadingLinks ? (
                  Array.from({ length: 5 }).map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td className="py-4.5 px-6">
                        <div className="h-4 bg-slate-100 dark:bg-slate-900 rounded-md w-44"></div>
                      </td>
                      <td className="py-4.5 px-6">
                        <div className="h-6 bg-slate-100 dark:bg-slate-900 rounded-full w-20"></div>
                      </td>
                      <td className="py-4.5 px-6">
                        <div className="h-6 bg-slate-100 dark:bg-slate-900 rounded-md w-12"></div>
                      </td>
                      <td className="py-4.5 px-6">
                        <div className="h-4 bg-slate-100 dark:bg-slate-900 rounded-md w-24"></div>
                      </td>
                      <td className="py-4.5 px-6 text-right">
                        <div className="h-8 bg-slate-100 dark:bg-slate-900 rounded-md w-8 ml-auto"></div>
                      </td>
                    </tr>
                  ))
                ) : filteredLinks.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="text-center py-16 text-muted-foreground"
                    >
                      <div className="flex flex-col items-center gap-3">
                        <div className="inline-flex items-center justify-center size-12 rounded-full bg-muted/40">
                          <Globe className="size-6 text-muted-foreground/60" />
                        </div>
                        <div className="space-y-1">
                          <p className="text-sm font-semibold text-slate-800 dark:text-zinc-100">
                            No short links found
                          </p>
                          <p className="text-xs max-w-[240px] mx-auto">
                            Create a link or adjust your search to view analytics.
                          </p>
                        </div>
                        <Button size="sm" variant="outline" className="rounded-xl mt-1" asChild>
                          <Link href="/links">Create a link</Link>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredLinks.map((link) => {
                    const fullShortUrl = `${REDIRECT_DOMAIN}/${link.short_url}`;
                    const platformTag =
                      link.tags
                        ?.find((t) => t.startsWith("platform:"))
                        ?.split(":")[1] || "web";

                    const dateCreated = new Date(link.created_at).toLocaleDateString(
                      undefined,
                      {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      },
                    );

                    return (
                      <tr
                        key={link.uuid}
                        className="hover:bg-slate-50/40 dark:hover:bg-slate-900/10 transition-colors"
                      >
                        {/* Link */}
                        <td className="py-4 px-6 max-w-[300px]">
                          <div className="flex flex-col gap-1 min-w-0">
                            <span
                              className="font-semibold text-slate-900 dark:text-zinc-50 truncate"
                              title={link.title || "Untitled Link"}
                            >
                              {link.title || "Untitled Link"}
                            </span>
                            <div className="flex items-center gap-1.5 min-w-0">
                              <span className="text-xs font-semibold text-primary font-mono select-all truncate">
                                {link.short_url}
                              </span>
                              <button
                                onClick={() => copyToClipboard(fullShortUrl)}
                                className="text-muted-foreground hover:text-foreground hover:cursor-pointer p-0.5 shrink-0"
                                title="Copy short link"
                              >
                                <Copy className="size-3" />
                              </button>
                            </div>
                            <div className="flex items-center gap-1.5 text-xs text-muted-foreground min-w-0">
                              <span
                                className="truncate"
                                title={link.destination_url}
                              >
                                {getHostname(link.destination_url)}
                              </span>
                              <a
                                href={link.destination_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-muted-foreground hover:text-foreground shrink-0"
                              >
                                <ExternalLink className="size-3" />
                              </a>
                            </div>
                          </div>
                        </td>

                        {/* Platform */}
                        <td className="py-4 px-6">
                          <span
                            className={cn(
                              "text-[11px] font-semibold rounded-full px-2.5 py-1 capitalize",
                              getPlatformBadgeColor(platformTag),
                            )}
                          >
                            {platformTag}
                          </span>
                        </td>

                        {/* Clicks */}
                        <td className="py-4 px-6">
                          <span
                            className={cn(
                              "text-xs font-bold rounded-full px-2.5 py-1",
                              getClicksBadgeColor(link.total_clicks),
                            )}
                          >
                            {link.total_clicks.toLocaleString()}
                          </span>
                        </td>

                        {/* Created */}
                        <td className="py-4 px-6 text-xs text-muted-foreground font-medium whitespace-nowrap">
                          {dateCreated}
                        </td>

                        {/* Actions */}
                        <td className="py-4 px-6 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon-sm"
                                className="size-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800"
                              >
                                <MoreVertical className="size-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                              align="end"
                              className="w-44 p-1.5 rounded-xl border border-border bg-popover"
                            >
                              <DropdownMenuItem
                                onClick={() => {
                                  setSelectedLink(link);
                                  setIsEditOpen(true);
                                }}
                                className="cursor-pointer rounded-lg text-xs font-semibold"
                              >
                                <Edit2 className="mr-2 h-3.5 w-3.5 text-muted-foreground" />
                                <span>Edit Title</span>
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => {
                                  setSelectedLink(link);
                                  setIsDrawerOpen(true);
                                }}
                                className="cursor-pointer rounded-lg text-xs font-semibold"
                              >
                                <BarChart2 className="mr-2 h-3.5 w-3.5 text-muted-foreground" />
                                <span>View Click Details</span>
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modals & Drawer */}
      <EditTitleModal
        link={selectedLink}
        isOpen={isEditOpen}
        onClose={() => {
          setIsEditOpen(false);
          setSelectedLink(null);
        }}
      />

      <LinkSessionsDrawer
        link={selectedLink}
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedLink(null);
        }}
      />
    </div>
  );
}
