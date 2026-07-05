import { AxiosInstance } from "axios";

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
      throw error;
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
      throw error;
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
      throw error;
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
      throw error;
    }
  }

  async delete<T = unknown>(url: string, config?: RequestConfig): Promise<T> {
    try {
      const response = await this.httpInstance.delete<T>(url, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}
