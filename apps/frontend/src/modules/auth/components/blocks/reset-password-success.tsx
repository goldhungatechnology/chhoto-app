import Link from "next/link";
import { ShieldCheck } from "lucide-react";

import { Button } from "@/shared/components/ui/button";

import { ROUTES } from "@/core/config";

// ----------------------------------------------------------------------

export default function ResetPasswordSuccess() {
  return (
    <>
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-green-50 border border-green-100">
        <ShieldCheck size={22} className="text-green-600" />
      </div>

      <header className="flex flex-col gap-1.5">
        <h2 className="text-2xl font-semibold tracking-tight">
          Password updated
        </h2>

        <p className="text-sm text-muted-foreground leading-relaxed">
          Your password has been reset successfully. You can now sign in with
          your new password.
        </p>
      </header>

      <Button asChild className="w-full h-12 text-sm font-medium">
        <Link href={ROUTES.AUTH.LOGIN}>Continue to login</Link>
      </Button>
    </>
  );
}
