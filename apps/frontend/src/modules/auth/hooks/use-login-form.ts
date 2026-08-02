"use client";

import { useState, useRef, useEffect } from "react";
import {
  useForm,
  UseFormReturn,
  SubmitHandler,
  useWatch,
} from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { type TurnstileInstance } from "@marsidev/react-turnstile";

import { toast } from "@/shared/components/custom/snackbar";

import { ROUTES, APP_DOMAIN } from "@/core/config";

import { useLogin, useVerifyMfa } from "@/modules/auth/api/hooks";
import type { VerifyMfaRequest } from "@/modules/auth/api/auth.types";
import { localStorageAdapter, STORAGE_KEYS } from "@/core/local-storage";

// ----------------------------------------------------------------------

const Schema = z.object({
  email: z.email("Invalid email"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean(),
  captcha_token: z.string().min(1, "Please complete the CAPTCHA"),
});

// ----------------------------------------------------------------------

export type LoginFormValues = z.infer<typeof Schema>;

export type MfaMode = "otp" | "recovery";

// ----------------------------------------------------------------------

export interface UseLoginFormReturn {
  methods: UseFormReturn<LoginFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  turnstileRef: React.RefObject<TurnstileInstance | null>;
  isSubmitting: boolean;
  turnstileToken: string;
  onCaptchaSuccess: (token: string) => void;
  onCaptchaExpire: () => void;
  mfaRequired: boolean;
  mfaMode: MfaMode;
  setMfaMode: (mode: MfaMode) => void;
  otpCode: string;
  setOtpCode: (code: string) => void;
  recoveryCode: string;
  setRecoveryCode: (code: string) => void;
  isVerifyingMfa: boolean;
  onVerifyMfaSubmit: () => Promise<void>;
  onBackToLogin: () => void;
}

// ----------------------------------------------------------------------

export function useLoginForm(): UseLoginFormReturn {
  const turnstileRef = useRef<TurnstileInstance | null>(null);

  const [mfaRequired, setMfaRequired] = useState(false);
  const [tempToken, setTempToken] = useState("");
  const [mfaMode, setMfaMode] = useState<MfaMode>("otp");
  const [otpCode, setOtpCode] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");

  const { loginAsync } = useLogin();
  const { verifyMfaAsync, isVerifyingMfa } = useVerifyMfa();

  const methods = useForm<LoginFormValues>({
    resolver: zodResolver(Schema),
    defaultValues: {
      email: "",
      password: "",
      captcha_token: "",
      rememberMe: false,
    },
  });

  const { reset, handleSubmit, setValue, control } = methods;

  useEffect(() => {
    // Never persist passwords; clear any that older versions may have saved.
    localStorageAdapter.removeItem("password");
    const email =
      localStorageAdapter.getItem<string>(STORAGE_KEYS.REMEMBER_EMAIL) || "";
    if (email) {
      reset({ email, password: "", captcha_token: "", rememberMe: true });
    }
  }, [reset]);

  const turnstileToken = useWatch({ control, name: "captcha_token" }) || "";

  const persistEmail = (rememberMe: boolean, email: string) => {
    if (rememberMe) {
      localStorageAdapter.setItem(STORAGE_KEYS.REMEMBER_EMAIL, email);
    } else {
      localStorageAdapter.removeItem(STORAGE_KEYS.REMEMBER_EMAIL);
    }
  };

  const onSubmitHandler: SubmitHandler<LoginFormValues> = async (
    data: LoginFormValues,
  ) => {
    try {
      const { rememberMe, ...finalData } = data;
      const res = await loginAsync(finalData);

      if (res?.data?.mfa_required && res?.data?.temp_token) {
        setTempToken(res.data.temp_token);
        setMfaRequired(true);
        persistEmail(rememberMe, data.email);
        toast.success("Password verified. Please enter your MFA code.");
        return;
      }

      persistEmail(rememberMe, data.email);
      window.location.assign(`${APP_DOMAIN}${ROUTES.DASHBOARD.ROOT}`);
      reset();
      toast.success("Logged in successfully!");
    } catch (error) {
      const apiError = error as {
        message?: string;
        errors?: Record<string, unknown>;
        error?: string;
      };
      const errors = apiError?.errors;

      if (
        errors &&
        errors.mfa_required === true &&
        typeof errors.temp_token === "string"
      ) {
        setTempToken(errors.temp_token);
        setMfaRequired(true);
        persistEmail(data.rememberMe, data.email);
        toast.success("Password verified. Please enter your MFA code.");
      } else if (errors) {
        Object.entries(errors).forEach(([key, value]) => {
          methods.setError(key as keyof LoginFormValues, {
            type: "manual",
            message: String(value),
          });
        });
      } else {
        const errorMessage =
          apiError?.message || apiError?.error || "Login failed. Please try again.";
        toast.error(errorMessage);
      }
    } finally {
      setValue("captcha_token", "");
      turnstileRef.current?.reset();
    }
  };

  const onVerifyMfaSubmit = async () => {
    if (!tempToken) return;
    if (mfaMode === "otp" && otpCode.length !== 6) return;
    if (mfaMode === "recovery" && recoveryCode.trim().length !== 9) return;
    try {
      const payload: VerifyMfaRequest =
        mfaMode === "recovery"
          ? { temp_token: tempToken, recovery_code: recoveryCode.trim().toUpperCase() }
          : { temp_token: tempToken, otp_code: otpCode };
      await verifyMfaAsync(payload);
      window.location.assign(`${APP_DOMAIN}${ROUTES.DASHBOARD.ROOT}`);
      reset();
      toast.success("MFA verified! Logged in successfully.");
    } catch {
      // Error handled in useVerifyMfa toast
    }
  };

  const onBackToLogin = () => {
    setMfaRequired(false);
    setTempToken("");
    setMfaMode("otp");
    setOtpCode("");
    setRecoveryCode("");
  };

  return {
    methods,
    onSubmit: handleSubmit(onSubmitHandler),
    turnstileRef,
    isSubmitting: methods.formState.isSubmitting,
    turnstileToken,
    onCaptchaSuccess: (token: string) => setValue("captcha_token", token),
    onCaptchaExpire: () => setValue("captcha_token", ""),
    mfaRequired,
    mfaMode,
    setMfaMode,
    otpCode,
    setOtpCode,
    recoveryCode,
    setRecoveryCode,
    isVerifyingMfa,
    onVerifyMfaSubmit,
    onBackToLogin,
  };
}
