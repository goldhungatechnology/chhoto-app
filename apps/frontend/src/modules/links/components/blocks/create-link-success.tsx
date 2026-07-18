"use client";

import * as React from "react";
import { Check, Copy, ExternalLink } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { LinkData } from "../../types";
import { REDIRECT_DOMAIN } from "@/core/config";

interface CreateLinkSuccessProps {
  createdLink: LinkData;
  onCreateAnother: () => void;
}

export function CreateLinkSuccess({
  createdLink,
  onCreateAnother,
}: CreateLinkSuccessProps) {
  const [copied, setCopied] = React.useState(false);

  const fullShortUrl = `${REDIRECT_DOMAIN}/${createdLink.short_url}`;
  const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
    fullShortUrl,
  )}&color=7c3aed`; // Purple color matching primary

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

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
        <div className="flex items-center justify-between gap-3 w-full  border border-border/80 rounded-2xl p-4 mt-2">
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
        <div className="w-full text-left border border-border/40 rounded-2xl p-4 text-xs space-y-2 mt-2">
          <div className="flex justify-between border-b border-border/40 pb-2">
            <span className="">Title</span>
            <span className="font-medium text-foreground">
              {createdLink.title || ""}
            </span>
          </div>
          <div className="flex justify-between border-b border-border/40 pb-2">
            <span className="">Original Destination</span>
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
            onClick={onCreateAnother}
          >
            Create Another Link
          </Button>
        </div>
      </div>
    </Card>
  );
}
