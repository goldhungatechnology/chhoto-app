import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { RevokeAllSessionsRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useRevokeAllSessions = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: RevokeAllSessionsRequest) =>
      authApi.revokeAllSessions(payload),
    onSuccess: (response) => {
      toast.success(response.message || "Sessions revoked successfully");
      queryClient.invalidateQueries({ queryKey: ["auth", "sessions"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to revoke sessions. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    revokeAllSessionsAsync: mutation.mutateAsync,
    isRevokingAllSessions: mutation.isPending,
    revokeAllSessionsError: mutation.error,
  };
};
