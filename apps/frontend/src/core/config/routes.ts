export const ROUTES = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    FORGOT_PASSWORD: "/auth/forgot-password",
    RESET_PASSWORD: "/auth/reset-password",
    VERIFY: "/auth/verify",
  },

  ONBOARDING: {
    ROOT: "/auth/onboarding",
  },

  LINKS: "/links",

  DASHBOARD: {
    ROOT: "/dashboard",
  },
} as const;
