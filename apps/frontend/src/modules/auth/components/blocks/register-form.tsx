import { useState } from "react";
import { FormProvider, useWatch } from "react-hook-form";
import Link from "next/link";
import { Turnstile } from "nextjs-turnstile";

import { Button } from "@/shared/components/ui/button";

import { ROUTES } from "@/core/config";

import { OAuthProviders, RegisterFormHeader } from "../primitives";
import RegisterFormFields from "./register-form-fields";
import RegisterTermsCheckbox from "./register-terms-checkbox";

import { useRegisterForm } from "@/modules/auth/hooks";

// ----------------------------------------------------------------------

export default function RegisterForm() {
  const { methods, onSubmit } = useRegisterForm();
  const [showPassword, setShowPassword] = useState(false);

  const {
    formState: { isSubmitting },
    trigger,
    setFocus,
    setValue,
    watch,
    control,
  } = methods;

  const turnstileToken = useWatch({ control, name: "cf_turnstile_response" });

  console.log("Turnstile token:", turnstileToken);

  const handleContinue = async () => {
    const isEmailValid = await trigger("email");

    if (!isEmailValid) {
      return;
    }

    setShowPassword(true);
    setFocus("password");
  };

  return (
    <>
      <RegisterFormHeader />

      <OAuthProviders />

      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
          <RegisterFormFields showPassword={showPassword} />

          <Turnstile
            onSuccess={(token) => setValue("cf_turnstile_response", token)}
            onExpire={() => setValue("cf_turnstile_response", "")}
          />

          <Button
            type={showPassword ? "submit" : "button"}
            onClick={showPassword ? undefined : handleContinue}
            className="h-11 w-full rounded-full bg-slate-900 text-[15px] font-semibold text-white shadow-none hover:bg-slate-800"
            disabled={isSubmitting || (showPassword && !turnstileToken)}
          >
            {isSubmitting
              ? "Creating account..."
              : showPassword
                ? "Create account"
                : "Continue"}
          </Button>

          <p className="text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link
              href={ROUTES.AUTH.LOGIN}
              className="font-medium text-slate-900 underline-offset-4 hover:underline"
            >
              Login
            </Link>
          </p>

          {showPassword && <RegisterTermsCheckbox />}
        </form>
      </FormProvider>
    </>
  );
}
