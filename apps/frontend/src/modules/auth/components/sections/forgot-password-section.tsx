"use client";

import { ROUTES } from "@/core/config";

import { useForgotPasswordForm } from "@/modules/auth/hooks";

import {
  CenteredAuthLayout,
  ForgotPasswordForm,
  ForgotPasswordEmailSent,
} from "../blocks";

export default function ForgotPasswordSection() {
  const { methods, onSubmit, state, submittedEmail, handleResend } =
    useForgotPasswordForm();

  const isSent = state === "sent";

  return (
    <CenteredAuthLayout backHref={ROUTES.AUTH.LOGIN} backLabel="Back to login">
      {isSent ? (
        <ForgotPasswordEmailSent
          submittedEmail={submittedEmail}
          state={state}
          //
          onResend={handleResend}
        />
      ) : (
        <ForgotPasswordForm
          methods={methods}
          state={state}
          //
          onSubmit={onSubmit}
        />
      )}
    </CenteredAuthLayout>
  );
}
