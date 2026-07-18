import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";
import { UpdateProfileRequest } from "../auth.types";
import { toast } from "@/shared/components/custom/snackbar";

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: UpdateProfileRequest) => authApi.updateProfile(payload),
    onSuccess: (response) => {
      toast.success(response.message || "Profile updated successfully");
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to update profile. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    updateProfileAsync: mutation.mutateAsync,
    isUpdatingProfile: mutation.isPending,
    updateProfileError: mutation.error,
  };
};
