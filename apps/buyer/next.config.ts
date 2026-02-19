import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/identity/:path*",
        destination: "http://localhost:8001/:path*",
      },
      {
        source: "/api/course/:path*",
        destination: "http://localhost:8002/:path*",
      },
    ];
  },
};

export default nextConfig;
