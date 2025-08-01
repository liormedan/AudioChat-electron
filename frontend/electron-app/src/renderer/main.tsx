import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { AppProviders } from './providers/app-providers';
import { useLanguage } from './contexts/language-provider';

const LanguageUpdater: React.FC = () => {
  const { language, direction } = useLanguage();

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = direction;
  }, [language, direction]);

  return null;
};

// Ensure we have a root element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

// Create React root and render app
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <AppProviders>
      <LanguageUpdater />
      <App />
    </AppProviders>
  </React.StrictMode>
);
