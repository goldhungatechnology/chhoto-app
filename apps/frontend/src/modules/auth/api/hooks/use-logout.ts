import { useMutation, useQueryClient } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";
import { ROUTES, AUTH_DOMAIN } from "@/core/config";
import { toast } from "@/shared/components/custom/snackbar";

// ----------------------------------------------------------------------

export const useLogout = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.setQueryData(["auth", "me"], null);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      toast.success("Logged out successfully!");
      window.location.assign(`${AUTH_DOMAIN}${ROUTES.AUTH.LOGIN}`);
    },
    onError: () => {
      // In case of error, we should still clear local query cache and redirect
      queryClient.setQueryData(["auth", "me"], null);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      toast.error("An error occurred during logout, but you have been redirected.");
      window.location.assign(`${AUTH_DOMAIN}${ROUTES.AUTH.LOGIN}`);
    },
  });

  return {
    logoutAsync: mutation.mutateAsync,
    isLoggingOut: mutation.isPending,
  };
};
