import Link from "next/link";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/shared/components/ui/button";

import { ROUTES } from "@/core/config";

// ----------------------------------------------------------------------

export default function ResetPasswordError() {
  return (
    <>
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-50 border border-red-100">
        <AlertTriangle size={22} className="text-red-500" />
      </div>

      <header className="flex flex-col gap-1.5">
        <h2 className="text-2xl font-semibold tracking-tight">Link expired</h2>

        <p className="text-sm text-muted-foreground leading-relaxed">
          This password reset link is no longer valid.
        </p>
      </header>

      <div className="flex flex-col gap-3">
        <Button asChild className="w-full h-12 text-sm font-medium">
          <Link href={ROUTES.AUTH.FORGOT_PASSWORD}>Request a new link</Link>
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
