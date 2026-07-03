import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// -----------------------------------------------------------------------------

export const useForgotPassword = () => {
  const mutation = useMutation({
    mutationFn: authApi.forgotPassword,
  });

  return {
    forgotPasswordAsync: mutation.mutateAsync,
    isSending: mutation.isPending,
    forgotPasswordError: mutation.error,
    resetForgotPassword: mutation.reset,
  };
};
