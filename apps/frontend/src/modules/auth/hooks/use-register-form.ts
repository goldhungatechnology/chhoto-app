"use client";

import { useState, useRef } from "react";
import {
  useForm,
  UseFormReturn,
  SubmitHandler,
  useWatch,
} from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { type TurnstileInstance } from "@marsidev/react-turnstile";

import { ROUTES } from "@/core/config";
import { localStorageAdapter, STORAGE_KEYS } from "@/core/local-storage";

import { useRegister } from "@/modules/auth/api/hooks";

import { toast } from "@/shared/components/custom/snackbar";

// ----------------------------------------------------------------------

const Schema = z.object({
  email: z.email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  cf_turnstile_response: z.string().min(1, "Please complete the CAPTCHA"),
});

// ----------------------------------------------------------------------

export type RegisterFormValues = z.infer<typeof Schema>;

// ----------------------------------------------------------------------

const defaultValues: RegisterFormValues = {
  email: "",
  password: "",
  cf_turnstile_response: "",
};

// ----------------------------------------------------------------------

interface UseRegisterFormReturn {
  methods: UseFormReturn<RegisterFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  showPassword: boolean;
  handleContinue: () => Promise<void>;
  isSubmitting: boolean;
  turnstileToken: string;
  onCaptchaSuccess: (token: string) => void;
  onCaptchaExpire: () => void;
  turnstileRef: React.RefObject<TurnstileInstance | null>;
}

// ----------------------------------------------------------------------

export function useRegisterForm(): UseRegisterFormReturn {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(true);
  const turnstileRef = useRef<TurnstileInstance | null>(null);

  const { registerAsync } = useRegister();

  const methods = useForm<RegisterFormValues>({
    resolver: zodResolver(Schema as never),
    defaultValues,
  });

  const {
    reset,
    handleSubmit,
    setError,
    trigger,
    setFocus,
    setValue,
    control,
  } = methods;

  const turnstileToken =
    useWatch({ control, name: "cf_turnstile_response" }) || "";

  const handleContinue = async () => {
    const isEmailValid = await trigger("email");

    if (!isEmailValid) {
      return;
    }

    setShowPassword(true);
    setFocus("password");
  };

  const onSubmitHandler: SubmitHandler<RegisterFormValues> = async (
    data: RegisterFormValues,
  ) => {
    try {
      await registerAsync({
        email: data.email,
        password: data.password,
        captcha_token: data.cf_turnstile_response,
      });

      localStorageAdapter.setItem(STORAGE_KEYS.PENDING_EMAIL, data.email);

      toast.success("Registered successfully!");

      router.push(ROUTES.AUTH.VERIFY);

      reset();
    } catch (error) {
      const apiError = error as { errors?: Record<string, string>; error?: string };
      const errors = apiError?.errors;
      if (errors) {
        Object.entries(errors).forEach(([key, value]) => {
          if (key === "captcha_token") {
            setError("cf_turnstile_response", {
              type: "manual",
              message: value,
            });
            toast.error(
              "Security check failed. Please reload the page and try again.",
            );
          } else {
            setError(key as keyof RegisterFormValues, {
              type: "manual",
              message: value,
            });
          }
        });
      } else {
        const errorMessage =
          typeof error === "string"
            ? error
            : error instanceof Error
              ? error.message
              : apiError?.error || "Registration failed. Please try again.";
        toast.error(errorMessage);
      }
    } finally {
      setValue("cf_turnstile_response", "");
      turnstileRef.current?.reset();
    }
  };

  return {
    methods,
    onSubmit: handleSubmit(onSubmitHandler),
    showPassword,
    handleContinue,
    isSubmitting: methods.formState.isSubmitting,
    turnstileToken,
    onCaptchaSuccess: (token: string) =>
      setValue("cf_turnstile_response", token),
    onCaptchaExpire: () => setValue("cf_turnstile_response", ""),
    turnstileRef,
  };
}
