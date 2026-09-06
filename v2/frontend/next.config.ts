import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  async rewrites() {
    return [
      {
        source: '/_internal/revalidate',
        destination: '/isr/revalidate',
      },
    ];
  },
};

export default nextConfig;
