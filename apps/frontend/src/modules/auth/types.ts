export interface AuthRequest {
  email: string;
  password: string;
  captcha_token: string;
}

export interface User {
  uuid: string;
  email: string;
  username: string;
  email_verified: boolean;
  is_onboarded: boolean;
  created_at: string;
}

export type AuthErrorCode =
  | "EMAIL_UNVERIFIED"
  | "ONBOARDING_REQUIRED"
  | "INVALID_CREDENTIALS";

export interface AuthErrorResponse {
  code: AuthErrorCode;
  [key: string]: unknown;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}

export interface ResetPasswordResponse {
  message: string;
}
