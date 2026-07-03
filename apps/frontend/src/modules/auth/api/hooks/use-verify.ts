import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useVerify = () => {
  const mutation = useMutation({
    mutationFn: authApi.verify,
  });

  return {
    verifyAsync: mutation.mutateAsync,
    isVerifying: mutation.isPending,
    verifyError: mutation.error,
    resetVerify: mutation.reset,
  };
};
