import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '../lib/query-client';
import { ThemeProvider } from '../contexts/theme-provider';
add-language-support-to-electron-app
import { LanguageProvider } from '../contexts/language-context';
replace-hard-coded-strings-in-sidebar.tsx


interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      add-language-support-to-electron-app
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <LanguageProvider>
          {children}
          {/* React Query DevTools - only shows in development */}
          <ReactQueryDevtools initialIsOpen={false} />
        </LanguageProvider>
      </ThemeProvider>
    </QueryClientProvider>

  );
};