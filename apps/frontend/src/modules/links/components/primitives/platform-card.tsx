import * as React from "react";
import { cn } from "@/lib/utils";

interface PlatformCardProps {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  selected: boolean;
  onClick: () => void;
}

export function PlatformCard({
  label,
  icon: Icon,
  selected,
  onClick,
}: PlatformCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex flex-col items-center justify-center gap-2.5 rounded-2xl border p-4 text-center transition-all duration-200 cursor-pointer select-none w-full",
        "bg-card/30 border-border hover:border-primary/50 hover:bg-primary-soft/5 hover:scale-[1.02]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40",
        selected &&
          "border-primary bg-primary-soft/20 text-primary dark:bg-primary-soft/10 ring-2 ring-primary/20 font-semibold"
      )}
    >
      <div
        className={cn(
          "flex items-center justify-center p-2 rounded-xl bg-muted/40 transition-colors duration-200",
          selected && "bg-primary/15 text-primary"
        )}
      >
        <Icon className="size-5 transition-transform duration-200" />
      </div>
      <span className="text-xs font-medium tracking-tight text-foreground/95">
        {label}
      </span>
    </button>
  );
}
