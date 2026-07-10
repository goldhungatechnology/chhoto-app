import { RefreshCw } from "lucide-react";

import { Button } from "@/shared/components/ui/button";
import { Logo } from "@/shared/components/custom/logo";

import { useVerifyForm } from "@/modules/auth/hooks";

import {
  ErrorAlert,
  VerifySuccess,
  VerifyHeader,
  VerifyActions,
  VerifyOtpInput,
  VerifyFooter,
} from "../primitives";

// ----------------------------------------------------------------------

export default function VerifyForm() {
  const {
    otp,
    state,
    errorMessage,
    resendCooldown,
    userEmail,
    isVerifying,
    isOtpComplete,
    //
    handleOtpChange,
    handleVerify,
    handleResend,
  } = useVerifyForm();

  const isDisabled = isVerifying || state === "success";

  return (
    <div className="min-h-screen py-6 flex items-center justify-center">
      <section className="flex flex-col gap-6">
        <header className="w-full px-4 sm:px-6 flex justify-center">
          <Logo variant="md" />
        </header>

        <main className="">
          {state === "success" ? (
            <VerifySuccess />
          ) : (
            <div className="space-y-6">
              <VerifyHeader email={userEmail} />

              <div className="space-y-4">
                <VerifyOtpInput
                  value={otp}
                  disabled={isDisabled}
                  hasError={state === "error"}
                  onChange={handleOtpChange}
                />

                {state === "error" && errorMessage && (
                  <ErrorAlert message={errorMessage} />
                )}
              </div>

              <Button
                size="lg"
                disabled={!isOtpComplete || isDisabled}
                className="w-full h-12 text-base font-medium rounded-lg shadow-sm"
                onClick={handleVerify}
              >
                {isVerifying ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  "Verify Account"
                )}
              </Button>

              <VerifyActions
                resendCooldown={resendCooldown}
                onResend={handleResend}
              />
            </div>
          )}
        </main>

        <VerifyFooter />
      </section>
    </div>
  );
}
