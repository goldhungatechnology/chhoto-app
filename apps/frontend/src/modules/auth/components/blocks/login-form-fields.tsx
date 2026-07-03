import { Controller, useFormContext } from "react-hook-form";

import { ROUTES } from "@/core/config";

import { Checkbox } from "@/shared/components/ui/checkbox";
import { Field as ShadcnField } from "@/shared/components/ui/field";
import { Label } from "@/shared/components/ui/label";
import { Field } from "@/shared/components/custom/form";

// ----------------------------------------------------------------------

export default function LoginFormFields() {
  const { control } = useFormContext();

  return (
    <>
      <Field.Input
        name="email"
        label="Email"
        placeholder="Enter email address"
        inputClassName="h-11 rounded-xl border-slate-200 bg-white text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0"
      />

      <Field.PasswordInput
        name="password"
        label="Password"
        placeholder="Enter password"
        inputClassName="h-11 rounded-xl border-slate-200 bg-white text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0"
      />

      <div className="flex items-center justify-between gap-4 text-slate-600">
        <Controller
          name="remember_me"
          control={control}
          render={({ field }) => (
            <ShadcnField orientation="horizontal">
              <Checkbox
                id="remember_me"
                checked={field.value}
                onCheckedChange={field.onChange}
              />

              <Label
                htmlFor="remember_me"
                className="cursor-pointer text-sm text-slate-600 transition-colors hover:text-slate-900"
              >
                Remember me
              </Label>
            </ShadcnField>
          )}
        />

        <a
          href={ROUTES.AUTH.FORGOT_PASSWORD}
          className="shrink-0 text-sm text-slate-500 underline-offset-4 transition-colors duration-200 hover:text-slate-900 hover:underline"
        >
          Forgot your password?
        </a>
      </div>
    </>
  );
}
