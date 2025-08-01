import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '../lib/query-client';
import { ThemeProvider } from '../contexts/theme-provider';
codex/add-language-direction-support-to-mainlayout
import { LanguageProvider } from '../contexts/language-context';


interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
       codex/add-language-direction-support-to-mainlayout
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