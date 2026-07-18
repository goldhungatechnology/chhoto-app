"use client";

import { useForm, UseFormReturn, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import * as React from "react";
import { useMe, useUpdateProfile } from "../api/hooks";
import { UserDetails } from "../api/auth.types";

const Schema = z.object({
  fullName: z
    .string()
    .min(1, "Full name is required")
    .max(100, "Full name must be less than 100 characters"),
  phoneNumber: z
    .string()
    .max(30, "Phone number must be less than 30 characters")
    .optional()
    .nullable(),
  avatar: z.string().optional().nullable(),
  avatarBg: z.string().optional().nullable(),
});

export type ProfileFormValues = z.infer<typeof Schema>;

interface UseProfileFormReturn {
  methods: UseFormReturn<ProfileFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  isSubmitting: boolean;
  user: UserDetails | undefined;
  isLoadingUser: boolean;
}

export function useProfileForm(): UseProfileFormReturn {
  const { data: meData, isLoading: isLoadingUser } = useMe();
  const user = meData?.data?.user;

  const { updateProfileAsync, isUpdatingProfile } = useUpdateProfile();

  const defaultValues: ProfileFormValues = {
    fullName: "",
    phoneNumber: "",
    avatar: "",
    avatarBg: "",
  };

  const methods = useForm<ProfileFormValues>({
    resolver: zodResolver(Schema),
    defaultValues,
  });

  const { reset, handleSubmit } = methods;

  // Sync user details to form defaults
  React.useEffect(() => {
    if (user) {
      reset({
        fullName: user.full_name || "",
        phoneNumber: user.phone_number || "",
        avatar: user.avatar || "",
        avatarBg: user.avatar_bg || "",
      });
    }
  }, [user, reset]);

  const onSubmitHandler: SubmitHandler<ProfileFormValues> = async (data) => {
    try {
      await updateProfileAsync({
        full_name: data.fullName.trim(),
        phone_number: data.phoneNumber?.trim() || null,
        avatar: data.avatar?.trim() || null,
        avatar_bg: data.avatarBg?.trim() || null,
      });
    } catch (err) {
      console.error(err);
    }
  };

  return {
    methods,
    onSubmit: handleSubmit(onSubmitHandler),
    isSubmitting: isUpdatingProfile,
    user,
    isLoadingUser,
  };
}
