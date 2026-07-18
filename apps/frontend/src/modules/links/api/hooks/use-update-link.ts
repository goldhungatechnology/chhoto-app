import { useMutation, useQueryClient } from "@tanstack/react-query";
import { linksApi } from "../index";
import { toast } from "@/shared/components/custom/snackbar";

export const useUpdateLink = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({
      linkUuid,
      title,
    }: {
      linkUuid: string;
      title: string | null;
    }) => linksApi.updateLink(linkUuid, { title }),
    onSuccess: (response) => {
      toast.success(response.message || "Link updated successfully");
      queryClient.invalidateQueries({ queryKey: ["links"] });
    },
    onError: (error: unknown) => {
      const apiError = error as { message?: string };
      const errorMessage =
        apiError?.message || "Failed to update link title. Please try again.";
      toast.error(errorMessage);
    },
  });

  return {
    updateLinkAsync: mutation.mutateAsync,
    isUpdatingLink: mutation.isPending,
    updateLinkError: mutation.error,
  };
};
