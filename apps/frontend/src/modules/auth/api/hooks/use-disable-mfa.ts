import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { DisableMfaRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useDisableMfa = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: DisableMfaRequest) => authApi.disableMfa(payload),
    onSuccess: (response) => {
      toast.success(response.message || "MFA disabled successfully");
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to disable MFA. Please check your password.";
      toast.error(errorMessage);
    },
  });

  return {
    disableMfaAsync: mutation.mutateAsync,
    isDisablingMfa: mutation.isPending,
    disableMfaError: mutation.error,
  };
};
