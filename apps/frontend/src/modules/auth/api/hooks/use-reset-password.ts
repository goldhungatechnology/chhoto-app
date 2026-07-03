import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useResetPassword = () => {
  const mutation = useMutation({
    mutationFn: authApi.resetPassword,
  });

  return {
    resetPasswordAsync: mutation.mutateAsync,
    isResetting: mutation.isPending,
    resetPasswordError: mutation.error,
    resetResetPassword: mutation.reset,
  };
};
