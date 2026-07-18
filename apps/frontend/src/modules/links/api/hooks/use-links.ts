import { useQuery } from "@tanstack/react-query";
import { linksApi } from "../index";

export const useLinks = () => {
  const query = useQuery({
    queryKey: ["links"],
    queryFn: linksApi.listLinks,
  });

  return {
    links: query.data?.data || [],
    isLoadingLinks: query.isLoading,
    linksError: query.error,
    refetchLinks: query.refetch,
  };
};
