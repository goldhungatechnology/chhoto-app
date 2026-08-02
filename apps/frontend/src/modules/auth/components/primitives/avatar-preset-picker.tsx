"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { UserCheck } from "lucide-react";

export const AVATAR_PRESETS = [
  { name: "Sky Blue", color: "0284c7" },
  { name: "Violet", color: "7c3aed" },
  { name: "Rose", color: "e11d48" },
  { name: "Amber", color: "d97706" },
  { name: "Emerald", color: "059669" },
  { name: "Slate", color: "475569" },
];

interface AvatarPresetPickerProps {
  currentBg?: string | null;
  onSelectPreset: (colorHex: string) => void;
  className?: string;
}

export function AvatarPresetPicker({
  currentBg,
  onSelectPreset,
  className,
}: AvatarPresetPickerProps) {
  return (
    <div className={cn("w-full space-y-2.5", className)}>
      <label className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider select-none">
        Avatar Theme Presets
      </label>
      <div className="grid grid-cols-6 gap-2">
        {AVATAR_PRESETS.map((preset) => {
          const isActive = currentBg === `#${preset.color}`;

          return (
            <button
              key={preset.color}
              type="button"
              onClick={() => onSelectPreset(preset.color)}
              className={cn(
                "size-8 rounded-full border border-border/40 transition-all duration-200 hover:scale-105 hover:cursor-pointer flex items-center justify-center relative focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary",
                isActive ? "ring-2 ring-primary ring-offset-2 dark:ring-offset-zinc-950" : ""
              )}
              style={{ backgroundColor: `#${preset.color}` }}
              title={preset.name}
            >
              {isActive && <UserCheck className="size-3.5 text-white" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
