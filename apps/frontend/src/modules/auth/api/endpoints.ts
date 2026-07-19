export const ENDPOINTS = {
  LOGIN: "/auth/login",
  REGISTER: "/auth/signup",
  VERIFY: "/auth/email/verify",
  RESEND_OTP: "/auth/email/resend",
  FORGOT_PASSWORD: "/auth/password/forgot",
  RESET_PASSWORD: "/auth/password/forgot/verify",
  ONBOARDING: "/auth/onboarding",
  ME: "/auth/me",
  PROFILE: "/auth/profile",
  LOGOUT: "/auth/logout",
  INTERFACE: "/auth/interface",
} as const;
