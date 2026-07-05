"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { localStorageAdapter, STORAGE_KEYS } from "@/core/local-storage";
import { ROUTES } from "@/core/config";

import { useVerify, useResendOtp } from "@/modules/auth/api/hooks";

// ----------------------------------------------------------------------

type VerificationState = "idle" | "verifying" | "success" | "error";

// ----------------------------------------------------------------------

export interface UseVerifyFormReturn {
  otp: string[];
  state: VerificationState;
  errorMessage: string;
  resendCooldown: number;
  userEmail: string;
  isVerifying: boolean;
  isOtpComplete: boolean;
  //
  handleOtpChange: (newOtp: string[]) => void;
  handleVerify: () => Promise<void>;
  handleResend: () => Promise<void>;
}

// ----------------------------------------------------------------------

export function useVerifyForm(): UseVerifyFormReturn {
  const router = useRouter();

  const { verifyAsync, isVerifying } = useVerify();
  const { resendOtpAsync } = useResendOtp();

  const [otp, setOtp] = useState<string[]>(["", "", "", "", "", ""]);
  const [state, setState] = useState<VerificationState>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [resendCooldown, setResendCooldown] = useState<number>(0);
  const [userEmail, setUserEmail] = useState<string>("");

  useEffect(() => {
    const storedEmail = localStorageAdapter.getItem<string>(
      STORAGE_KEYS.PENDING_EMAIL,
    );

    // eslint-disable-next-line react-hooks/set-state-in-effect
    setUserEmail(storedEmail || "");
  }, []);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(
        () => setResendCooldown(resendCooldown - 1),
        1000,
      );
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const handleOtpChange = (newOtp: string[]) => {
    setOtp(newOtp);

    if (state === "error") {
      setState("idle");
      setErrorMessage("");
    }
  };

  const handleVerify = async () => {
    const code = otp.join("");

    if (code.length !== 6) {
      setErrorMessage("Please enter all 6 digits");
      setState("error");
      return;
    }

    setState("verifying");
    setErrorMessage("");

    try {
      const payload = {
        verification_token: code,
        email: userEmail,
      };

      await verifyAsync(payload);

      setState("success");
      localStorageAdapter.removeItem(STORAGE_KEYS.PENDING_EMAIL);

      setTimeout(() => {
        router.push(ROUTES.ONBOARDING.ROOT);
      }, 1000);
    } catch (error) {
      setState("error");

      const message =
        error instanceof Error
          ? error.message
          : "Invalid verification code. Please try again.";

      setErrorMessage(message);
      setOtp(["", "", "", "", "", ""]);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;

    try {
      const payload = {
        email: userEmail,
        type: "account_verification",
      };

      await resendOtpAsync(payload);

      setResendCooldown(60);
      setOtp(["", "", "", "", "", ""]);
      setState("idle");
      setErrorMessage("");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to resend code. Please try again.";
      setErrorMessage(message);
    }
  };

  const isOtpComplete = otp.every((digit) => digit !== "");

  return {
    otp,
    state,
    errorMessage,
    resendCooldown,
    userEmail,
    isVerifying,
    isOtpComplete,
    //
    handleOtpChange,
    handleVerify,
    handleResend,
  };
}
