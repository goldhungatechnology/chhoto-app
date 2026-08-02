import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { VerifyMfaRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useVerifyMfa = () => {
  const mutation = useMutation({
    mutationFn: (payload: VerifyMfaRequest) => authApi.verifyMfa(payload),
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Invalid MFA code. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    verifyMfaAsync: mutation.mutateAsync,
    isVerifyingMfa: mutation.isPending,
    verifyMfaError: mutation.error,
  };
};
