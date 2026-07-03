import { FormProvider } from "react-hook-form";
import Link from "next/link";
import { Turnstile } from "nextjs-turnstile";

import { ROUTES } from "@/core/config";
import { Button } from "@/shared/components/ui/button";

import { OAuthProviders } from "../primitives";
import LoginFormFields from "./login-form-fields";

import { useLoginForm } from "@/modules/auth/hooks";

// ----------------------------------------------------------------------

export default function LoginForm() {
  const { methods, onSubmit } = useLoginForm();

  const {
    formState: { isSubmitting },
    setValue,
    watch,
  } = methods;

  const turnstileToken = watch("captcha_token");

  return (
    <>
      <header className="space-y-1 text-center">
        <h2 className="text-[2rem] font-semibold tracking-tight text-slate-900 sm:text-[2.15rem]">
          Welcome back
        </h2>

        <p className="mx-auto max-w-sm text-sm leading-6 text-slate-600">
          Sign in to continue where you left off.
        </p>
      </header>

      <OAuthProviders />

      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
          <LoginFormFields />

          <Turnstile
            onSuccess={(token) => setValue("captcha_token", token)}
            onExpire={() => setValue("captcha_token", "")}
          />

          <Button
            type="submit"
            className="h-11 w-full rounded-full bg-slate-900 text-[15px] font-semibold text-white shadow-none hover:bg-slate-800"
            disabled={isSubmitting || !turnstileToken}
          >
            {isSubmitting ? "Logging in..." : "Continue"}
          </Button>

          <p className="text-center text-sm text-slate-500">
            Don&apos;t have an account?{" "}
            <Link
              href={ROUTES.AUTH.REGISTER}
              className="font-medium text-slate-900 underline-offset-4 hover:underline"
            >
              Register
            </Link>
          </p>
        </form>
      </FormProvider>
    </>
  );
}
