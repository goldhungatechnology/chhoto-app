import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { RevokeSessionRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useRevokeSession = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: RevokeSessionRequest) => authApi.revokeSession(payload),
    onSuccess: (response) => {
      toast.success(response.message || "Session revoked successfully");
      queryClient.invalidateQueries({ queryKey: ["auth", "sessions"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to revoke session. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    revokeSessionAsync: mutation.mutateAsync,
    isRevokingSession: mutation.isPending,
    revokeSessionError: mutation.error,
  };
};
