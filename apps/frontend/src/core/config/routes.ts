export const ROUTES = {
  AUTH: {
    LOGIN: "/login",
    REGISTER: "/register",
    FORGOT_PASSWORD: "/forgot-password",
    RESET_PASSWORD: "/reset-password",
    VERIFY: "/verify",
  },

  ONBOARDING: {
    ROOT: "/onboarding",
  },

  DASHBOARD: {
    ROOT: "/",

    SETTINGS: {
      ROOT: "/settings",
      ACCOUNT: "/settings/account",
      SECURITY: "/settings/security",
      APPEARANCE: "/settings/appearance",
    },
  },
} as const;
