"use client";

import { useForm, UseFormReturn, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";

import { ROUTES } from "@/core/config";
import { localStorageAdapter, STORAGE_KEYS } from "@/core/local-storage";

import { useRegister } from "@/modules/auth/api/hooks";

import { toast } from "@/shared/components/custom/snackbar";

import { evaluatePasswordStrength } from "@/shared/lib/password-strength";

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

function deriveNameParts(email: string) {
  const localPart = email.split("@")[0] ?? "";
  const cleaned = localPart
    .replace(/[._-]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  const capitalize = (value: string) =>
    value ? `${value.charAt(0).toUpperCase()}${value.slice(1)}` : "User";

  const fallback = localPart || "User";
  const firstName = capitalize(cleaned[0] ?? fallback);
  const lastName = capitalize(cleaned[1] ?? cleaned[0] ?? fallback);

  return {
    first_name: firstName,
    last_name: lastName,
  };
}

// ----------------------------------------------------------------------

interface UseRegisterFormReturn {
  methods: UseFormReturn<RegisterFormValues>;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
}

// ----------------------------------------------------------------------

export function useRegisterForm(): UseRegisterFormReturn {
  const router = useRouter();

  const { registerAsync } = useRegister();

  const methods = useForm<RegisterFormValues>({
    resolver: zodResolver(Schema as never),
    defaultValues,
  });

  const { reset, handleSubmit, setError } = methods;

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
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Registration failed. Please try again.";

      if (errorMessage.startsWith("Email")) {
        setError("email", {
          type: "server",
          message: errorMessage,
        });
      } else {
        toast.error(errorMessage);
      }
    }
  };

  return {
    methods: methods,
    onSubmit: handleSubmit(onSubmitHandler),
  };
}
