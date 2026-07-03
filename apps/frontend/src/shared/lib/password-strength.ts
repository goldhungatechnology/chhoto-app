export type PasswordStrength = "weak" | "medium" | "strong";

// ----------------------------------------------------------------------

export interface PasswordStrengthResult {
  strength: PasswordStrength;
  score: number;
  feedback: string[];
  hasMinLength: boolean;
  hasUpperCase: boolean;
  hasLowerCase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
}

// ----------------------------------------------------------------------

const MIN_LENGTH = 8;
const STRONG_MIN_SCORE = 5;
const MEDIUM_MIN_SCORE = 3;

// ----------------------------------------------------------------------

export function evaluatePasswordStrength(
  password: string,
): PasswordStrengthResult {
  const feedback: string[] = [];
  let score = 0;

  const hasMinLength = password.length >= MIN_LENGTH;
  if (hasMinLength) {
    score++;
  } else {
    feedback.push(`At least ${MIN_LENGTH} characters`);
  }

  const hasUpperCase = /[A-Z]/.test(password);
  if (hasUpperCase) {
    score++;
  } else {
    feedback.push("At least one uppercase letter");
  }

  const hasLowerCase = /[a-z]/.test(password);
  if (hasLowerCase) {
    score++;
  } else {
    feedback.push("At least one lowercase letter");
  }

  const hasNumber = /\d/.test(password);
  if (hasNumber) {
    score++;
  } else {
    feedback.push("At least one number");
  }

  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  if (hasSpecialChar) {
    score++;
  } else {
    feedback.push("At least one special character");
  }

  // Bonus point for extra length beyond minimum
  if (password.length >= 12) {
    score++;
  }

  let strength: PasswordStrength;

  if (score >= STRONG_MIN_SCORE) {
    strength = "strong";
  } else if (score >= MEDIUM_MIN_SCORE) {
    strength = "medium";
  } else {
    strength = "weak";
  }

  return {
    strength,
    score,
    feedback,
    //
    hasMinLength,
    hasUpperCase,
    hasLowerCase,
    hasNumber,
    hasSpecialChar,
  };
}
