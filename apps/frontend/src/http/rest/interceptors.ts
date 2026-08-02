import type {
  AxiosInstance,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";

// ----------------------------------------------------------------------

const DEFAULT_ERROR_MESSAGE = "Something went wrong. Please try again.";

export interface NormalizedApiError {
  message: string;
  error?: string;
  errors?: unknown;
  status?: number;
}

// ----------------------------------------------------------------------

export const setupInterceptors = (instance: AxiosInstance): void => {
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      return config;
    },

    (error: AxiosError) => {
      return Promise.reject(error);
    },
  );

  instance.interceptors.response.use(
    (response: AxiosResponse) => response,

    (error: AxiosError) => {
      const payload = error.response?.data as
        | { message?: string; error?: string; errors?: unknown }
        | undefined;

      const normalized: NormalizedApiError = {
        message: payload?.error || payload?.message || DEFAULT_ERROR_MESSAGE,
        error: payload?.error,
        errors: payload?.errors,
        status: error.response?.status,
      };

      return Promise.reject(normalized);
    },
  );
};
