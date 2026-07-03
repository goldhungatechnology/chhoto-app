"use client";

import { useEffect, useState } from "react";
import { useFormContext, useWatch } from "react-hook-form";

import {
  evaluatePasswordStrength,
  type PasswordStrengthResult,
} from "@/shared/lib/password-strength";

// ----------------------------------------------------------------------

interface UsePasswordStrengthOptions {
  fieldName?: string;
}

// ----------------------------------------------------------------------

export function usePasswordStrength(
  options: UsePasswordStrengthOptions = {},
): PasswordStrengthResult | null {
  const { fieldName = "password" } = options;

  const { control } = useFormContext();

  const password = useWatch({ control, name: fieldName });

  const [strengthResult, setStrengthResult] =
    useState<PasswordStrengthResult | null>(null);

  useEffect(() => {
    if (!password || password.length === 0) {
      setStrengthResult(null);
      return;
    }

    const result = evaluatePasswordStrength(password);
    setStrengthResult(result);
  }, [password]);

  return strengthResult;
}
