"use client";

import { NavbarSearch } from "./navbar-search";
import { NavbarThemeToggle } from "./navbar-theme-toggle";
import { NavbarProfile } from "./navbar-profile";
import { useNavbar } from "@/shared/hooks/use-navbar";
import { SidebarTrigger } from "@/shared/components/ui/sidebar";

export function Navbar() {
  const { toggleTheme, isCommandOpen, setIsCommandOpen, user, userLoading } =
    useNavbar();

  if (!user || userLoading) {
    return <div>Loading</div>;
  }

  return (
    <header className="sticky top-0 z-40 w-full h-16 border-b border-border/40 bg-card px-4 sm:px-6 flex items-center justify-between transition-colors duration-200">
      <SidebarTrigger />

      <div className="hidden md:flex flex-1 justify-center max-w-lg px-4">
        <NavbarSearch
          isOpen={isCommandOpen}
          setIsOpen={setIsCommandOpen}
          onThemeToggle={toggleTheme}
        />
      </div>

      <div className="flex items-center gap-3">
        <NavbarThemeToggle onToggle={toggleTheme} />
        <NavbarProfile user={user} />
      </div>
    </header>
  );
}
