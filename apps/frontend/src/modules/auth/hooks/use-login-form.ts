"use client";

import { useForm, UseFormReturn, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";

import { toast } from "@/shared/components/custom/snackbar";

import { ROUTES } from "@/core/config";

import { useLogin } from "@/modules/auth/api/hooks";

// ----------------------------------------------------------------------

const Schema = z.object({
  email: z.email("Invalid email"),
  password: z.string().min(1, "Password is required"),
  captcha_token: z.string().min(1, "Please complete the CAPTCHA"),
});

// ----------------------------------------------------------------------

export type LoginFormValues = z.infer<typeof Schema>;

// ----------------------------------------------------------------------

const defaultValues: LoginFormValues = {
  email: "",
  password: "",
  captcha_token: "",
};

// ----------------------------------------------------------------------

interface UseLoginFormReturn {
  methods: UseFormReturn<LoginFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
}

// ----------------------------------------------------------------------

export function useLoginForm(): UseLoginFormReturn {
  const router = useRouter();

  const { loginAsync } = useLogin();

  const methods = useForm<LoginFormValues>({
    resolver: zodResolver(Schema),
    defaultValues,
  });

  const { reset, handleSubmit } = methods;

  const onSubmitHandler: SubmitHandler<LoginFormValues> = async (
    data: LoginFormValues,
  ) => {
    try {
      await loginAsync(data);

      toast.success("Logged in successfully!");

      router.push(ROUTES.DASHBOARD.ROOT);

      reset();
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Login failed. Please check your credentials.";

      toast.error(errorMessage);
    }
  };

  return {
    methods: methods,
    onSubmit: handleSubmit(onSubmitHandler),
  };
}
