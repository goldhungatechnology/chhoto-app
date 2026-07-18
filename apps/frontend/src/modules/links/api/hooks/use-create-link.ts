import { useMutation, useQueryClient } from "@tanstack/react-query";
import { linksApi } from "../index";

export const useCreateLink = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: linksApi.createLink,
    onSuccess: () => {
      // Invalidate existing list of links query to trigger a refetch if it exists
      queryClient.invalidateQueries({ queryKey: ["links"] });
    },
  });

  return {
    createLinkAsync: mutation.mutateAsync,
    isCreatingLink: mutation.isPending,
    createLinkError: mutation.error,
    resetCreateLink: mutation.reset,
  };
};
