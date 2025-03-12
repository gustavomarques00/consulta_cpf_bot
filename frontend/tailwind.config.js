/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}", // Pasta app/
    "./components/**/*.{js,ts,jsx,tsx}", // Componentes
    "./pages/**/*.{js,ts,jsx,tsx}" // Se estiver usando pages/
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
