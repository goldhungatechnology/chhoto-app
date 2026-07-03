import { FormProvider, UseFormReturn } from "react-hook-form";

import { Button } from "@/shared/components/ui/button";

import { type ResetPasswordState } from "@/modules/auth/hooks";

import { ResetPasswordHeader } from "../primitives";
import ResetPasswordFormFields from "./reset-password-form-fields";

// ----------------------------------------------------------------------

interface ResetPasswordFormProps {
  methods: UseFormReturn<any>;
  state: ResetPasswordState;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
}

// ----------------------------------------------------------------------

export default function ResetPasswordForm({
  methods,
  state,
  //
  onSubmit,
}: ResetPasswordFormProps) {
  const isLoading = state === "loading";

  return (
    <>
      <ResetPasswordHeader />

      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
          <ResetPasswordFormFields />

          <Button
            type="submit"
            className="w-full h-12 text-sm font-medium"
            disabled={isLoading}
          >
            {isLoading ? "Updating password..." : "Update password"}
          </Button>
        </form>
      </FormProvider>
    </>
  );
}
