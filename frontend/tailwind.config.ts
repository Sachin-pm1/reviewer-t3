import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0f1115",
        panel: "#171a21",
        "panel-2": "#1e222b",
        border: "#2a2f3a",
        muted: "#9aa3b2",
        accent: "#5b8cff",
        "accent-2": "#34d399",
        danger: "#f87171",
        warn: "#fbbf24",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "Cascadia Code",
          "Consolas",
          "monospace",
        ],
      },
      borderRadius: {
        DEFAULT: "10px",
      },
    },
  },
  plugins: [],
};

export default config;
