"use client";

import * as React from "react";
import { Download, Copy, Check, ShieldAlert } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { MfaRecoveryCodeCard } from "../primitives";
import { toast } from "@/shared/components/custom/snackbar";

interface MfaRecoveryCodesProps {
  codes: string[];
}

export function MfaRecoveryCodes({ codes }: MfaRecoveryCodesProps) {
  const [copied, setCopied] = React.useState(false);

  const displayCodes = codes;

  const handleCopyAll = async () => {
    try {
      await navigator.clipboard.writeText(displayCodes.join("\n"));
      setCopied(true);
      toast.success("Recovery codes copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy recovery codes");
    }
  };

  const handleDownload = () => {
    const content = `CHHOTO APP - MFA RECOVERY CODES\nGenerated at: ${new Date().toISOString()}\n\nKeep these codes in a secure place:\n\n${displayCodes.join(
      "\n"
    )}\n\nEach code can only be used once.`;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "chhoto-recovery-codes.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Recovery codes downloaded");
  };

  if (!displayCodes || displayCodes.length === 0) {
    return null;
  }

  return (
    <div className="p-5 rounded-3xl bg-slate-50/70 dark:bg-zinc-900/50 border border-slate-200/80 dark:border-zinc-800 space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h4 className="font-bold text-slate-950 dark:text-zinc-50 text-sm flex items-center gap-2">
            <ShieldAlert className="size-4 text-purple-600 dark:text-purple-400" />
            <span>Recovery Codes</span>
          </h4>
          <p className="text-xs text-muted-foreground mt-0.5">
            Save these codes in a secure place. They can be used to access your account if you lose your phone.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleCopyAll}
            className="h-8 px-3 text-xs border-slate-200 dark:border-zinc-700 hover:bg-slate-100 dark:hover:bg-zinc-800 rounded-xl"
          >
            {copied ? <Check className="size-3.5 mr-1 text-emerald-500" /> : <Copy className="size-3.5 mr-1" />}
            <span>{copied ? "Copied" : "Copy Codes"}</span>
          </Button>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleDownload}
            className="h-8 px-3 text-xs text-primary border-primary/30 hover:bg-primary/5 rounded-xl flex items-center gap-1.5"
          >
            <Download className="size-3.5" />
            <span>Download</span>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {displayCodes.map((code, idx) => (
          <MfaRecoveryCodeCard key={idx} code={code} />
        ))}
      </div>
    </div>
  );
}
