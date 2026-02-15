/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "hsl(var(--primary) / <alpha-value>)",
        primaryHover: "hsl(var(--primary-hover) / <alpha-value>)",
        background: "hsl(var(--background) / <alpha-value>)",
        accent: "hsl(var(--accent) / <alpha-value>)",
        secondary: "hsl(var(--secondary) / <alpha-value>)",
        grayed: "hsl(var(--grayed) / <alpha-value>)",
      },
      keyframes: {
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-5px)' },
          '75%': { transform: 'translateX(5px)' },
        },
      },
      animation: {
        shake: 'shake 0.2s ease-in-out 0s 2',
      },
    },
  },
  plugins: [],
};
