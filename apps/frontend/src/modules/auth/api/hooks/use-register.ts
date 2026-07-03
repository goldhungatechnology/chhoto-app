import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useRegister = () => {
  const mutation = useMutation({
    mutationFn: authApi.register,
  });

  return {
    registerAsync: mutation.mutateAsync,
    isRegistering: mutation.isPending,
    registerError: mutation.error,
    resetRegister: mutation.reset,
  };
};
