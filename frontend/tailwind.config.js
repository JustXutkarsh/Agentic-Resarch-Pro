/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        research: {
          bg: "#F6F5F1",
          paper: "#FFFFFF",
          primary: "#17181C",
          ink: "#101114",
          secondary: "#575861",
          muted: "#8A8B91",
          border: "#E2E0D8",
          borderLight: "#EDECE7",
          blue: "#315BFF",
          deepBlue: "#2146D8",
          green: "#168463",
          greenLight: "#E8F5F0",
          warning: "#C88A16",
          warningLight: "#FEF7EB",
          coral: "#D85D4A",
          coralLight: "#FDF0EE",
          surface: "#F0EFEA",
        },
      },
      fontFamily: {
        sans: ["'Space Grotesk'", "sans-serif"],
        serif: ["'Instrument Serif'", "Georgia", "serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      maxWidth: {
        instrument: "1220px",
      },
      boxShadow: {
        subtle: "0 1px 3px rgba(16, 17, 20, 0.04), 0 4px 12px rgba(16, 17, 20, 0.03)",
        card: "0 2px 8px rgba(16, 17, 20, 0.05), 0 12px 28px rgba(16, 17, 20, 0.04)",
        cardHover: "0 8px 24px rgba(16, 17, 20, 0.08), 0 20px 48px rgba(49, 91, 255, 0.08)",
        composer: "0 4px 20px rgba(16, 17, 20, 0.06), 0 1px 2px rgba(16, 17, 20, 0.04)",
        composerFocus: "0 0 0 3px rgba(49, 91, 255, 0.15), 0 8px 30px rgba(49, 91, 255, 0.12)",
      },
    },
  },
  plugins: [],
};
