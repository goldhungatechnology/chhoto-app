import axios, { AxiosInstance } from "axios";

import { API_BASE_URL } from "@/core/config/api";

import { setupInterceptors } from "./interceptors";

// ----------------------------------------------------------------------

const instance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

setupInterceptors(instance);

// ----------------------------------------------------------------------

export default instance;
