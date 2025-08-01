/**
 * Playwright Configuration for E2E Tests
 * הגדרות Playwright לבדיקות E2E
 */

import { defineConfig, devices } from '@playwright/test';
import path from 'path';

// Environment configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:5000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5174';
const CI = !!process.env.CI;

export default defineConfig({
  // Test directory
  testDir: '.',
  
  // Global test timeout
  timeout: 30000,
  
  // Expect timeout for assertions
  expect: {
    timeout: 10000,
  },
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: CI,
  
  // Retry on CI only
  retries: CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'test-results.xml' }],
    CI ? ['github'] : ['list']
  ],
  
  // Global setup and teardown
  globalSetup: path.resolve(__dirname, 'global-setup.ts'),
  globalTeardown: path.resolve(__dirname, 'global-teardown.ts'),
  
  // Shared settings for all projects
  use: {
    // Base URL for page.goto() calls
    baseURL: FRONTEND_URL,
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Record video on failure
    video: 'retain-on-failure',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Browser context options
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,
    
    // Action timeout
    actionTimeout: 10000,
    
    // Navigation timeout
    navigationTimeout: 30000,
  },
  
  // Test projects for different browsers and scenarios
  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Mobile browsers
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // Tablet
    {
      name: 'tablet',
      use: { ...devices['iPad Pro'] },
    },
    
    // Electron app (when available)
    {
      name: 'electron',
      use: {
        // Custom configuration for Electron
        viewport: null, // Electron manages its own window size
      },
      testMatch: /.*electron.*\.spec\.ts/,
    },
    
    // Accessibility tests
    {
      name: 'accessibility',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /.*accessibility.*\.spec\.ts/,
    },
    
    // Performance tests
    {
      name: 'performance',
      use: { 
        ...devices['Desktop Chrome'],
        // Enable performance metrics
        launchOptions: {
          args: ['--enable-precise-memory-info']
        }
      },
      testMatch: /.*performance.*\.spec\.ts/,
    },
  ],
  
  // Web server configuration
  webServer: [
    // Backend server
    {
      command: 'cd ../../ && python backend/main.py --host 127.0.0.1 --port 5000',
      port: 5000,
      timeout: 120000,
      reuseExistingServer: !CI,
      env: {
        NODE_ENV: 'test',
        PYTHONPATH: path.resolve(__dirname, '../../'),
      },
    },
    // Frontend server
    {
      command: 'cd ../../frontend/electron-app && npm run dev:vite',
      port: 5174,
      timeout: 120000,
      reuseExistingServer: !CI,
      env: {
        NODE_ENV: 'test',
      },
    },
  ],
  
  // Output directory for test artifacts
  outputDir: 'test-results/',
  
  // Test metadata
  metadata: {
    'test-environment': 'e2e',
    'backend-url': BACKEND_URL,
    'frontend-url': FRONTEND_URL,
    'ci': CI,
  },
});