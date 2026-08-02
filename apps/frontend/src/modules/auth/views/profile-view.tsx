"use client";

import * as React from "react";
import {
  PersonalDetailsSection,
  SessionsSection,
  MfaSettingsSection,
} from "../components/sections";

export function ProfileView() {
  return (
    <div className="flex flex-col flex-1 bg-zinc-50/50 dark:bg-black/50 font-sans w-full min-h-[calc(100vh-64px)] py-8 px-4 md:px-8">
      <div className="max-w-7xl w-full mx-auto space-y-8">
        {/* Header section */}
        <div className="text-left space-y-1">
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-950 dark:text-zinc-50">
            Account Settings
          </h1>
          <p className="text-sm text-muted-foreground">
            Update your personal details, avatar presets, and manage contact info.
          </p>
        </div>

        {/* Top Section: Avatar Presets & Personal Details */}
        <PersonalDetailsSection />

        {/* Middle Section: Sessions */}
        <SessionsSection />

        {/* Bottom Section: Multi-Factor Authentication */}
        <MfaSettingsSection />
      </div>
    </div>
  );
}
