import type { Client } from "@/http/rest";

import type {
  LoginRequest,
  LoginResponse,
  //
  RegisterRequest,
  RegisterResponse,
  //
  VerifyRequest,
  VerifyResponse,
  //
  ResendOtpRequest,
  ResendOtpResponse,
  //
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  //
  ResetPasswordRequest,
  ResetPasswordResponse,
  //
  OnboardingRequest,
  OnboardingResponse,
  //
  MeResponse,
  UpdateProfileRequest,
  UpdateProfileResponse,
  InterfaceSetupRequest,
  InterfaceSetupResponse,
  SetupMfaResponse,
  ConfirmMfaRequest,
  ConfirmMfaResponse,
  DisableMfaRequest,
  DisableMfaResponse,
  VerifyMfaRequest,
  VerifyMfaResponse,
  SessionsResponse,
  RevokeSessionRequest,
  RevokeSessionResponse,
  RevokeAllSessionsRequest,
  RevokeAllSessionsResponse,
} from "./auth.types";

import { ENDPOINTS } from "./endpoints";

// ----------------------------------------------------------------------

export class AuthApi {
  private client: Client;

  constructor(client: Client) {
    this.client = client;
  }

  login = (payload: LoginRequest): Promise<LoginResponse> => {
    return this.client.post<LoginResponse>(ENDPOINTS.LOGIN, payload);
  };

  register = (payload: RegisterRequest): Promise<RegisterResponse> => {
    return this.client.post<RegisterResponse>(ENDPOINTS.REGISTER, payload);
  };

  verify = (payload: VerifyRequest): Promise<VerifyResponse> => {
    return this.client.post<VerifyResponse>(ENDPOINTS.VERIFY, payload);
  };

  resendOtp = (payload: ResendOtpRequest): Promise<ResendOtpResponse> => {
    return this.client.post<ResendOtpResponse>(ENDPOINTS.RESEND_OTP, payload);
  };

  forgotPassword = (
    payload: ForgotPasswordRequest,
  ): Promise<ForgotPasswordResponse> => {
    return this.client.post<ForgotPasswordResponse>(
      ENDPOINTS.FORGOT_PASSWORD,
      payload,
    );
  };

  resetPassword = (
    payload: ResetPasswordRequest,
  ): Promise<ResetPasswordResponse> => {
    return this.client.post<ResetPasswordResponse>(
      ENDPOINTS.RESET_PASSWORD,
      payload,
    );
  };

  onboarding = (
    payload: OnboardingRequest,
  ): Promise<OnboardingResponse> => {
    return this.client.post<OnboardingResponse>(
      ENDPOINTS.ONBOARDING,
      payload,
    );
  };

  me = (): Promise<MeResponse> => {
    return this.client.get<MeResponse>(ENDPOINTS.ME);
  };

  updateProfile = (
    payload: UpdateProfileRequest,
  ): Promise<UpdateProfileResponse> => {
    return this.client.patch<UpdateProfileResponse>(
      ENDPOINTS.PROFILE,
      payload,
    );
  };

  interfaceSetup = (
    payload: InterfaceSetupRequest,
  ): Promise<InterfaceSetupResponse> => {
    return this.client.put<InterfaceSetupResponse>(
      ENDPOINTS.INTERFACE,
      payload,
    );
  };

  logout = (): Promise<void> => {
    return this.client.post<void>(ENDPOINTS.LOGOUT);
  };

  setupMfa = (): Promise<SetupMfaResponse> => {
    return this.client.post<SetupMfaResponse>(ENDPOINTS.MFA_SETUP);
  };

  confirmMfa = (payload: ConfirmMfaRequest): Promise<ConfirmMfaResponse> => {
    return this.client.post<ConfirmMfaResponse>(ENDPOINTS.MFA_CONFIRM, payload);
  };

  disableMfa = (payload: DisableMfaRequest): Promise<DisableMfaResponse> => {
    return this.client.post<DisableMfaResponse>(ENDPOINTS.MFA_DISABLE, payload);
  };

  verifyMfa = (payload: VerifyMfaRequest): Promise<VerifyMfaResponse> => {
    return this.client.post<VerifyMfaResponse>(ENDPOINTS.MFA_VERIFY, payload);
  };

  getSessions = (): Promise<SessionsResponse> => {
    return this.client.get<SessionsResponse>(ENDPOINTS.SESSIONS);
  };

  revokeSession = (
    payload: RevokeSessionRequest,
  ): Promise<RevokeSessionResponse> => {
    return this.client.post<RevokeSessionResponse>(
      ENDPOINTS.SESSIONS_REVOKE,
      payload,
    );
  };

  revokeAllSessions = (
    payload: RevokeAllSessionsRequest,
  ): Promise<RevokeAllSessionsResponse> => {
    return this.client.post<RevokeAllSessionsResponse>(
      ENDPOINTS.SESSIONS_REVOKE_ALL,
      payload,
    );
  };
}
