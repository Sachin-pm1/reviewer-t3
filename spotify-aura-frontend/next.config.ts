import type { NextConfig } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

const nextConfig: NextConfig = {
  async rewrites() {
    // Proxy /api/* to the backend so the browser only ever talks to one
    // origin — no CORS to configure on the client, same pattern as the main
    // repo's frontend/next.config.ts.
    return [
      {
        source: "/api/:path*",
        destination: `${API_BASE}/:path*`,
      },
    ];
  },
};

export default nextConfig;
