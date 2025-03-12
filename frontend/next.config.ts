import path from 'path';

const nextConfig = {
  reactStrictMode: true, // Habilitar modo estrito para evitar erros no React
  webpack(config: any) {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'app'), // Define o alias "@"
    };
    return config;
  },
};

export default nextConfig;
