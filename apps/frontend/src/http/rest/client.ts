import { AxiosError, AxiosInstance } from "axios";

import { ApiError } from "@/http/errors";

import instance from "./instance";

// ----------------------------------------------------------------------

export interface RequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  [key: string]: unknown;
}

// ----------------------------------------------------------------------

export class Client {
  private httpInstance: AxiosInstance;

  constructor(httpInstance?: AxiosInstance) {
    this.httpInstance = httpInstance || instance;
  }

  async get<T = unknown>(url: string, config?: RequestConfig): Promise<T> {
    try {
      const response = await this.httpInstance.get<T>(url, config);
      return response.data;
    } catch (error) {
      throw this.parseError("GET", url, error);
    }
  }

  async post<T = unknown>(
    url: string,
    data?: unknown,
    config?: RequestConfig,
  ): Promise<T> {
    try {
      const response = await this.httpInstance.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.parseError("POST", url, error);
    }
  }

  async put<T = unknown>(
    url: string,
    data?: unknown,
    config?: RequestConfig,
  ): Promise<T> {
    try {
      const response = await this.httpInstance.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.parseError("PUT", url, error);
    }
  }

  async patch<T = unknown>(
    url: string,
    data?: unknown,
    config?: RequestConfig,
  ): Promise<T> {
    try {
      const response = await this.httpInstance.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.parseError("PATCH", url, error);
    }
  }

  async delete<T = unknown>(url: string, config?: RequestConfig): Promise<T> {
    try {
      const response = await this.httpInstance.delete<T>(url, config);
      return response.data;
    } catch (error) {
      throw this.parseError("DELETE", url, error);
    }
  }

  private parseError(method: string, url: string, error: unknown): ApiError {
    if (error instanceof AxiosError) {
      const statusCode = error.response?.status ?? 500;

      const message =
        (error.response?.data as Record<string, unknown>)?.message ??
        error.message ??
        "Unknown error occurred";

      const apiError = new ApiError(statusCode, method, url, String(message));

      this.logError(apiError);

      return apiError;
    }

    const apiError = new ApiError(500, method, url, "Unknown error occurred");
    this.logError(apiError);

    return apiError;
  }

  private logError(error: ApiError): void {
    console.error("[API ERROR]", error.toJSON());

    // For (Sentry, DataDog, etc.)
  }
}
