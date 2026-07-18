"use client";

import * as React from "react";
import { FormProvider } from "react-hook-form";
import {
  User,
  Mail,
  ShieldCheck,
  Save,
  UserCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Field } from "@/shared/components/custom/form";
import { useProfileForm } from "../hooks";
import { Avatar, AvatarFallback, AvatarImage } from "@/shared/components/ui/avatar";

const AVATAR_PRESETS = [
  { name: "Sky Blue", color: "0284c7" },
  { name: "Violet", color: "7c3aed" },
  { name: "Rose", color: "e11d48" },
  { name: "Amber", color: "d97706" },
  { name: "Emerald", color: "059669" },
  { name: "Slate", color: "475569" },
];

export function ProfileView() {
  const { methods, onSubmit, isSubmitting, user, isLoadingUser } = useProfileForm();
  const { watch, setValue, register } = methods;

  React.useEffect(() => {
    register("avatar");
    register("avatarBg");
  }, [register]);

  const currentAvatar = watch("avatar");
  const currentAvatarBg = watch("avatarBg");
  const fullNameValue = watch("fullName");

  const selectPreset = (colorCode: string) => {
    setValue("avatarBg", `#${colorCode}`, { shouldDirty: true });
    setValue("avatar", null, { shouldDirty: true });
  };

  const commonInputStyles =
    "h-11 rounded-xl border border-slate-200 bg-white px-3.5 text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0 focus-visible:ring-offset-0 disabled:opacity-60 disabled:cursor-not-allowed dark:border-slate-800 dark:bg-zinc-950 dark:text-zinc-50 dark:focus-visible:border-slate-500";

  if (isLoadingUser) {
    return (
      <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50/50 dark:bg-black/50 font-sans w-full min-h-[calc(100vh-64px)] py-8 px-4">
        <div className="animate-pulse space-y-6 max-w-7xl w-full">
          <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded-md w-1/4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-4 h-64 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>
            <div className="lg:col-span-8 h-96 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 bg-zinc-50/50 dark:bg-black/50 font-sans w-full min-h-[calc(100vh-64px)] py-8 px-4 md:px-8">
      <div className="max-w-7xl w-full mx-auto space-y-6">
        {/* Header section */}
        <div className="text-left space-y-1">
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-950 dark:text-zinc-50">
            Account Settings
          </h1>
          <p className="text-sm text-muted-foreground">
            Update your personal details, avatar presets, and manage contact info.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Avatar & Quick Info Card */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <Card className="border border-border/60 rounded-3xl p-6 bg-white dark:bg-card flex flex-col items-center text-center gap-5 shadow-sm">
              <div className="relative">
                <Avatar className="size-24 border border-border shadow-sm">
                  {currentAvatar && <AvatarImage src={currentAvatar} />}
                  <AvatarFallback
                    className="text-white text-2xl font-bold"
                    style={{ backgroundColor: currentAvatarBg || user?.avatar_bg || "var(--primary)" }}
                  >
                    {(fullNameValue || user?.full_name || "C").split("")[0]}
                  </AvatarFallback>
                </Avatar>
                <div className="absolute -bottom-1 -right-1 bg-emerald-500 border-2 border-white dark:border-zinc-900 rounded-full p-1.5 text-white">
                  <ShieldCheck className="size-4" />
                </div>
              </div>

              <div className="space-y-1">
                <h3 className="font-bold text-slate-950 dark:text-zinc-50 text-base">
                  {fullNameValue || user?.full_name || "Your Name"}
                </h3>
                <p className="text-xs text-muted-foreground font-mono bg-slate-50 dark:bg-slate-900/40 border border-border/40 px-2 py-0.5 rounded-full inline-block">
                  @{user?.username || "username"}
                </p>
              </div>

              {/* Avatar Preset Customizer */}
              <div className="w-full border-t border-border/40 pt-4 text-left space-y-2.5">
                <label className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider select-none">
                  Avatar Theme Presets
                </label>
                <div className="grid grid-cols-6 gap-2">
                  {AVATAR_PRESETS.map((preset) => {
                    const isActive = currentAvatarBg === `#${preset.color}`;

                    return (
                      <button
                        key={preset.color}
                        type="button"
                        onClick={() => selectPreset(preset.color)}
                        className={cn(
                          "size-8 rounded-full border border-border/40 transition-all duration-200 hover:scale-105 hover:cursor-pointer flex items-center justify-center relative",
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
            </Card>
          </div>

          {/* Right Column: Profile Edit Form */}
          <div className="lg:col-span-8">
            <Card className="border border-border/60 rounded-3xl p-6 bg-white dark:bg-card shadow-sm">
              <FormProvider {...methods}>
                <form onSubmit={onSubmit} className="space-y-6 text-left">
                  <div className="border-b border-border/40 pb-4 mb-4">
                    <h2 className="text-lg font-bold text-slate-950 dark:text-zinc-50">
                      Personal Details
                    </h2>
                    <p className="text-xs text-muted-foreground">
                      Edit your account details. Verified identifiers like email are read-only.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Full Name */}
                    <div className="space-y-1.5">
                      <Field.Input
                        name="fullName"
                        label="Full Name"
                        placeholder="John Doe"
                        inputClassName={commonInputStyles}
                      />
                    </div>

                    {/* Phone Number */}
                    <div className="space-y-1.5">
                      <Field.Input
                        name="phoneNumber"
                        label="Phone Number"
                        placeholder="+1 (555) 000-0000"
                        inputClassName={commonInputStyles}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Username (Disabled) */}
                    <div className="space-y-1.5 relative">
                      <label className="text-xs font-semibold text-muted-foreground select-none flex items-center gap-1">
                        <User className="size-3 text-muted-foreground/60" />
                        Username
                      </label>
                      <input
                        type="text"
                        disabled
                        value={user?.username || ""}
                        className={cn(commonInputStyles, "w-full cursor-not-allowed")}
                      />
                      <span className="absolute right-3.5 bottom-3.5 text-[10px] font-mono text-muted-foreground/50 bg-slate-50 px-1 py-0.5 rounded border border-border/30">
                        ReadOnly
                      </span>
                    </div>

                    {/* Email (Disabled) */}
                    <div className="space-y-1.5 relative">
                      <label className="text-xs font-semibold text-muted-foreground select-none flex items-center gap-1">
                        <Mail className="size-3 text-muted-foreground/60" />
                        Email Address
                      </label>
                      <input
                        type="text"
                        disabled
                        value={user?.email || ""}
                        className={cn(commonInputStyles, "w-full cursor-not-allowed")}
                      />
                      <div className="absolute right-3.5 bottom-3 flex items-center gap-1 px-1.5 py-0.5 rounded border border-emerald-100 bg-emerald-50 text-[10px] font-medium text-emerald-700">
                        <ShieldCheck className="size-3.5" />
                        <span>Verified</span>
                      </div>
                    </div>
                  </div>

                  {/* Submit buttons */}
                  <div className="flex justify-end gap-3 pt-4 border-t border-border/40 mt-6">
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="rounded-xl h-11 px-5 bg-primary text-white hover:bg-primary-hover flex items-center gap-2 hover:cursor-pointer shadow-sm"
                    >
                      <Save className="size-4" />
                      <span>{isSubmitting ? "Saving Changes..." : "Save Changes"}</span>
                    </Button>
                  </div>
                </form>
              </FormProvider>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
