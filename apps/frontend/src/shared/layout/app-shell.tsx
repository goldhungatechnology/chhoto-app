"use client";

import * as React from "react";
import { Navbar } from "@/shared/layout/navbar";
import { AppSidebar } from "@/shared/layout/sidebar/sidebar";
import { SettingsPanel } from "@/shared/layout/sidebar/settings-panel";

export function AppShell({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [settingsOpen, setSettingsOpen] = React.useState(false);

  return (
    <>
      <AppSidebar onOpenSettings={() => setSettingsOpen(true)} />
      <SettingsPanel open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <div className="flex flex-col w-full">
        <Navbar />
        {children}
      </div>
    </>
  );
}
