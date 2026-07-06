import { Suspense } from "react";
import { OnboardingView } from "@/modules/auth/views";

export const metadata = {
  title: "Onboarding",
};

export default function Page() {
  return (
    <Suspense fallback={null}>
      <OnboardingView />
    </Suspense>
  );
}
