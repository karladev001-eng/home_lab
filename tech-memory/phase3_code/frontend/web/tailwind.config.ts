import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
        accent: {
          teal: "#14b8a6",
          "teal-light": "#99f6e4",
          orange: "#f97316",
          "orange-light": "#fed7aa",
        },
        neutral: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          850: "#172032",
          900: "#0f172a",
          950: "#020617",
        },
        surface: {
          DEFAULT: "#1e293b",
          elevated: "#334155",
        },
        semantic: {
          success: "#22c55e",
          warning: "#f59e0b",
          error: "#ef4444",
          info: "#3b82f6",
        },
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans JP", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Cascadia Code", "monospace"],
      },
      boxShadow: {
        card: "0 4px 24px rgba(0,0,0,0.3)",
      },
      maxWidth: {
        content: "900px",
      },
      height: {
        nav: "56px",
      },
      width: {
        sidebar: "260px",
      },
    },
  },
  plugins: [],
};

export default config;
