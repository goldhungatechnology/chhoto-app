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
        "flex flex-col items-center justify-center gap-1.5 rounded-xl border py-2 px-2 text-center transition-all duration-200 cursor-pointer select-none w-full",
        "bg-white border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50/50 hover:scale-[1.01]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40",
        selected &&
          "border-primary bg-primary-soft/10 text-primary ring-1 ring-primary/10 font-semibold"
      )}
    >
      <div
        className={cn(
          "flex items-center justify-center p-1.5 rounded-lg bg-slate-50 transition-colors duration-200",
          selected && "bg-primary/10 text-primary"
        )}
      >
        <Icon className="size-4.5 transition-transform duration-200" />
      </div>
      <span className="text-[11px] font-medium tracking-tight">
        {label}
      </span>
    </button>
  );
}
