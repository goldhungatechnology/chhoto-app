"use client";

import { useState } from "react";
import { useForm, UseFormReturn, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { useResetPassword } from "@/modules/auth/api/hooks";

import { toast } from "@/shared/components/custom/snackbar";

// ----------------------------------------------------------------------

const Schema = z
  .object({
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[0-9]/, "Password must contain at least one number"),
    confirm_password: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

// ----------------------------------------------------------------------

export type ResetPasswordFormValues = z.infer<typeof Schema>;

// ----------------------------------------------------------------------

export type ResetPasswordState =
  | "idle"
  | "loading"
  | "success"
  | "invalid_token";

// ----------------------------------------------------------------------

interface UseResetPasswordFormReturn {
  methods: UseFormReturn<ResetPasswordFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  state: ResetPasswordState;
  token: string | null;
}

// ----------------------------------------------------------------------

export function useResetPasswordForm(
  token: string | null,
): UseResetPasswordFormReturn {
  const [state, setState] = useState<ResetPasswordState>(
    token ? "idle" : "invalid_token",
  );

  const { resetPasswordAsync } = useResetPassword();

  const methods = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(Schema),
    defaultValues: { password: "", confirm_password: "" },
  });

  const { handleSubmit } = methods;

  const onSubmitHandler: SubmitHandler<ResetPasswordFormValues> = async (
    data,
  ) => {
    if (!token) {
      setState("invalid_token");
      return;
    }

    setState("loading");

    try {
      await resetPasswordAsync({ token, password: data.password });

      setState("success");

      toast.success("Password reset successfully!");
    } catch (error) {
      const message = error instanceof Error ? error.message.toLowerCase() : "";

      if (message.includes("expired") || message.includes("invalid")) {
        setState("invalid_token");
      } else {
        setState("idle");
      }
    }
  };

  return {
    methods,
    onSubmit: handleSubmit(onSubmitHandler),
    state,
    token,
  };
}
