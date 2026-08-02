import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/modules/auth/api";

export const useSessions = () => {
  return useQuery({
    queryKey: ["auth", "sessions"],
    queryFn: () => authApi.getSessions(),
    staleTime: 60 * 1000,
    refetchOnWindowFocus: true,
  });
};
