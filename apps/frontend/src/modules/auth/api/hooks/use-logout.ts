import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { authApi } from "@/modules/auth/api";
import { ROUTES } from "@/core/config";
import { toast } from "@/shared/components/custom/snackbar";

// ----------------------------------------------------------------------

export const useLogout = () => {
  const router = useRouter();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.setQueryData(["auth", "me"], null);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      toast.success("Logged out successfully!");
      router.push(ROUTES.AUTH.LOGIN);
    },
    onError: () => {
      // In case of error, we should still clear local query cache and redirect
      queryClient.setQueryData(["auth", "me"], null);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      toast.error("An error occurred during logout, but you have been redirected.");
      router.push(ROUTES.AUTH.LOGIN);
    },
  });

  return {
    logoutAsync: mutation.mutateAsync,
    isLoggingOut: mutation.isPending,
  };
};
