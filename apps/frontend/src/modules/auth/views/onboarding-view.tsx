"use client";

import { OnboardingSection } from "@/modules/auth/components";
import { useMe } from "../api/hooks";
import { redirect } from "next/navigation";
import { ROUTES } from "@/core/config";

export default function OnboardingView() {
  const { data } = useMe();
  const user = data?.data?.user;
  if (user && user.is_onboarded) {
    redirect(ROUTES.DASHBOARD.ROOT);
  }
  return <OnboardingSection />;
}
