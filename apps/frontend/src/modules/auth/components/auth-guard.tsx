"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

import { useMe } from "../api/hooks/use-me";
import { ROUTES } from "@/core/config";

// ----------------------------------------------------------------------

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { data, isLoading, error } = useMe();

  useEffect(() => {
    if (isLoading) return;

    // 1. Session Expired or Unauthenticated
    if (error || !data?.data?.user) {
      if (!pathname.startsWith("/auth")) {
        router.replace(ROUTES.AUTH.LOGIN);
      }
      return;
    }

    const { is_email_verified, is_onboarded } = data.data.user;

    // 2. Email Verification Required
    if (!is_email_verified) {
      if (pathname !== ROUTES.AUTH.VERIFY) {
        router.replace(ROUTES.AUTH.VERIFY);
      }
      return;
    }

    // 3. Onboarding Required
    if (!is_onboarded) {
      if (pathname !== ROUTES.ONBOARDING.ROOT) {
        router.replace(ROUTES.ONBOARDING.ROOT);
      }
      return;
    }

    // 4. If user is on an auth page but fully authenticated, redirect to Dashboard
    if (
      pathname.startsWith("/auth") &&
      pathname !== ROUTES.ONBOARDING.ROOT &&
      pathname !== ROUTES.AUTH.VERIFY
    ) {
      router.replace(ROUTES.DASHBOARD.ROOT);
    }
  }, [data, isLoading, error, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-zinc-50 dark:bg-black min-h-screen">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-slate-900 dark:border-zinc-700 dark:border-t-zinc-50" />
          <p className="text-sm text-zinc-500 animate-pulse">
            Checking session...
          </p>
        </div>
      </div>
    );
  }

  // Prevent flash of protected content before redirect
  const isAuthPage = pathname.startsWith("/auth");
  const isVerified = data?.data?.user?.is_email_verified;
  const isOnboarded = data?.data?.user?.is_onboarded;

  if (!data?.data?.user && !isAuthPage) return null;
  if (!isVerified && pathname !== ROUTES.AUTH.VERIFY) return null;
  if (isVerified && !isOnboarded && pathname !== ROUTES.ONBOARDING.ROOT)
    return null;

  return <>{children}</>;
}
