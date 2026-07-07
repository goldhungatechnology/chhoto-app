"use client";

import { z } from "zod";
import { useState } from "react";
import { useForm, UseFormReturn, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useForgotPassword } from "@/modules/auth/api/hooks";

import { toast } from "@/shared/components/custom/snackbar";

// ----------------------------------------------------------------------

const Schema = z.object({
  email: z.email("Please enter a valid email address"),
});

// ----------------------------------------------------------------------

export type ForgotPasswordFormValues = z.infer<typeof Schema>;

// ----------------------------------------------------------------------

export type ForgotPasswordState = "idle" | "loading" | "sent";

// ----------------------------------------------------------------------

interface UseForgotPasswordFormReturn {
  methods: UseFormReturn<ForgotPasswordFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  state: ForgotPasswordState;
  submittedEmail: string;
  handleResend: () => Promise<void>;
}

// ----------------------------------------------------------------------

export function useForgotPasswordForm(): UseForgotPasswordFormReturn {
  const [state, setState] = useState<ForgotPasswordState>("idle");
  const [submittedEmail, setSubmittedEmail] = useState<string>("");

  const { forgotPasswordAsync } = useForgotPassword();

  const methods = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(Schema),
    defaultValues: { email: "" },
  });

  const { handleSubmit } = methods;

  const onSubmitHandler: SubmitHandler<ForgotPasswordFormValues> = async (
    data,
  ) => {
    setState("loading");

    try {
      await forgotPasswordAsync({ email: data.email });

      setSubmittedEmail(data.email);
      setState("sent");

      toast.success("Password reset link sent to your email!");
    } catch (error) {
      setState("idle");
      const apiError = error as {
        errors?: Record<string, string>;
        error?: string;
      };
      const errors = apiError?.errors;
      if (errors) {
        Object.entries(errors).forEach(([key, value]) => {
          methods.setError(key as keyof ForgotPasswordFormValues, {
            type: "manual",
            message: value,
          });
        });
      } else {
        const errorMessage =
          typeof error === "string"
            ? error
            : error instanceof Error
              ? error.message
              : apiError?.error || "Failed to send password reset link. Please try again.";
        toast.error(errorMessage);
      }
    }
  };

  const handleResend = async () => {
    if (!submittedEmail) return;

    setState("loading");

    try {
      await forgotPasswordAsync({ email: submittedEmail });

      setState("sent");

      toast.success("Password reset link resent!");
    } catch (error) {
      setState("idle");
      const apiError = error as {
        errors?: Record<string, string>;
        error?: string;
      };
      const errorMessage =
        typeof error === "string"
          ? error
          : error instanceof Error
            ? error.message
            : apiError?.error || "Failed to resend password reset link. Please try again.";
      toast.error(errorMessage);
    }
  };

  return {
    methods,
    state,
    submittedEmail,
    //
    handleResend,
    onSubmit: handleSubmit(onSubmitHandler),
  };
}
