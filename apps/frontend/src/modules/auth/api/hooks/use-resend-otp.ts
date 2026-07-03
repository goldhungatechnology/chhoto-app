import { useMutation } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useResendOtp = () => {
  const mutation = useMutation({
    mutationFn: authApi.resendOtp,
  });

  return {
    resendOtpAsync: mutation.mutateAsync,
    isResendingOtp: mutation.isPending,
    resendOtpError: mutation.error,
    resetResendOtp: mutation.reset,
  };
};
