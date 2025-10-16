/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8765',
    ORGANISM_API_URL: process.env.ORGANISM_API_URL || 'http://localhost:5000',
  },
  async rewrites() {
    return [
      {
        source: '/api/organism/:path*',
        destination: `${process.env.ORGANISM_API_URL || 'http://localhost:5000'}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
