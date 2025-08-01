import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '../lib/query-client';
import { ThemeProvider } from '../contexts/theme-provider';
replace-hard-coded-strings-in-sidebar.tsx
import { LocaleProvider } from '../contexts/locale-provider';
add-language-direction-support-to-mainlayout


interface AppProvidersProps {
  children: React.ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
       replace-hard-coded-strings-in-sidebar.tsx
      <LocaleProvider>
        <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
          {children}
          {/* React Query DevTools - only shows in development */}
          <ReactQueryDevtools initialIsOpen={false} />
        </ThemeProvider>
      </LocaleProvider>
\    </QueryClientProvider>
  );
};