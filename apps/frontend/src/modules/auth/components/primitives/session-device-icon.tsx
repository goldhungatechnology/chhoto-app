"use client";

import * as React from "react";
import { Monitor, Smartphone, Tablet, Laptop, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

interface SessionDeviceIconProps {
  device?: string | null;
  browser?: string | null;
  className?: string;
}

export function SessionDeviceIcon({
  device,
  browser,
  className,
}: SessionDeviceIconProps) {
  const normalized = (
    (device || "") +
    " " +
    (browser || "")
  ).toLowerCase();

  let Icon = Laptop;
  if (normalized.includes("iphone") || normalized.includes("mobile") || normalized.includes("android")) {
    Icon = Smartphone;
  } else if (normalized.includes("ipad") || normalized.includes("tablet")) {
    Icon = Tablet;
  } else if (normalized.includes("mac") || normalized.includes("windows") || normalized.includes("linux")) {
    Icon = Monitor;
  } else if (!device && !browser) {
    Icon = Globe;
  }

  return (
    <div
      className={cn(
        "size-10 rounded-xl bg-slate-100 dark:bg-zinc-800/80 flex items-center justify-center text-slate-700 dark:text-zinc-300 border border-slate-200/60 dark:border-zinc-700/60 shrink-0",
        className
      )}
    >
      <Icon className="size-5" />
    </div>
  );
}
