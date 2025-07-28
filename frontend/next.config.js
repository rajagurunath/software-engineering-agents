/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['img.youtube.com', 'github.com', 'raw.githubusercontent.com'],
  },
}

module.exports = nextConfig