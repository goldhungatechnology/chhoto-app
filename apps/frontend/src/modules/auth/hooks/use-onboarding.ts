"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { ROUTES } from "@/core/config";
import { localStorageAdapter } from "@/core/local-storage";
import { useOnboardingSubmit } from "../api/hooks/use-onboarding-submit";
import { toast } from "@/shared/components/custom/snackbar";

export interface UseOnboardingReturn {
  currentStep: string;
  setStep: (step: string) => void;
  getBackHref: () => string;
  fullName: string;
  setFullName: (name: string) => void;
  theme: "light" | "dark" | "";
  setTheme: (theme: "light" | "dark" | "") => void;
  referralSource: string;
  setReferralSource: (source: string) => void;
  handleContinue: () => Promise<void>;
  handleSkip: () => Promise<void>;
  isSubmitting: boolean;
  isMounted: boolean;
}

export function useOnboarding(): UseOnboardingReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const currentStep = searchParams.get("step") || "1";

  const [fullName, setFullName] = useState("");
  const [theme, setTheme] = useState<"light" | "dark" | "">("");
  const [referralSource, setReferralSource] = useState("");
  const [isMounted, setIsMounted] = useState(false);

  const { onboardingAsync, isOnboarding } = useOnboardingSubmit();

  useEffect(() => {
    const savedName = localStorageAdapter.getItem<string>("onboarding_full_name") || "";
    const savedTheme = localStorageAdapter.getItem<"light" | "dark" | "">("onboarding_theme") || "";
    const savedSource = localStorageAdapter.getItem<string>("onboarding_referral_source") || "";

    setTimeout(() => {
      setIsMounted(true);
      if (savedName) setFullName(savedName);
      if (savedTheme) setTheme(savedTheme);
      if (savedSource) setReferralSource(savedSource);
    }, 0);
  }, []);

  const handleSetFullName = (name: string) => {
    setFullName(name);
    localStorageAdapter.setItem("onboarding_full_name", name);
  };

  const handleSetTheme = (newTheme: "light" | "dark" | "") => {
    setTheme(newTheme);
    localStorageAdapter.setItem("onboarding_theme", newTheme);
  };

  const handleSetReferralSource = (source: string) => {
    setReferralSource(source);
    localStorageAdapter.setItem("onboarding_referral_source", source);
  };

  const setStep = (step: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("step", step);
    router.push(`${pathname}?${params.toString()}`);
  };

  const getBackHref = () => {
    if (currentStep === "1") {
      return ROUTES.AUTH.LOGIN;
    }
    return `${ROUTES.ONBOARDING.ROOT}?step=${Number(currentStep) - 1}`;
  };

  const handleContinue = async () => {
    if (currentStep === "1") {
      if (!fullName.trim()) return;
      setStep("2");
    } else if (currentStep === "2") {
      if (!theme) return;
      setStep("3");
    } else if (currentStep === "3") {
      if (!referralSource) return;
      await submitOnboarding(fullName, theme || "light", referralSource);
    }
  };

  const handleSkip = async () => {
    if (currentStep === "1") {
      return;
    } else if (currentStep === "2") {
      const nextTheme = theme || "light";
      handleSetTheme(nextTheme);
      setStep("3");
    } else if (currentStep === "3") {
      await submitOnboarding(fullName, theme || "light", "skipped");
    }
  };

  const submitOnboarding = async (
    name: string,
    selectedTheme: "light" | "dark",
    source: string,
  ) => {
    try {
      await onboardingAsync({
        full_name: name,
        theme: selectedTheme,
        referral_source: source,
      });

      toast.success("Onboarding completed successfully!");

      localStorageAdapter.removeItem("onboarding_full_name");
      localStorageAdapter.removeItem("onboarding_theme");
      localStorageAdapter.removeItem("onboarding_referral_source");

      router.push(ROUTES.DASHBOARD.ROOT);
    } catch (error) {
      const apiError = error as { errors?: Record<string, unknown>; message?: string };
      const errorMessage =
        apiError?.message || "Failed to submit onboarding. Please try again.";
      toast.error(errorMessage);
    }
  };

  return {
    currentStep,
    setStep,
    getBackHref,
    fullName,
    setFullName: handleSetFullName,
    theme,
    setTheme: handleSetTheme,
    referralSource,
    setReferralSource: handleSetReferralSource,
    handleContinue,
    handleSkip,
    isSubmitting: isOnboarding,
    isMounted,
  };
}
