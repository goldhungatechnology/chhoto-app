"use client";

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

  if (!password || password.length === 0) {
    return null;
  }

  return evaluatePasswordStrength(password);
}
