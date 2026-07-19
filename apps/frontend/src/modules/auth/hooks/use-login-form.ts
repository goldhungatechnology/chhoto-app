"use client";

import { useRef } from "react";
import {
  useForm,
  UseFormReturn,
  SubmitHandler,
  useWatch,
} from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { type TurnstileInstance } from "@marsidev/react-turnstile";

import { toast } from "@/shared/components/custom/snackbar";

import { ROUTES, APP_DOMAIN } from "@/core/config";

import { useLogin } from "@/modules/auth/api/hooks";
import useLocalStorage from "@/shared/hooks/use-localstorage";

// ----------------------------------------------------------------------

const Schema = z.object({
  email: z.email("Invalid email"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean(),
  captcha_token: z.string().min(1, "Please complete the CAPTCHA"),
});

// ----------------------------------------------------------------------

export type LoginFormValues = z.infer<typeof Schema>;

// ----------------------------------------------------------------------

// ----------------------------------------------------------------------

interface UseLoginFormReturn {
  methods: UseFormReturn<LoginFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  turnstileRef: React.RefObject<TurnstileInstance | null>;
  isSubmitting: boolean;
  turnstileToken: string;
  onCaptchaSuccess: (token: string) => void;
  onCaptchaExpire: () => void;
}

// ----------------------------------------------------------------------

export function useLoginForm(): UseLoginFormReturn {
  const turnstileRef = useRef<TurnstileInstance | null>(null);
  const { setItem, getItem } = useLocalStorage();

  const { loginAsync } = useLogin();

  const defaultValues: LoginFormValues = {
    email: getItem("email") || "",
    password: getItem("password") || "",
    captcha_token: "",
    rememberMe: !!(getItem("email") && getItem("password")),
  };

  const methods = useForm<LoginFormValues>({
    resolver: zodResolver(Schema),
    defaultValues,
  });

  const { reset, handleSubmit, setValue, control } = methods;

  const turnstileToken = useWatch({ control, name: "captcha_token" }) || "";

  const onSubmitHandler: SubmitHandler<LoginFormValues> = async (
    data: LoginFormValues,
  ) => {
    try {
      const { rememberMe, ...finalData } = data;
      await loginAsync(finalData);

      if (rememberMe) {
        setItem("email", data.email);
        setItem("password", data.password);
      }
      window.location.assign(`${APP_DOMAIN}${ROUTES.DASHBOARD.ROOT}`);
      reset();
      toast.success("Logged in successfully!");
    } catch (error) {
      const apiError = error as {
        errors?: Record<string, string>;
        error?: string;
      };
      const errors = apiError?.errors;
      if (errors) {
        Object.entries(errors).forEach(([key, value]) => {
          methods.setError(key as keyof LoginFormValues, {
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
              : apiError?.error || "Login failed. Please try again.";
        toast.error(errorMessage);
      }
    } finally {
      setValue("captcha_token", "");
      turnstileRef.current?.reset();
    }
  };

  return {
    methods,
    onSubmit: handleSubmit(onSubmitHandler),
    turnstileRef,
    isSubmitting: methods.formState.isSubmitting,
    turnstileToken,
    onCaptchaSuccess: (token: string) => setValue("captcha_token", token),
    onCaptchaExpire: () => setValue("captcha_token", ""),
  };
}
