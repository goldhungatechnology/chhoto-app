"use client";

import * as React from "react";
import { useMe } from "../api/hooks/use-me";
import { useSetupMfa } from "../api/hooks/use-setup-mfa";
import { useConfirmMfa } from "../api/hooks/use-confirm-mfa";
import { useDisableMfa } from "../api/hooks/use-disable-mfa";

export function useMfaSettings() {
  const { data: meData, isLoading: isLoadingMe } = useMe();
  const mfaEnabled = Boolean(meData?.data?.security?.mfa_enabled);

  const [isSetupActive, setIsSetupActive] = React.useState(false);
  const [isRecoveryViewActive, setIsRecoveryViewActive] = React.useState(false);
  const [authUrl, setAuthUrl] = React.useState<string>("");
  const [secret, setSecret] = React.useState<string>("");
  const [otpCode, setOtpCode] = React.useState<string>("");
  const [recoveryCodes, setRecoveryCodes] = React.useState<string[]>([]);
  const [isDisableDialogOpen, setIsDisableDialogOpen] = React.useState(false);

  const { setupMfaAsync, isSettingUpMfa } = useSetupMfa();
  const { confirmMfaAsync, isConfirmingMfa } = useConfirmMfa();
  const { disableMfaAsync, isDisablingMfa } = useDisableMfa();

  const handleStartSetup = async () => {
    try {
      const res = await setupMfaAsync();
      if (res?.data) {
        setAuthUrl(res.data.auth_url);
        setSecret(res.data.secret);
        setIsSetupActive(true);
        setIsRecoveryViewActive(false);
        setOtpCode("");
        setRecoveryCodes([]);
      }
    } catch {
      // Error handled by mutation toast
    }
  };

  const handleConfirmSetup = async () => {
    if (otpCode.length !== 6) return;
    try {
      const res = await confirmMfaAsync({ otp_code: otpCode });
      if (res?.data?.recovery_codes) {
        setRecoveryCodes(res.data.recovery_codes);
        setIsSetupActive(false);
        setIsRecoveryViewActive(true);
        setOtpCode("");
        setAuthUrl("");
        setSecret("");
      }
    } catch {
      // Error handled by mutation toast
    }
  };

  const handleRecoveryCodesAcknowledged = () => {
    setIsRecoveryViewActive(false);
    setRecoveryCodes([]);
  };

  const handleDisableMfa = async (password: string) => {
    try {
      await disableMfaAsync({ password });
      setIsDisableDialogOpen(false);
      setIsSetupActive(false);
      setIsRecoveryViewActive(false);
      setRecoveryCodes([]);
    } catch {
      // Error handled by mutation toast
    }
  };

  const handleCancelSetup = () => {
    setIsSetupActive(false);
    setIsRecoveryViewActive(false);
    setOtpCode("");
    setAuthUrl("");
    setSecret("");
    setRecoveryCodes([]);
  };

  const handleToggleMfa = () => {
    if (mfaEnabled) {
      setIsDisableDialogOpen(true);
    } else {
      handleStartSetup();
    }
  };

  return {
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
  };
}
