"use client";

import * as React from "react";
import { Button } from "@/shared/components/ui/button";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/shared/components/ui/input-otp";
import { CheckCircle2, Loader2 } from "lucide-react";

interface MfaOtpInputProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
}

export function MfaOtpInput({
  value,
  onChange,
  onSubmit,
  isSubmitting = false,
}: MfaOtpInputProps) {
  const isComplete = value.length === 6;

  return (
    <div className="space-y-4 flex flex-col justify-between h-full">
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="size-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">
            2
          </div>
          <h4 className="font-bold text-slate-900 dark:text-zinc-100 text-sm">
            Verify Code
          </h4>
        </div>

        <p className="text-xs text-muted-foreground leading-relaxed">
          Enter the 6-digit code from your app to complete the setup.
        </p>

        {/* 6-digit Input OTP */}
        <div className="flex justify-start py-2">
          <InputOTP
            maxLength={6}
            value={value}
            onChange={onChange}
            disabled={isSubmitting}
          >
            <InputOTPGroup className="gap-2">
              <InputOTPSlot index={0} className="size-11 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-mono text-base font-bold" />
              <InputOTPSlot index={1} className="size-11 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-mono text-base font-bold" />
              <InputOTPSlot index={2} className="size-11 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-mono text-base font-bold" />
              <InputOTPSlot index={3} className="size-11 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-mono text-base font-bold" />
              <InputOTPSlot index={4} className="size-11 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-mono text-base font-bold" />
              <InputOTPSlot index={5} className="size-11 rounded-xl border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-mono text-base font-bold" />
            </InputOTPGroup>
          </InputOTP>
        </div>
      </div>

      <div className="pt-4">
        <Button
          type="button"
          onClick={onSubmit}
          disabled={!isComplete || isSubmitting}
          className="w-full h-11 rounded-xl bg-primary text-white hover:bg-primary-hover font-medium shadow-sm transition-all flex items-center justify-center gap-2 hover:cursor-pointer disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              <span>Verifying...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="size-4" />
              <span>Complete Setup</span>
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
