"use client";

import * as React from "react";
import { useWatch } from "react-hook-form";
import {
  Globe,
  Megaphone,
  MoreHorizontal,
  Type,
  Link2,
  Zap,
  QrCode,
  Clock,
  Copy,
  Check,
  ExternalLink,
} from "lucide-react";

// Inline SVG Icons for social platforms that are missing or compile differently in this Lucide version
const InstagramIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
    <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
  </svg>
);

const YoutubeIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z" />
    <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" />
  </svg>
);

const TiktokIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5-5" />
  </svg>
);

import { cn } from "@/lib/utils";
import { Input } from "@/shared/components/ui/input";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/shared/components/ui/input-group";
import { Field, FieldLabel, FieldError } from "@/shared/components/ui/field";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { PlatformCard } from "../primitives/platform-card";
import { useCreateLinkForm } from "../../hooks/use-create-link-form";
import { PlatformCategory, LinkData } from "../../types";

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

export function CreateLinkCard() {
  const [createdLink, setCreatedLink] = React.useState<LinkData | null>(null);
  const [copied, setCopied] = React.useState(false);

  const handleSuccess = (data: LinkData) => {
    setCreatedLink(data);
  };

  const { methods, onSubmit, isSubmitting, resetForm } =
    useCreateLinkForm(handleSuccess);
  const {
    register,
    control,
    setValue,
    formState: { errors },
  } = methods;

  // Watch fields for dynamic visibility and layout changes
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

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  const handleCreateAnother = () => {
    setCreatedLink(null);
    resetForm();
  };

  // Render the Success State
  if (createdLink) {
    const fullShortUrl = `${window.location.origin.replace("3000", "8000")}/api/v1/links/redirect/${createdLink.short_url}`;
    const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
      fullShortUrl,
    )}&color=7c3aed`; // Purple color matching primary

    return (
      <Card className="w-full max-w-xl bg-card border border-border/60 shadow-2xl p-8 rounded-4xl animate-in fade-in zoom-in-95 duration-350">
        <div className="flex flex-col items-center text-center gap-6">
          <div className="flex items-center justify-center size-14 rounded-full bg-emerald-500/10 text-emerald-500 animate-bounce">
            <Check className="size-7" />
          </div>

          <div className="space-y-2">
            <h3 className="text-2xl font-bold tracking-tight text-foreground">
              Short Link Created!
            </h3>
            <p className="text-sm text-muted-foreground">
              Your shortened URL is ready. Share it anywhere.
            </p>
          </div>

          {/* Copy link Box */}
          <div className="flex items-center justify-between gap-3 w-full bg-muted/30 border border-border/80 rounded-2xl p-4 mt-2">
            <span className="text-sm font-semibold truncate text-primary font-mono text-left select-all">
              {fullShortUrl}
            </span>
            <Button
              size="sm"
              variant="outline"
              className="rounded-xl flex items-center gap-1.5 shrink-0 bg-background"
              onClick={() => copyToClipboard(fullShortUrl)}
            >
              {copied ? (
                <>
                  <Check className="size-3.5 text-emerald-500" />
                  <span className="text-emerald-500">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="size-3.5" />
                  <span>Copy</span>
                </>
              )}
            </Button>
          </div>

          {/* Optional QR Code Display */}
          {createdLink.generateQr && (
            <div className="flex flex-col items-center gap-4 w-full bg-primary-soft/5 dark:bg-primary-soft/3 border border-primary-border/20 rounded-3xl p-6 animate-in slide-in-from-bottom-4 duration-300">
              <div className="bg-white p-3 rounded-2xl shadow-md ring-1 ring-black/5 dark:ring-white/10">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={qrImageUrl}
                  alt="QR Code"
                  className="size-40 object-contain"
                />
              </div>
              <div className="text-center space-y-1">
                <p className="text-xs font-semibold text-primary uppercase tracking-wider">
                  Dynamic QR Code
                </p>
                <p className="text-xs text-muted-foreground">
                  Scan this code to redirect to your destination url.
                </p>
              </div>
              <Button
                variant="link"
                size="sm"
                className="text-xs font-semibold flex items-center gap-1 hover:text-primary-hover"
                asChild
              >
                <a href={qrImageUrl} target="_blank" rel="noopener noreferrer">
                  <span>Open QR Code Image</span>
                  <ExternalLink className="size-3" />
                </a>
              </Button>
            </div>
          )}

          {/* Details Table */}
          <div className="w-full text-left bg-muted/15 border border-border/40 rounded-2xl p-4 text-xs space-y-2 mt-2">
            <div className="flex justify-between border-b border-border/40 pb-2">
              <span className="text-muted-foreground">Title</span>
              <span className="font-medium text-foreground">
                {createdLink.title || "Untitled Link"}
              </span>
            </div>
            <div className="flex justify-between border-b border-border/40 pb-2">
              <span className="text-muted-foreground">
                Original Destination
              </span>
              <span className="font-medium text-foreground truncate max-w-[250px]">
                {createdLink.destination_url}
              </span>
            </div>
            {createdLink.auto_expire && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Auto Expires At</span>
                <span className="font-medium text-foreground">
                  {new Date(createdLink.auto_expire).toLocaleString()}
                </span>
              </div>
            )}
          </div>

          <div className="flex gap-3 w-full mt-4">
            <Button
              className="flex-1 rounded-2xl bg-primary hover:bg-primary-hover text-white py-5"
              onClick={handleCreateAnother}
            >
              Create Another Link
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  // Form State
  return (
    <Card className="w-full max-w-xl bg-card border border-border/60 shadow-xl p-8 rounded-4xl">
      <form onSubmit={onSubmit} className="flex flex-col gap-6">
        {/* LINK TITLE */}
        <Field>
          <FieldLabel
            htmlFor="link-title"
            className="text-xs font-bold tracking-wider text-muted-foreground/80 uppercase"
          >
            Link Title
          </FieldLabel>
          <InputGroup>
            <InputGroupAddon align="inline-start">
              <Type className="size-4 text-muted-foreground/75" />
            </InputGroupAddon>
            <InputGroupInput
              id="link-title"
              placeholder="e.g., Summer Campaign Launch"
              {...register("title")}
            />
          </InputGroup>
          {errors.title && <FieldError>{errors.title.message}</FieldError>}
        </Field>

        {/* DESTINATION URL */}
        <Field>
          <FieldLabel
            htmlFor="destination-url"
            className="text-xs font-bold tracking-wider text-muted-foreground/80 uppercase"
          >
            Destination URL
          </FieldLabel>
          <InputGroup>
            <InputGroupAddon align="inline-start">
              <Link2 className="size-4 text-muted-foreground/75" />
            </InputGroupAddon>
            <InputGroupInput
              id="destination-url"
              placeholder="https://example.com/your-long-campaign-url"
              {...register("url")}
            />
          </InputGroup>
          {errors.url && <FieldError>{errors.url.message}</FieldError>}
        </Field>

        {/* CUSTOM SHORT SLUG */}
        <Field>
          <FieldLabel
            htmlFor="custom-slug"
            className="text-xs font-bold tracking-wider text-muted-foreground/80 uppercase"
          >
            Custom Slug (Optional)
          </FieldLabel>
          <InputGroup>
            <InputGroupAddon align="inline-start">
              <span className="text-xs font-semibold text-muted-foreground/85">
                chhoto.xyz/
              </span>
            </InputGroupAddon>
            <InputGroupInput
              id="custom-slug"
              placeholder="my-campaign"
              {...register("customSlug")}
            />
          </InputGroup>
          {errors.customSlug && (
            <FieldError>{errors.customSlug.message}</FieldError>
          )}
        </Field>

        {/* PLATFORM CATEGORY */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-bold tracking-wider text-muted-foreground/80 uppercase select-none">
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

        {/* TOGGLE OPTIONS */}
        <div className="grid grid-cols-2 gap-4 mt-2">
          {/* Generate QR */}
          <div className="flex items-start justify-between border border-border/70 rounded-2xl p-4 bg-muted/10 hover:bg-muted/20 transition-all duration-200">
            <div className="flex gap-3">
              <div className="p-2 rounded-xl bg-primary-soft/10 text-primary">
                <QrCode className="size-4.5" />
              </div>
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-foreground">
                  Generate QR
                </h4>
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
          <div className="flex items-start justify-between border border-border/70 rounded-2xl p-4 bg-muted/10 hover:bg-muted/20 transition-all duration-200">
            <div className="flex gap-3">
              <div className="p-2 rounded-xl bg-primary-soft/10 text-primary">
                <Clock className="size-4.5" />
              </div>
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-foreground">
                  Auto-Expire
                </h4>
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

        {/* Conditional Expiry Date Picker */}
        {isExpireEnabled && (
          <div className="animate-in fade-in slide-in-from-top-3 duration-250">
            <Field>
              <FieldLabel
                htmlFor="expiry-date"
                className="text-xs font-bold tracking-wider text-muted-foreground/80 uppercase"
              >
                Expiry Date & Time
              </FieldLabel>
              <Input
                id="expiry-date"
                type="datetime-local"
                className="rounded-2xl"
                {...register("expiryDate")}
              />
              {errors.expiryDate && (
                <FieldError>{errors.expiryDate.message}</FieldError>
              )}
            </Field>
          </div>
        )}

        {/* CREATE BUTTON */}
        <Button
          type="submit"
          className={cn(
            "w-full rounded-2xl bg-primary py-6 text-base font-semibold text-white shadow-lg shadow-primary/10 transition-all hover:bg-primary-hover hover:scale-[1.01] hover:shadow-primary/20",
            isSubmitting && "opacity-70 pointer-events-none",
          )}
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Creating...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <span>Create Short Link</span>
              <Zap className="size-4 fill-white" />
            </div>
          )}
        </Button>

        {/* Disclaimers */}
        <p className="text-[11px] text-center text-muted-foreground">
          By creating a link, you agree to our{" "}
          <a
            href="#"
            className="underline hover:text-primary transition-colors"
          >
            Terms of Service
          </a>{" "}
          and Privacy Policy.
        </p>
      </form>
    </Card>
  );
}
