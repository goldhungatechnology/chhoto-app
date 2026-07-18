import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  allowedDevOrigins: [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://auth.chhoto.tech",
    "https://chhoto.tech",
    "https://app.chhoto.tech",
  ],
};

export default nextConfig;
