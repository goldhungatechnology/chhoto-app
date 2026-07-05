import Link from "next/link";
import { MailOpen } from "lucide-react";

import { Button } from "@/shared/components/ui/button";

import { ROUTES } from "@/core/config";

import { type ForgotPasswordState } from "@/modules/auth/hooks";

import { ForgotPasswordHeader } from "../primitives";

// ----------------------------------------------------------------------

interface ForgotPasswordEmailSentProps {
  submittedEmail: string;
  state: ForgotPasswordState;
  onResend: () => Promise<void>;
}

// ----------------------------------------------------------------------

export default function ForgotPasswordEmailSent({
  submittedEmail,
  state,
  //
  onResend,
}: ForgotPasswordEmailSentProps) {
  const isLoading = state === "loading";

  return (
    <>
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-green-50 border border-green-100">
        <MailOpen size={22} className="text-green-600" />
      </div>

      <ForgotPasswordHeader isSent />

      {submittedEmail && (
        <p className="text-sm text-muted-foreground">
          We sent the link to{" "}
          <span className="font-medium text-foreground">{submittedEmail}</span>.
          Be sure to check your spam folder if you don&apos;t see it.
        </p>
      )}

      <div className="flex flex-col gap-3">
        <Button
          type="button"
          variant="outline"
          className="w-full h-12 text-sm font-medium"
          disabled={isLoading}
          onClick={onResend}
        >
          {isLoading ? "Resending..." : "Resend email"}
        </Button>

        <Link
          href={ROUTES.AUTH.LOGIN}
          className="text-center text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline transition-colors"
        >
          Back to login
        </Link>
      </div>
    </>
  );
}
