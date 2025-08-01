/**
 * Global Setup for E2E Tests
 * הגדרה גלובלית לבדיקות E2E
 */

import { chromium, FullConfig } from '@playwright/test';
import path from 'path';
import fs from 'fs';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test setup...');
  
  // Create test directories
  const testDirs = [
    'test-results',
    'playwright-report',
    'screenshots',
    'videos',
    'traces'
  ];
  
  for (const dir of testDirs) {
    const dirPath = path.join(__dirname, dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  }
  
  // Wait for services to be ready
  await waitForServices();
  
  // Setup test data
  await setupTestData();
  
  console.log('✅ E2E test setup completed');
}

async function waitForServices() {
  const BACKEND_URL = 'http://127.0.0.1:5000';
  const FRONTEND_URL = 'http://localhost:5174';
  const MAX_RETRIES = 30;
  const RETRY_DELAY = 2000;
  
  console.log('⏳ Waiting for services to be ready...');
  
  // Wait for backend
  let backendReady = false;
  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      const response = await fetch(`${BACKEND_URL}/health`);
      if (response.ok) {
        backendReady = true;
        console.log('✅ Backend service is ready');
        break;
      }
    } catch (error) {
      // Service not ready yet
    }
    
    if (i < MAX_RETRIES - 1) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
    }
  }
  
  if (!backendReady) {
    throw new Error('Backend service failed to start within timeout');
  }
  
  // Wait for frontend
  let frontendReady = false;
  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      const response = await fetch(FRONTEND_URL);
      if (response.ok) {
        frontendReady = true;
        console.log('✅ Frontend service is ready');
        break;
      }
    } catch (error) {
      // Service not ready yet
    }
    
    if (i < MAX_RETRIES - 1) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
    }
  }
  
  if (!frontendReady) {
    throw new Error('Frontend service failed to start within timeout');
  }
}

async function setupTestData() {
  console.log('📝 Setting up test data...');
  
  // Create a browser instance for setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Setup test database state
    const BACKEND_URL = 'http://127.0.0.1:5000';
    
    // Clear any existing test data
    try {
      await fetch(`${BACKEND_URL}/api/test/cleanup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_mode: true })
      });
    } catch (error) {
      // Cleanup endpoint might not exist, that's okay
      console.log('⚠️ Test cleanup endpoint not available');
    }
    
    // Create test user and initial data
    try {
      await fetch(`${BACKEND_URL}/api/test/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_mode: true,
          create_test_user: true,
          user_id: 'e2e-test-user'
        })
      });
    } catch (error) {
      // Setup endpoint might not exist, that's okay
      console.log('⚠️ Test setup endpoint not available');
    }
    
    console.log('✅ Test data setup completed');
    
  } catch (error) {
    console.error('❌ Failed to setup test data:', error);
    // Don't fail the entire test suite if test data setup fails
  } finally {
    await browser.close();
  }
}

export default globalSetup;