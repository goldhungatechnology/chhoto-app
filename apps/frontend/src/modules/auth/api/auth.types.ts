export interface AuthUser {
  uuid: string;
  email: string;
  username: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  captcha_token: string;
}

export interface LoginResponse {
  data?: {
    mfa_required?: boolean;
    temp_token?: string;
    session_uuid?: string;
    user?: AuthUser;
  };
  message: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
  captcha_token: string;
}

export interface RegisterResponse {
  message: string;
  data: AuthUser;
}

export interface VerifyRequest {
  token: string;
}

export interface VerifyResponse {
  message: string;
}

export interface ResendOtpRequest {
  email: string;
  type?: string;
}

export interface ResendOtpResponse {
  message: string;
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

export interface OnboardingRequest {
  full_name: string;
  theme: "light" | "dark";
  referral_source: string;
}

export interface OnboardingResponse {
  message: string;
  data?: unknown;
}

export interface Country {
  uuid: string;
  name: string;
  iso_code_2: string;
  iso_code_3: string;
  phone_code: string | null;
}

export interface UserDetails {
  uuid: string;
  email: string;
  username: string | null;
  full_name: string | null;
  avatar: string | null;
  email_verified_at: string | null;
  is_online: boolean;
  avatar_bg: string | null;
  is_onboarded: boolean;
  is_email_verified: boolean;
  phone_number: string | null;
  country: Country | null;
  onboarding_details?: {
    theme: string;
  };
}

export interface MeResponse {
  data: {
    user: UserDetails;
    organizations: unknown;
    current_organization: unknown;
    security: {
      last_password_changed_at: string | null;
      mfa_enabled: boolean;
    };
  };
  message: string;
}

export interface UpdateProfileRequest {
  full_name?: string | null;
  avatar?: string | null;
  avatar_bg?: string | null;
  phone_number?: string | null;
  country_uuid?: string | null;
}

export interface UpdateProfileResponse {
  data: {
    user: UserDetails;
  };
  message: string;
}

export interface InterfaceSetupRequest {
  theme: "light" | "dark";
  language: string;
}

export interface InterfaceSetupResponse {
  message: string;
}

export interface SetupMfaResponse {
  data: {
    secret: string;
    auth_url: string;
  };
  message: string;
}

export interface ConfirmMfaRequest {
  otp_code: string;
}

export interface ConfirmMfaResponse {
  data?: {
    verified?: boolean;
    recovery_codes?: string[];
  };
  message: string;
}

export interface DisableMfaRequest {
  password: string;
}

export interface DisableMfaResponse {
  message: string;
}

export interface VerifyMfaRequest {
  temp_token: string;
  otp_code?: string;
  recovery_code?: string;
}

export interface VerifyMfaResponse {
  message: string;
}

export interface UserSession {
  session_uuid: string;
  uuid?: string;
  user_id?: number | null;
  ip_address: string | null;
  device: string | null;
  browser: string | null;
  is_current: boolean;
  status?: string;
  created_at: string;
  city: string | null;
  country: string | null;
  country_code: string | null;
}

export interface SessionsResponse {
  data: UserSession[];
  message: string;
}

export interface RevokeSessionRequest {
  session_uuid: string;
}

export interface RevokeSessionResponse {
  message: string;
}

export interface RevokeAllSessionsRequest {
  keep_current_session: boolean;
}

export interface RevokeAllSessionsResponse {
  message: string;
}
