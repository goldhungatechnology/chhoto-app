"use client";

import { Moon, Sun } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

interface NavbarThemeToggleProps {
  onToggle: () => void;
}

export function NavbarThemeToggle({ onToggle }: NavbarThemeToggleProps) {
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={onToggle}
      className="w-10 h-10 rounded-[16px] border border-border/40 bg-card hover:bg-muted/40 shadow-sm transition-all duration-200 cursor-pointer text-foreground/80 hover:text-primary active:scale-95"
      aria-label="Toggle Theme"
    >
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Sun Icon */}
        <Sun className="h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all duration-300 dark:rotate-0 dark:scale-100 absolute" />

        {/* Moon Icon */}
        <Moon className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all duration-300 dark:-rotate-90 dark:scale-0 absolute" />
      </div>
    </Button>
  );
}
