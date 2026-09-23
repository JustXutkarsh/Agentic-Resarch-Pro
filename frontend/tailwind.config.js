function withOpacity(variableName) {
  return ({ opacityValue }) => {
    if (opacityValue !== undefined) {
      return `rgba(var(${variableName}), ${opacityValue})`;
    }
    return `rgb(var(${variableName}))`;
  };
}

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['selector', '[data-theme="dark"]'],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        research: {
          bg: withOpacity("--research-bg-rgb"),
          paper: withOpacity("--research-paper-rgb"),
          primary: withOpacity("--research-primary-rgb"),
          ink: withOpacity("--research-ink-rgb"),
          secondary: withOpacity("--research-secondary-rgb"),
          muted: withOpacity("--research-muted-rgb"),
          border: withOpacity("--research-border-rgb"),
          borderLight: withOpacity("--research-border-light-rgb"),
          blue: withOpacity("--research-blue-rgb"),
          deepBlue: withOpacity("--research-deep-blue-rgb"),
          green: withOpacity("--research-green-rgb"),
          greenLight: withOpacity("--research-green-light-rgb"),
          warning: withOpacity("--research-warning-rgb"),
          warningLight: withOpacity("--research-warning-light-rgb"),
          coral: withOpacity("--research-coral-rgb"),
          coralLight: withOpacity("--research-coral-light-rgb"),
          surface: withOpacity("--research-surface-rgb"),
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
        subtle: "var(--research-shadow-subtle)",
        card: "var(--research-shadow-card)",
        cardHover: "var(--research-shadow-card-hover)",
        composer: "var(--research-shadow-composer)",
        composerFocus: "var(--research-shadow-composer-focus)",
      },
    },
  },
  plugins: [],
};
