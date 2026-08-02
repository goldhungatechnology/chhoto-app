import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { ConfirmMfaRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useConfirmMfa = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: ConfirmMfaRequest) => authApi.confirmMfa(payload),
    onSuccess: (response) => {
      toast.success(response.message || "MFA enabled successfully");
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Invalid TOTP code. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    confirmMfaAsync: mutation.mutateAsync,
    isConfirmingMfa: mutation.isPending,
    confirmMfaError: mutation.error,
  };
};
