"use client";

import { useEffect, useState } from "react";
import { SearchIcon, Settings, User, LogOut, Moon, Sun } from "lucide-react";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
} from "@/shared/components/ui/command";

interface NavbarSearchProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  onThemeToggle: () => void;
}

export function NavbarSearch({
  isOpen,
  setIsOpen,
  onThemeToggle,
}: NavbarSearchProps) {
  const [platform, setPlatform] = useState("⌘K");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const isMac = navigator.userAgent.toLowerCase().includes("mac");
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPlatform(isMac ? "⌘K" : "Ctrl+K");
    }
  }, []);

  return (
    <>
      <div
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 w-72 md:w-80 h-9 rounded-2xl border px-3 cursor-pointer  transition-all duration-200 select-none"
      >
        <SearchIcon className="w-4 h-4 text-muted-foreground/60 shrink-0" />
        <span className="text-sm text-muted-foreground/60 flex-1 text-left">
          Search...
        </span>
        <kbd className="hidden sm:inline-flex h-5.5 select-none items-center gap-0.5 rounded-lg border border-border/60 bg-background px-1.5 font-mono text-[10px] font-semibold text-muted-foreground shadow-sm">
          {platform}
        </kbd>
      </div>

      <CommandDialog
        open={isOpen}
        onOpenChange={setIsOpen}
        title="Search Dashboard"
        description="Search dashboard shortcuts and actions"
      >
        <CommandInput placeholder="Type a command or search..." />
        <CommandList className="p-2">
          <CommandEmpty>No results found.</CommandEmpty>
          <CommandGroup heading="Suggestions">
            <CommandItem
              onSelect={() => {
                setIsOpen(false);
                alert("Navigating to Profile...");
              }}
            >
              <User className="mr-2 h-4 w-4" />
              <span>Go to Profile</span>
            </CommandItem>
            <CommandItem
              onSelect={() => {
                setIsOpen(false);
                alert("Navigating to Settings...");
              }}
            >
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings & Preferences</span>
            </CommandItem>
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="System Actions">
            <CommandItem
              onSelect={() => {
                setIsOpen(false);
                onThemeToggle();
              }}
            >
              <Sun className="mr-2 h-4 w-4 dark:hidden" />
              <Moon className="mr-2 h-4 w-4 hidden dark:block" />
              <span>Toggle Theme (Light / Dark)</span>
            </CommandItem>
            <CommandItem
              onSelect={() => {
                setIsOpen(false);
                alert("Logging out...");
              }}
            >
              <LogOut className="mr-2 h-4 w-4 text-destructive" />
              <span className="text-destructive">Logout</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}
