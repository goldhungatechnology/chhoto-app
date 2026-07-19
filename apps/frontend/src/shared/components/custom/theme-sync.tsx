"use client";

import { useEffect, useRef } from "react";
import { useTheme } from "next-themes";
import { useMe } from "@/modules/auth/api/hooks";

export function ThemeSync() {
  const { theme, setTheme } = useTheme();
  const { data } = useMe();
  const hasSyncedRef = useRef(false);

  // Sync user theme preference from backend when available
  useEffect(() => {
    const userTheme = data?.data?.user?.onboarding_details?.theme;
    if (userTheme && (userTheme === "light" || userTheme === "dark")) {
      if (!hasSyncedRef.current && theme !== userTheme) {
        setTheme(userTheme);
        hasSyncedRef.current = true;
      }
    }
  }, [data, theme, setTheme]);

  // Reset sync status when the user changes (e.g. log out / log in as a different user)
  const userUuid = data?.data?.user?.uuid;
  useEffect(() => {
    hasSyncedRef.current = false;
  }, [userUuid]);

  return null;
}
