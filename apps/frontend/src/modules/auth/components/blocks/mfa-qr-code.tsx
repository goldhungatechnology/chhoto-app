"use client";

import * as React from "react";
import QRCode from "qrcode";
import { Copy, Check } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { toast } from "@/shared/components/custom/snackbar";

interface MfaQrCodeProps {
  authUrl: string;
  secret: string;
}

export function MfaQrCode({ authUrl, secret }: MfaQrCodeProps) {
  const [copied, setCopied] = React.useState(false);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  React.useEffect(() => {
    if (!canvasRef.current) return;
    const text = authUrl || secret;
    if (!text) return;

    let cancelled = false;
    QRCode.toCanvas(canvasRef.current, text, {
      width: 192,
      margin: 2,
      color: {
        dark: "#0F172A",
        light: "#FFFFFF",
      },
      errorCorrectionLevel: "M",
    }).catch(() => {
      if (!cancelled) {
        toast.error("Failed to generate QR code. Use the secret key below instead.");
      }
    });

    return () => {
      cancelled = true;
    };
  }, [authUrl, secret]);

  const copySecret = async () => {
    try {
      await navigator.clipboard.writeText(secret);
      setCopied(true);
      toast.success("Secret key copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy secret key");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="size-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">
          1
        </div>
        <h4 className="font-bold text-slate-900 dark:text-zinc-100 text-sm">
          Scan QR Code
        </h4>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">
        Open your authenticator app (like Google Authenticator or Authy) and scan the QR code below to link your account.
      </p>

      {/* Styled QR container */}
      <div className="flex flex-col items-center justify-center p-4 rounded-2xl border border-slate-200/80 dark:border-zinc-800 bg-slate-50/50 dark:bg-zinc-900/50 space-y-3">
        <div className="size-48 p-2 rounded-xl bg-white shadow-sm border border-slate-200/60 dark:border-zinc-700 flex items-center justify-center">
          <canvas ref={canvasRef} className="size-44" />
        </div>

        {/* Secret Key manual entry container */}
        <div className="w-full max-w-xs flex items-center justify-between gap-2 px-3 py-1.5 rounded-xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs">
          <span className="text-muted-foreground font-mono text-[11px] truncate">
            {secret}
          </span>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={copySecret}
            className="h-7 px-2 text-[11px] text-primary hover:text-primary-hover hover:bg-primary/10 rounded-lg shrink-0"
          >
            {copied ? (
              <Check className="size-3.5 mr-1 text-emerald-500" />
            ) : (
              <Copy className="size-3.5 mr-1" />
            )}
            <span>{copied ? "Copied" : "Copy"}</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
