import { useQuery } from "@tanstack/react-query";

import { authApi } from "@/modules/auth/api";

// ----------------------------------------------------------------------

export const useMe = () => {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: authApi.me,
    retry: 0, // We want to fail quickly if unauthenticated so the router can redirect
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000, // 5 minutes cache stale time
  });
};
