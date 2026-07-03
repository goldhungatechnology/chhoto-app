import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useLogin = () => {
  const mutation = useMutation({
    mutationFn: authApi.login,
  });

  return {
    loginAsync: mutation.mutateAsync,
    isLoggingIn: mutation.isPending,
    loginError: mutation.error,
    resetLogin: mutation.reset,
  };
};
