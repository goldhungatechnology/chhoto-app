import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useOnboardingSubmit = () => {
  const mutation = useMutation({
    mutationFn: authApi.onboarding,
  });

  return {
    onboardingAsync: mutation.mutateAsync,
    isOnboarding: mutation.isPending,
    onboardingError: mutation.error,
    resetOnboarding: mutation.reset,
  };
};
