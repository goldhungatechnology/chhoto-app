"use client";

import { useForm, UseFormReturn, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "@/shared/components/custom/snackbar";
import { useCreateLink } from "../api/hooks/use-create-link";
import { LinkData } from "../types";

const Schema = z
  .object({
    url: z.string().url("Must be a valid destination URL"),
    title: z
      .string()
      .max(255, "Title must be less than 255 characters")
      .optional(),
    customSlug: z
      .string()
      .max(255, "Custom slug must be less than 255 characters")
      .regex(
        /^[a-zA-Z0-9_-]*$/,
        "Slug can only contain alphanumeric characters, hyphens, and underscores",
      )
      .optional(),
    platform: z.enum(["web", "instagram", "youtube", "tiktok", "ads", "other"]),
    generateQr: z.boolean(),
    autoExpire: z.boolean(),
    expiryDate: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.autoExpire && !data.expiryDate) {
        return false;
      }
      return true;
    },
    {
      message: "Expiry date is required when auto-expire is enabled",
      path: ["expiryDate"],
    },
  );

export type CreateLinkFormValues = z.infer<typeof Schema>;

interface UseCreateLinkFormReturn {
  methods: UseFormReturn<CreateLinkFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  isSubmitting: boolean;
  successData: LinkData | null;
  resetForm: () => void;
}

export function useCreateLinkForm(
  onSuccessCallback?: (data: LinkData) => void,
): UseCreateLinkFormReturn {
  const { createLinkAsync, isCreatingLink } = useCreateLink();

  const defaultValues: CreateLinkFormValues = {
    url: "",
    title: "",
    customSlug: "",
    platform: "instagram",
    generateQr: false,
    autoExpire: false,
    expiryDate: "",
  };

  const methods = useForm<CreateLinkFormValues>({
    resolver: zodResolver(Schema),
    defaultValues,
  });

  const { reset, handleSubmit } = methods;

  const onSubmitHandler: SubmitHandler<CreateLinkFormValues> = async (data) => {
    try {
      const payload = {
        destination_url: data.url,
        title: data.title || undefined,
        custom_slug: data.customSlug || undefined,
        tags: [`platform:${data.platform}`],
        auto_expire:
          data.autoExpire && data.expiryDate
            ? new Date(data.expiryDate).toISOString()
            : null,
      };

      const response = await createLinkAsync(payload);
      toast.success(response.message || "Short link created successfully!");

      if (onSuccessCallback) {
        onSuccessCallback({
          ...response.data,
          generateQr: data.generateQr,
        });
      }

      reset(defaultValues);
    } catch (error: unknown) {
      const apiError = error as {
        errors?: Record<string, string>;
        error?: string;
        message?: string;
      };

      const errors = apiError?.errors;
      if (errors) {
        Object.entries(errors).forEach(([key, value]) => {
          // Map backend error keys if needed
          const formKey =
            key === "destination_url"
              ? "url"
              : key === "custom_slug"
                ? "customSlug"
                : key;
          methods.setError(formKey as keyof CreateLinkFormValues, {
            type: "manual",
            message: value,
          });
        });
      } else {
        const errorMessage =
          apiError?.message ||
          apiError?.error ||
          (error instanceof Error
            ? error.message
            : "Failed to create short link. Please try again.");
        toast.error(errorMessage);
      }
    }
  };

  return {
    methods,
    onSubmit: handleSubmit(onSubmitHandler),
    isSubmitting: isCreatingLink,
    successData: null,
    resetForm: () => reset(defaultValues),
  };
}
