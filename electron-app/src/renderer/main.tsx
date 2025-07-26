import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { AppProviders } from './providers/app-providers'; // Import AppProviders

// Ensure we have a root element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

// Create React root and render app
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <AppProviders> {/* Wrap App with AppProviders */}
      <App />
    </AppProviders>
  </React.StrictMode>
);