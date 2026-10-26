import type { NextConfig } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    // Proxy all /api/* calls to the FastAPI backend so the browser never
    // touches the API origin directly (no CORS issues, no hardcoded port
    // in production images).
    return [
      {
        source: "/api/:path*",
        destination: `${API_BASE}/:path*`,
      },
    ];
  },
};

export default nextConfig;
