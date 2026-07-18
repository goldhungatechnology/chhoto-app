import { useQuery } from "@tanstack/react-query";
import { linksApi } from "../index";

export const useLinkSessions = (linkUuid: string, enabled: boolean) => {
  const query = useQuery({
    queryKey: ["link-sessions", linkUuid],
    queryFn: () => linksApi.listLinkSessions(linkUuid),
    enabled: enabled && !!linkUuid,
  });

  return {
    sessions: query.data?.data || [],
    isLoadingSessions: query.isLoading,
    sessionsError: query.error,
    refetchSessions: query.refetch,
  };
};
