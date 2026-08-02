import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { toast } from "@/shared/components/custom/snackbar";

export const useSetupMfa = () => {
  const mutation = useMutation({
    mutationFn: () => authApi.setupMfa(),
    onSuccess: (response) => {
      toast.success(response.message || "MFA setup initiated");
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to initiate MFA setup. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    setupMfaAsync: mutation.mutateAsync,
    isSettingUpMfa: mutation.isPending,
    setupMfaError: mutation.error,
  };
};
