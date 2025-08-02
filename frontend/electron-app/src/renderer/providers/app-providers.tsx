import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '../lib/query-client';
import { ThemeProvider } from '../contexts/theme-provider';
import { LanguageProvider } from '../contexts/language-context';
import { LocaleProvider } from '../contexts/locale-provider';

interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <LocaleProvider defaultLocale="he">
          <LanguageProvider>
            {children}
            {/* React Query DevTools - only shows in development */}
            <ReactQueryDevtools initialIsOpen={false} />
          </LanguageProvider>
        </LocaleProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};