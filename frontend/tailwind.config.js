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
    },
  },
  plugins: [],
};
