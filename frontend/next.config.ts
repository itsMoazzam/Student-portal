const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_BASE_URL: 'http://localhost:8000/api',
  },
};

module.exports = nextConfig;
