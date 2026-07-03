import { FormProvider, UseFormReturn } from "react-hook-form";

import { Button } from "@/shared/components/ui/button";

import { Field } from "@/shared/components/custom/form";

import { type ForgotPasswordState } from "@/modules/auth/hooks";

import { ForgotPasswordHeader } from "../primitives";

// ----------------------------------------------------------------------

interface ForgotPasswordFormProps {
  methods: UseFormReturn<any>;
  state: ForgotPasswordState;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
}

// ----------------------------------------------------------------------

export default function ForgotPasswordForm({
  methods,
  state,
  //
  onSubmit,
}: ForgotPasswordFormProps) {
  const isLoading = state === "loading";

  return (
    <>
      <ForgotPasswordHeader />

      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
          <Field.Input
            name="email"
            type="email"
            label="Email address"
            placeholder="you@example.com"
            inputClassName="rounded-none border-0 shadow-none border-b border-gray-300 focus-visible:ring-0 focus:border-black"
            disabled={isLoading}
          />

          <Button
            type="submit"
            className="w-full h-12 text-sm font-medium"
            disabled={isLoading}
          >
            {isLoading ? "Sending link..." : "Send reset link"}
          </Button>
        </form>
      </FormProvider>
    </>
  );
}
