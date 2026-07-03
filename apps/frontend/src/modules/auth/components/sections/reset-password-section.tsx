"use client";

import { useSearchParams } from "next/navigation";

import { ROUTES } from "@/core/config";

import { useResetPasswordForm } from "@/modules/auth/hooks";

import {
  CenteredAuthLayout,
  ResetPasswordForm,
  ResetPasswordSuccess,
  ResetPasswordError,
} from "../blocks";

export default function ResetPasswordSection() {
  const searchParams = useSearchParams();

  const token = searchParams.get("token");

  const { methods, onSubmit, state } = useResetPasswordForm(token);

  const renderContent = () => {
    switch (state) {
      case "success":
        return <ResetPasswordSuccess />;

      case "invalid_token":
        return <ResetPasswordError />;

      default:
        return (
          <ResetPasswordForm
            methods={methods}
            state={state}
            //
            onSubmit={onSubmit}
          />
        );
    }
  };

  return (
    <CenteredAuthLayout
      backHref={
        state === "idle" || state === "loading" ? ROUTES.AUTH.LOGIN : undefined
      }
      backLabel="Back to login"
    >
      {renderContent()}
    </CenteredAuthLayout>
  );
}
