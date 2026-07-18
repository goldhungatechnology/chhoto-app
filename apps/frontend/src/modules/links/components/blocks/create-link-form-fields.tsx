"use client";

import * as React from "react";
import { useFormContext, useWatch } from "react-hook-form";
import { Globe, Megaphone, MoreHorizontal, QrCode, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { Field } from "@/shared/components/custom/form";
import {
  PlatformCard,
  InstagramIcon,
  YoutubeIcon,
  TiktokIcon,
} from "../primitives";
import { PlatformCategory } from "../../types";

// Clean Switch component
function SwitchToggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
        checked ? "bg-primary" : "bg-muted-foreground/30",
      )}
    >
      <span
        className={cn(
          "pointer-events-none block h-4 w-4 rounded-full bg-background shadow-sm ring-0 transition duration-200 ease-in-out",
          checked ? "translate-x-4" : "translate-x-0",
        )}
      />
    </button>
  );
}

export function CreateLinkFormFields() {
  const { control, setValue } = useFormContext();

  const selectedPlatform = useWatch({ control, name: "platform" });
  const isQrEnabled = useWatch({ control, name: "generateQr" });
  const isExpireEnabled = useWatch({ control, name: "autoExpire" });

  const platforms: {
    id: PlatformCategory;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }[] = [
    { id: "web", label: "Web", icon: Globe },
    { id: "instagram", label: "Instagram", icon: InstagramIcon },
    { id: "youtube", label: "YouTube", icon: YoutubeIcon },
    { id: "tiktok", label: "TikTok", icon: TiktokIcon },
    { id: "ads", label: "Ads", icon: Megaphone },
    { id: "other", label: "Other", icon: MoreHorizontal },
  ];

  const commonInputStyles =
    "h-11 w-full rounded-xl border-slate-200 bg-white text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0";

  return (
    <>
      {/* LINK TITLE */}
      <Field.Input
        name="title"
        label="Link Title"
        placeholder="e.g., Summer Campaign Launch"
        inputClassName={commonInputStyles}
      />

      {/* DESTINATION URL */}
      <Field.Input
        name="url"
        label="Destination URL"
        placeholder="https://example.com/your-long-campaign-url"
        inputClassName={commonInputStyles}
      />

      {/* PLATFORM CATEGORY */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium leading-none text-slate-900 select-none">
          Platform Category
        </label>
        <div className="grid grid-cols-3 gap-3">
          {platforms.map((platform) => (
            <PlatformCard
              key={platform.id}
              label={platform.label}
              icon={platform.icon}
              selected={selectedPlatform === platform.id}
              onClick={() => setValue("platform", platform.id)}
            />
          ))}
        </div>
      </div>

      {/* Conditional Custom Platform Input */}
      {selectedPlatform === "other" && (
        <div className="animate-in fade-in slide-in-from-top-3 duration-250">
          <Field.Input
            name="customPlatform"
            label="Platform Name"
            placeholder="e.g., LinkedIn, Pinterest"
            inputClassName={commonInputStyles}
          />
        </div>
      )}

      {/* TOGGLE OPTIONS */}
      <div className="grid grid-cols-2 gap-4 mt-2">
        {/* Generate QR */}
        <div className="flex items-start justify-between border border-slate-200 rounded-2xl p-4 bg-white hover:bg-slate-50/50 transition-all duration-200">
          <div className="flex gap-3">
            <div className="p-2 rounded-xl bg-primary-soft/10 text-primary">
              <QrCode className="size-4.5" />
            </div>
            <div className="space-y-0.5">
              <h4 className="text-xs font-bold text-foreground">Generate QR</h4>
              <p className="text-[10px] leading-tight text-muted-foreground">
                Create a dynamic QR code for print.
              </p>
            </div>
          </div>
          <SwitchToggle
            checked={isQrEnabled || false}
            onChange={(val) => setValue("generateQr", val)}
          />
        </div>

        {/* Auto Expire */}
        <div className="flex items-start justify-between border border-slate-200 rounded-2xl p-4 bg-white hover:bg-slate-50/50 transition-all duration-200">
          <div className="flex gap-3">
            <div className="p-2 rounded-xl bg-primary-soft/10 text-primary">
              <Clock className="size-4.5" />
            </div>
            <div className="space-y-0.5">
              <h4 className="text-xs font-bold text-foreground">Auto-Expire</h4>
              <p className="text-[10px] leading-tight text-muted-foreground">
                Set a date for this link to deactivate.
              </p>
            </div>
          </div>
          <SwitchToggle
            checked={isExpireEnabled || false}
            onChange={(val) => setValue("autoExpire", val)}
          />
        </div>
      </div>

      {/* Conditional Expiry Date & Time Picker */}
      {isExpireEnabled && (
        <div className="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-3 duration-250">
          <Field.Input
            name="expiryDate"
            label="Expiry Date"
            type="date"
            inputClassName={commonInputStyles}
          />
          <Field.Input
            name="expiryTime"
            label="Expiry Time"
            type="time"
            inputClassName={commonInputStyles}
          />
        </div>
      )}
    </>
  );
}
