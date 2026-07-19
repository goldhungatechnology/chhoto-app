import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { InterfaceSetupRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useUpdateInterface = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: InterfaceSetupRequest) => authApi.interfaceSetup(payload),
    onSuccess: () => {
      // Quietly invalidate the query to update state across the app,
      // avoiding too many success toasts for background config changes unless desired.
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to save interface settings. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    updateInterfaceAsync: mutation.mutateAsync,
    isUpdatingInterface: mutation.isPending,
    updateInterfaceError: mutation.error,
  };
};
