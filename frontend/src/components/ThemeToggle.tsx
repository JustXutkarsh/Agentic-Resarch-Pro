import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { toggleTheme, isDark } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-research-paper border border-research-borderLight hover:border-research-border hover:bg-research-surface text-research-secondary hover:text-research-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-research-blue shrink-0 min-h-[36px] min-w-[36px] sm:min-h-[32px] sm:min-w-[32px] touch-manipulation after:absolute after:-inset-1 after:content-[''] cursor-pointer"
      aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      title={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-research-warning transition-transform duration-200 rotate-0 hover:rotate-45" />
      ) : (
        <Moon className="w-4 h-4 text-research-secondary transition-transform duration-200 -rotate-12 hover:rotate-0" />
      )}
    </button>
  );
};
