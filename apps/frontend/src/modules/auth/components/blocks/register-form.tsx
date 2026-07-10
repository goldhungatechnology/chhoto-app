import { FormProvider } from "react-hook-form";
import { Turnstile } from "@marsidev/react-turnstile";

import { Button } from "@/shared/components/ui/button";

import { TURN_STILE_SITE_KEY } from "@/core/config";

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
    turnstileRef,
  } = useRegisterForm();

  return (
    <>
      <RegisterFormHeader />

      <OAuthProviders />

      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
          <RegisterFormFields showPassword={showPassword} />

          <Turnstile
            ref={turnstileRef}
            siteKey={TURN_STILE_SITE_KEY || ""}
            // options={{ size: "invisible" }}
            onSuccess={onCaptchaSuccess}
            onExpire={onCaptchaExpire}
          />

          <Button
            type={"submit"}
            onClick={handleContinue}
            className="h-11 w-full rounded-full bg-primary text-[15px] font-semibold text-white shadow-none hover:bg-primary-hover"
            disabled={isSubmitting || !turnstileToken}
          >
            {isSubmitting
              ? "Creating account..."
              : showPassword
                ? "Create account"
                : "Continue"}
          </Button>
          <RegisterTermsCheckbox />
        </form>
      </FormProvider>
    </>
  );
}
