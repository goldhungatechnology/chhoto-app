"use client";

import * as React from "react";
import {
  MoreVertical,
  Edit2,
  BarChart2,
  Copy,
  ExternalLink,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Card } from "@/shared/components/ui/card";
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

  const getPlatformBadgeColor = (platform: string) => {
    const plat = platform.toLowerCase();
    if (plat === "instagram") {
      return "bg-pink-50 text-pink-700 border-pink-100 dark:bg-pink-950/20 dark:text-pink-400 dark:border-pink-900/30";
    }
    if (plat === "youtube") {
      return "bg-red-50 text-red-700 border-red-100 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/30";
    }
    if (plat === "tiktok") {
      return "bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-900/20 dark:text-slate-300 dark:border-slate-800/30";
    }
    if (plat === "web") {
      return "bg-blue-50 text-blue-700 border-blue-100 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/30";
    }
    if (plat === "ads") {
      return "bg-purple-50 text-purple-700 border-purple-100 dark:bg-purple-950/20 dark:text-purple-400 dark:border-purple-900/30";
    }
    return "bg-slate-50 text-slate-600 border-slate-100 dark:bg-slate-900/10 dark:text-slate-400 dark:border-slate-800/10";
  };

  const getClicksBadgeColor = (clicks: number) => {
    if (clicks === 0) {
      return "bg-slate-100 text-slate-600 dark:bg-slate-900 dark:text-slate-400 border border-slate-200 dark:border-slate-800";
    }
    if (clicks < 10) {
      return "bg-blue-50 text-blue-700 border border-blue-100 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/30";
    }
    if (clicks < 100) {
      return "bg-amber-50 text-amber-700 border border-amber-100 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/30";
    }
    return "bg-emerald-50 text-emerald-700 border border-emerald-100 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/30";
  };

  return (
    <div className="flex flex-col flex-1 bg-zinc-50/50 dark:bg-black/50 font-sans w-full min-h-[calc(100vh-64px)] py-8 px-4 md:px-8">
      <div className="max-w-7xl w-full mx-auto space-y-6">
        {/* Header section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-left space-y-1">
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-950 dark:text-zinc-50">
              Link Analytics
            </h1>
            <p className="text-sm text-muted-foreground">
              Monitor short URL click rates, target platforms, and active click
              sessions.
            </p>
          </div>

          {/* Search bar */}
          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search links..."
              className="h-10 w-full pl-9 pr-4 rounded-xl border border-slate-200 bg-white text-sm text-slate-900 shadow-none placeholder:text-slate-400 focus:outline-none focus:border-slate-400"
            />
          </div>
        </div>

        {/* Table layout card */}
        <Card className="border border-border/60 rounded-3xl overflow-hidden shadow-sm bg-white dark:bg-card">
          <div className="w-full overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="border-b border-border/50 bg-slate-50/50 dark:bg-slate-900/10 text-xs font-bold text-muted-foreground uppercase select-none">
                  <th className="py-4 px-6">Link Details</th>
                  <th className="py-4 px-6">Destination</th>
                  <th className="py-4 px-6">Platform</th>
                  <th className="py-4 px-6">Clicks</th>
                  <th className="py-4 px-6">Date Created</th>
                  <th className="py-4 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30 text-sm text-foreground">
                {isLoadingLinks ? (
                  Array.from({ length: 5 }).map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td className="py-4.5 px-6">
                        <div className="h-4 bg-slate-100 dark:bg-slate-900 rounded-md w-36"></div>
                      </td>
                      <td className="py-4.5 px-6">
                        <div className="h-4 bg-slate-100 dark:bg-slate-900 rounded-md w-48"></div>
                      </td>
                      <td className="py-4.5 px-6">
                        <div className="h-6 bg-slate-100 dark:bg-slate-900 rounded-full w-20"></div>
                      </td>
                      <td className="py-4.5 px-6">
                        <div className="h-6 bg-slate-100 dark:bg-slate-900 rounded-full w-14"></div>
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
                      colSpan={6}
                      className="text-center py-16 text-muted-foreground space-y-3"
                    >
                      <div className="inline-flex items-center justify-center size-12 rounded-full bg-slate-50">
                        <Search className="size-6 text-muted-foreground/60" />
                      </div>
                      <p className="text-sm font-semibold text-slate-800">
                        No short links found
                      </p>
                      <p className="text-xs max-w-[240px] mx-auto">
                        Create a link or adjust your search to view analytics.
                      </p>
                    </td>
                  </tr>
                ) : (
                  filteredLinks.map((link) => {
                    const fullShortUrl = `${REDIRECT_DOMAIN}/${link.short_url}`;
                    const platformTag =
                      link.tags
                        ?.find((t) => t.startsWith("platform:"))
                        ?.split(":")[1] || "web";

                    const dateCreated = new Date(
                      link.created_at,
                    ).toLocaleDateString(undefined, {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    });

                    return (
                      <tr
                        key={link.uuid}
                        className="hover:bg-slate-50/30 dark:hover:bg-slate-900/10 transition-colors"
                      >
                        {/* Link Details */}
                        <td className="py-4 px-6 text-left max-w-[200px]">
                          <div className="flex flex-col gap-1">
                            <span
                              className="font-bold text-slate-900 dark:text-zinc-50 truncate"
                              title={link.title || "Untitled Link"}
                            >
                              {link.title || ""}
                            </span>
                            <div className="flex items-center gap-1.5">
                              <span className="text-xs font-semibold text-primary font-mono select-all truncate max-w-[140px]">
                                {link.short_url}
                              </span>
                              <button
                                onClick={() => copyToClipboard(fullShortUrl)}
                                className="text-muted-foreground hover:text-foreground hover:cursor-pointer p-0.5"
                                title="Copy short link"
                              >
                                <Copy className="size-3" />
                              </button>
                            </div>
                          </div>
                        </td>

                        {/* Destination */}
                        <td className="py-4 px-6 text-left max-w-[240px]">
                          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <span
                              className="truncate max-w-[200px]"
                              title={link.destination_url}
                            >
                              {link.destination_url}
                            </span>
                            <a
                              href={link.destination_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-muted-foreground hover:text-foreground"
                            >
                              <ExternalLink className="size-3" />
                            </a>
                          </div>
                        </td>

                        {/* Platform */}
                        <td className="py-4 px-6 text-left">
                          <span
                            className={cn(
                              "text-[11px] font-semibold border rounded-full px-2.5 py-0.5 capitalize",
                              getPlatformBadgeColor(platformTag),
                            )}
                          >
                            {platformTag}
                          </span>
                        </td>

                        {/* Clicks */}
                        <td className="py-4 px-6 text-left">
                          <span
                            className={cn(
                              "text-[11px] font-semibold px-2.5 py-0.5 rounded-full capitalize",
                              getClicksBadgeColor(link.total_clicks),
                            )}
                          >
                            {link.total_clicks} clicks
                          </span>
                        </td>

                        {/* Date Created */}
                        <td className="py-4 px-6 text-left text-xs text-muted-foreground font-medium">
                          {dateCreated}
                        </td>

                        {/* Actions Dropdown */}
                        <td className="py-4 px-6 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon-sm"
                                className="size-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-slate-100"
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
        </Card>
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
