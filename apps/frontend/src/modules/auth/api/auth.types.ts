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
  data: AuthUser;
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
  email: string;
  verification_token: string;
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
