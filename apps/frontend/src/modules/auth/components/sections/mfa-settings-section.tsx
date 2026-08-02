"use client";

import * as React from "react";
import { Card } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { MfaMethodCard, MfaQrCode, MfaOtpInput, MfaRecoveryCodes, MfaDisableDialog } from "../blocks";
import { useMfaSettings } from "../../hooks";
import { ShieldCheck, Plus, ArrowLeft, Shield } from "lucide-react";

export function MfaSettingsSection() {
  const {
    mfaEnabled,
    isLoadingMe,
    isSetupActive,
    isRecoveryViewActive,
    authUrl,
    secret,
    otpCode,
    setOtpCode,
    recoveryCodes,
    isSettingUpMfa,
    isConfirmingMfa,
    isDisablingMfa,
    isDisableDialogOpen,
    setIsDisableDialogOpen,
    handleStartSetup,
    handleConfirmSetup,
    handleRecoveryCodesAcknowledged,
    handleDisableMfa,
    handleCancelSetup,
    handleToggleMfa,
  } = useMfaSettings();

  if (isLoadingMe) {
    return (
      <Card className="border border-border/60 rounded-3xl p-6 bg-white dark:bg-card shadow-xs">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded-md w-1/4" />
          <div className="h-20 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card className="border border-border/60 rounded-3xl p-6 bg-white dark:bg-card shadow-xs space-y-6 text-left">
        {/* Header with Title, Description, and Back Button */}
        <div className="border-b border-border/40 pb-4 flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 className="text-lg font-bold text-slate-950 dark:text-zinc-50 flex items-center gap-2">
              <Shield className="size-5 text-purple-600 dark:text-purple-400" />
              <span>Multi-Factor Authentication</span>
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Add an extra layer of security to your account by requiring more than just a password to log in.
            </p>
          </div>

          {isSetupActive && !isRecoveryViewActive && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleCancelSetup}
              className="h-8 px-3 text-xs text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-800 rounded-xl flex items-center gap-1.5 hover:cursor-pointer"
            >
              <ArrowLeft className="size-3.5" />
              <span>Back</span>
            </Button>
          )}
        </div>

        {/* State 1: Setup Flow Active (mfa_2.png) */}
        {isSetupActive ? (
          <div className="space-y-6 animate-in fade-in-50 duration-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
              {/* Step 1: Scan QR Code */}
              <MfaQrCode authUrl={authUrl} secret={secret} />

              {/* Step 2: Verify Code */}
              <MfaOtpInput
                value={otpCode}
                onChange={setOtpCode}
                onSubmit={handleConfirmSetup}
                isSubmitting={isConfirmingMfa}
              />
            </div>
          </div>
        ) : isRecoveryViewActive ? (
          /* State 2: Recovery Codes (shown once after setup completes) */
          <div className="space-y-6 animate-in fade-in-50 duration-200">
            <MfaRecoveryCodes codes={recoveryCodes} />

            <div className="flex flex-col items-center gap-2 pt-1">
              <Button
                type="button"
                onClick={handleRecoveryCodesAcknowledged}
                className="w-full max-w-sm h-11 rounded-xl bg-primary text-white hover:bg-primary-hover font-medium shadow-sm transition-all flex items-center justify-center gap-2 hover:cursor-pointer"
              >
                <ShieldCheck className="size-4" />
                <span>I&apos;ve saved my codes</span>
              </Button>
              <p className="text-[11px] text-muted-foreground">
                These codes will only be shown once. Store them somewhere safe.
              </p>
            </div>
          </div>
        ) : (
          /* State 3: List View (mfa_1.png) */
          <div className="space-y-4">
            <MfaMethodCard
              enabled={mfaEnabled}
              onToggleMfa={handleToggleMfa}
              isLoading={isSettingUpMfa || isDisablingMfa}
            />

            {/* Add backup method dashed button */}
            <button
              type="button"
              onClick={handleStartSetup}
              disabled={isSettingUpMfa}
              className="w-full py-3.5 px-4 rounded-2xl border-2 border-dashed border-slate-200 dark:border-zinc-800 text-xs font-semibold text-slate-600 dark:text-zinc-400 hover:border-slate-300 dark:hover:border-zinc-700 hover:bg-slate-50/50 dark:hover:bg-zinc-900/40 transition-all flex items-center justify-center gap-2 hover:cursor-pointer disabled:opacity-50"
            >
              <Plus className="size-4" />
              <span>{mfaEnabled ? "Add backup method" : "Setup Multi-Factor Authentication"}</span>
            </button>
          </div>
        )}
      </Card>

      {/* Disable MFA Confirmation Dialog */}
      <MfaDisableDialog
        open={isDisableDialogOpen}
        onOpenChange={setIsDisableDialogOpen}
        onConfirmDisable={handleDisableMfa}
        isDisabling={isDisablingMfa}
      />
    </>
  );
}
