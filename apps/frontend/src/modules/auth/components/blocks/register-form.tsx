import { FormProvider } from "react-hook-form";
import Link from "next/link";
import { Turnstile } from "@marsidev/react-turnstile";

import { Button } from "@/shared/components/ui/button";

import { ROUTES, TURN_STILE_SITE_KEY } from "@/core/config";

import { OAuthProviders, RegisterFormHeader } from "../primitives";
import RegisterFormFields from "./register-form-fields";
import RegisterTermsCheckbox from "./register-terms-checkbox";

import { useRegisterForm } from "@/modules/auth/hooks";

// ----------------------------------------------------------------------

export default function RegisterForm() {
  const {
    methods,
    onSubmit,
    showPassword,
    handleContinue,
    isSubmitting,
    turnstileToken,
    onCaptchaSuccess,
    onCaptchaExpire,
  } = useRegisterForm();

  return (
    <>
      <RegisterFormHeader />

      <OAuthProviders />

      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
          <RegisterFormFields showPassword={showPassword} />

          <Turnstile
            siteKey={TURN_STILE_SITE_KEY || ""}
            options={{ size: "invisible" }}
            onSuccess={onCaptchaSuccess}
            onExpire={onCaptchaExpire}
          />

          <Button
            type={showPassword ? "submit" : "button"}
            onClick={showPassword ? undefined : handleContinue}
            className="h-11 w-full rounded-full bg-primary text-[15px] font-semibold text-white shadow-none hover:bg-primary-hover"
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
              className="font-medium text-primary underline-offset-4 hover:underline"
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
