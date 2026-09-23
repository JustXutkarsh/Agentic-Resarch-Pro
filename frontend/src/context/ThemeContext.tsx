import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

export type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
}

const STORAGE_KEY = 'agentic-research-pro-theme';

const getInitialTheme = (): Theme => {
  // 1. First check documentElement (already set synchronously by index.html inline script)
  if (typeof document !== 'undefined') {
    const docTheme = document.documentElement.getAttribute('data-theme');
    if (docTheme === 'dark' || docTheme === 'light') {
      return docTheme;
    }
  }

  // 2. Check localStorage
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') {
      return stored;
    }
  } catch {
    // localStorage restricted or throws
  }

  // 3. Fallback to system preference
  if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }

  return 'light';
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme);

  const applyThemeToDOM = useCallback((newTheme: Theme, enableTransition = false) => {
    if (typeof document === 'undefined') return;

    if (enableTransition) {
      document.documentElement.classList.add('theme-transition');
    }

    document.documentElement.setAttribute('data-theme', newTheme);
    document.documentElement.style.colorScheme = newTheme;

    if (enableTransition) {
      window.setTimeout(() => {
        document.documentElement.classList.remove('theme-transition');
      }, 250);
    }
  }, []);

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    try {
      localStorage.setItem(STORAGE_KEY, newTheme);
    } catch {
      // localStorage may fail/throw in private browsing/sandboxed iframes
    }
    applyThemeToDOM(newTheme, true);
  }, [applyThemeToDOM]);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => {
      const nextTheme = prev === 'light' ? 'dark' : 'light';
      try {
        localStorage.setItem(STORAGE_KEY, nextTheme);
      } catch {
        // localStorage may fail/throw
      }
      applyThemeToDOM(nextTheme, true);
      return nextTheme;
    });
  }, [applyThemeToDOM]);

  // Listen for OS system theme changes ONLY IF no valid user preference is stored
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        // Only react to OS changes if user has NOT explicitly chosen a preference
        if (stored !== 'light' && stored !== 'dark') {
          const systemTheme: Theme = e.matches ? 'dark' : 'light';
          setThemeState(systemTheme);
          applyThemeToDOM(systemTheme, false);
        }
      } catch {
        // If localStorage throws, follow system preference
        const systemTheme: Theme = e.matches ? 'dark' : 'light';
        setThemeState(systemTheme);
        applyThemeToDOM(systemTheme, false);
      }
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else if ((mediaQuery as any).addListener) {
      (mediaQuery as any).addListener(handleChange);
      return () => (mediaQuery as any).removeListener(handleChange);
    }
  }, [applyThemeToDOM]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, isDark: theme === 'dark' }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
