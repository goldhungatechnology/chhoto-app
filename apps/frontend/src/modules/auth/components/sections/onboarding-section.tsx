"use client";

import { ArrowLeft } from "lucide-react";
import { useOnboarding } from "../../hooks";
import Link from "next/link";
import { Logo } from "@/shared/components/custom/logo";
import StepName from "./onboarding/step-name";
import StepTheme from "./onboarding/step-theme";
import StepReferral from "./onboarding/step-referral";

export default function OnboardingSection() {
  const {
    currentStep,
    getBackHref,
    fullName,
    setFullName,
    theme,
    setTheme,
    referralSource,
    setReferralSource,
    handleContinue,
    handleSkip,
    isSubmitting,
    isMounted,
  } = useOnboarding();

  if (!isMounted) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen w-screen flex-col items-center justify-center bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-primary-soft/50 via-slate-50 to-slate-100/80 p-6">
      <OnboardingLogoSection getBackHref={getBackHref} />

      {/* Dynamic Step Rendering */}
      {currentStep === "1" && (
        <StepName
          fullName={fullName}
          setFullName={setFullName}
          onContinue={handleContinue}
        />
      )}

      {currentStep === "2" && (
        <StepTheme
          theme={theme}
          setTheme={setTheme}
          onContinue={handleContinue}
          onSkip={handleSkip}
        />
      )}

      {currentStep === "3" && (
        <StepReferral
          referralSource={referralSource}
          setReferralSource={setReferralSource}
          onContinue={handleContinue}
          onSkip={handleSkip}
          isSubmitting={isSubmitting}
        />
      )}
    </div>
  );
}

const OnboardingLogoSection = ({
  getBackHref,
}: {
  getBackHref: () => string;
}) => {
  return (
    <div className="fixed top-0 left-0 right-0 flex items-center justify-between px-6 py-4 md:px-12">
      <div className="flex items-center gap-3">
        <Link
          href={getBackHref()}
          className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 shadow-sm transition-all duration-200 hover:bg-slate-50 hover:text-slate-900"
        >
          <ArrowLeft size={16} />
        </Link>
        <Logo />
      </div>
    </div>
  );
};
