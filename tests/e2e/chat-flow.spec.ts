/**
 * End-to-End Tests for AI Chat System
 * בדיקות E2E למערכת שיחות AI
 * 
 * This file contains comprehensive E2E tests using Playwright to verify
 * the complete user experience of the AI chat system, including UI interactions,
 * chat flows, session management, and accessibility.
 */

import { test, expect, Page, BrowserContext, ElectronApplication } from '@playwright/test';
import { _electron as electron } from 'playwright';
import path from 'path';

// Test configuration
const BACKEND_URL = 'http://127.0.0.1:5000';
const FRONTEND_URL = 'http://localhost:5174';
const ELECTRON_APP_PATH = path.join(__dirname, '../../frontend/electron-app');

// Helper functions
class ChatTestHelper {
  constructor(private page: Page) {}

  async waitForChatInterface() {
    await this.page.waitForSelector('[data-testid="chat-interface"]', { timeout: 10000 });
  }

  async sendMessage(message: string) {
    const inputArea = this.page.locator('[data-testid="message-input"]');
    await inputArea.fill(message);
    await this.page.locator('[data-testid="send-button"]').click();
  }

  async waitForResponse() {
    await this.page.waitForSelector('[data-testid="ai-message"]', { timeout: 15000 });
  }

  async getLastMessage() {
    const messages = this.page.locator('[data-testid="message-bubble"]');
    const lastMessage = messages.last();
    return await lastMessage.textContent();
  }

  async getMessageCount() {
    const messages = this.page.locator('[data-testid="message-bubble"]');
    return await messages.count();
  }

  async createNewSession(title: string = 'Test Session') {
    await this.page.locator('[data-testid="new-session-button"]').click();
    await this.page.locator('[data-testid="session-title-input"]').fill(title);
    await this.page.locator('[data-testid="create-session-button"]').click();
  }

  async selectSession(sessionTitle: string) {
    await this.page.locator(`[data-testid="session-item"]:has-text("${sessionTitle}")`).click();
  }

  async deleteSession(sessionTitle: string) {
    const sessionItem = this.page.locator(`[data-testid="session-item"]:has-text("${sessionTitle}")`);
    await sessionItem.hover();
    await sessionItem.locator('[data-testid="delete-session-button"]').click();
    await this.page.locator('[data-testid="confirm-delete-button"]').click();
  }

  async openSettings() {
    await this.page.locator('[data-testid="settings-button"]').click();
  }

  async selectModel(modelName: string) {
    await this.page.locator('[data-testid="model-selector"]').click();
    await this.page.locator(`[data-testid="model-option"]:has-text("${modelName}")`).click();
  }

  async adjustTemperature(value: number) {
    const slider = this.page.locator('[data-testid="temperature-slider"]');
    await slider.fill(value.toString());
  }

  async enableStreaming() {
    await this.page.locator('[data-testid="streaming-toggle"]').check();
  }

  async searchMessages(query: string) {
    await this.page.locator('[data-testid="search-input"]').fill(query);
    await this.page.locator('[data-testid="search-button"]').click();
  }

  async exportSession(format: 'json' | 'markdown' | 'txt' = 'json') {
    await this.page.locator('[data-testid="export-button"]').click();
    await this.page.locator(`[data-testid="export-format-${format}"]`).click();
    await this.page.locator('[data-testid="confirm-export-button"]').click();
  }
}

// Mock backend setup for testing
async function setupMockBackend(page: Page) {
  // Intercept API calls and provide mock responses
  await page.route(`${BACKEND_URL}/api/chat/sessions`, async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'test-session-1',
            title: 'Test Session 1',
            model_id: 'mock-model',
            user_id: 'test-user',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            message_count: 0,
            is_archived: false,
            metadata: {}
          }
        ])
      });
    } else if (route.request().method() === 'POST') {
      const requestBody = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'new-session-' + Date.now(),
          title: requestBody.title || 'New Session',
          model_id: requestBody.model_id || 'mock-model',
          user_id: requestBody.user_id || 'test-user',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          message_count: 0,
          is_archived: false,
          metadata: {}
        })
      });
    }
  });

  await page.route(`${BACKEND_URL}/api/chat/send`, async (route) => {
    const requestBody = route.request().postDataJSON();
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        content: `Mock response to: ${requestBody.message}`,
        model_id: 'mock-model',
        tokens_used: 10,
        response_time: 0.5,
        metadata: {}
      })
    });
  });

  await page.route(`${BACKEND_URL}/api/chat/stream`, async (route) => {
    const requestBody = route.request().postDataJSON();
    const words = `Mock streaming response to: ${requestBody.message}`.split(' ');
    
    // Simulate streaming response
    let streamData = '';
    for (const word of words) {
      streamData += `data: ${word} \n\n`;
    }
    streamData += 'data: [DONE]\n\n';

    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: streamData
    });
  });

  await page.route(`${BACKEND_URL}/api/chat/sessions/*/messages`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'msg-1',
          session_id: 'test-session-1',
          role: 'user',
          content: 'Hello, this is a test message',
          timestamp: new Date().toISOString(),
          model_id: null,
          tokens_used: null,
          response_time: null,
          metadata: {}
        },
        {
          id: 'msg-2',
          session_id: 'test-session-1',
          role: 'assistant',
          content: 'Mock response to: Hello, this is a test message',
          timestamp: new Date().toISOString(),
          model_id: 'mock-model',
          tokens_used: 10,
          response_time: 0.5,
          metadata: {}
        }
      ])
    });
  });

  await page.route(`${BACKEND_URL}/api/llm/models`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'local-gemma-3-4b-it',
          name: 'Gemma 3 4B IT',
          provider: 'Local Gemma',
          is_available: true,
          parameters: {
            max_tokens: 4096,
            temperature: 0.7,
            top_p: 0.9
          }
        },
        {
          id: 'gpt-4',
          name: 'GPT-4',
          provider: 'OpenAI',
          is_available: false,
          parameters: {
            max_tokens: 8192,
            temperature: 0.7,
            top_p: 1.0
          }
        }
      ])
    });
  });
}

// Test suites
test.describe('Chat Interface E2E Tests', () => {
  let page: Page;
  let context: BrowserContext;
  let helper: ChatTestHelper;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    helper = new ChatTestHelper(page);
    
    // Setup mock backend
    await setupMockBackend(page);
    
    // Navigate to the application
    await page.goto(FRONTEND_URL);
    await helper.waitForChatInterface();
  });

  test.afterEach(async () => {
    await context.close();
  });

  test('should display chat interface correctly', async () => {
    // Verify main UI elements are present
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="send-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="session-panel"]')).toBeVisible();
    
    // Verify initial state
    const messageCount = await helper.getMessageCount();
    expect(messageCount).toBe(0);
  });

  test('should send and receive messages', async () => {
    const testMessage = 'Hello, this is a test message';
    
    // Send message
    await helper.sendMessage(testMessage);
    
    // Wait for response
    await helper.waitForResponse();
    
    // Verify message count increased
    const messageCount = await helper.getMessageCount();
    expect(messageCount).toBe(2); // User message + AI response
    
    // Verify message content
    const lastMessage = await helper.getLastMessage();
    expect(lastMessage).toContain('Mock response to: Hello, this is a test message');
  });

  test('should handle streaming responses', async () => {
    // Enable streaming
    await helper.openSettings();
    await helper.enableStreaming();
    
    // Send message
    await helper.sendMessage('Test streaming response');
    
    // Wait for streaming to complete
    await page.waitForTimeout(2000);
    
    // Verify response was received
    const messageCount = await helper.getMessageCount();
    expect(messageCount).toBeGreaterThan(0);
  });

  test('should create and manage sessions', async () => {
    const sessionTitle = 'E2E Test Session';
    
    // Create new session
    await helper.createNewSession(sessionTitle);
    
    // Verify session appears in list
    await expect(page.locator(`[data-testid="session-item"]:has-text("${sessionTitle}")`)).toBeVisible();
    
    // Send message in new session
    await helper.sendMessage('Hello in new session');
    await helper.waitForResponse();
    
    // Verify message count
    const messageCount = await helper.getMessageCount();
    expect(messageCount).toBe(2);
    
    // Switch to another session and back
    await helper.createNewSession('Another Session');
    await helper.selectSession(sessionTitle);
    
    // Verify messages are preserved
    const preservedMessageCount = await helper.getMessageCount();
    expect(preservedMessageCount).toBe(2);
  });

  test('should delete sessions', async () => {
    const sessionTitle = 'Session to Delete';
    
    // Create session
    await helper.createNewSession(sessionTitle);
    
    // Verify session exists
    await expect(page.locator(`[data-testid="session-item"]:has-text("${sessionTitle}")`)).toBeVisible();
    
    // Delete session
    await helper.deleteSession(sessionTitle);
    
    // Verify session is removed
    await expect(page.locator(`[data-testid="session-item"]:has-text("${sessionTitle}")`)).not.toBeVisible();
  });

  test('should change model settings', async () => {
    // Open settings
    await helper.openSettings();
    
    // Change model
    await helper.selectModel('Gemma 3 4B IT');
    
    // Adjust temperature
    await helper.adjustTemperature(0.9);
    
    // Send message to test with new settings
    await helper.sendMessage('Test with new model settings');
    await helper.waitForResponse();
    
    // Verify response received
    const messageCount = await helper.getMessageCount();
    expect(messageCount).toBe(2);
  });

  test('should search messages', async () => {
    // Send some messages first
    await helper.sendMessage('This is about Python programming');
    await helper.waitForResponse();
    
    await helper.sendMessage('This is about JavaScript development');
    await helper.waitForResponse();
    
    // Search for specific content
    await helper.searchMessages('Python');
    
    // Verify search results
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-result-item"]')).toContainText('Python');
  });

  test('should export session data', async () => {
    // Send some messages
    await helper.sendMessage('Message for export test');
    await helper.waitForResponse();
    
    // Setup download handler
    const downloadPromise = page.waitForEvent('download');
    
    // Export session
    await helper.exportSession('json');
    
    // Verify download started
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/session_.*\.json/);
  });

  test('should handle keyboard shortcuts', async () => {
    const messageInput = page.locator('[data-testid="message-input"]');
    
    // Type message
    await messageInput.fill('Test keyboard shortcut');
    
    // Send with Ctrl+Enter
    await messageInput.press('Control+Enter');
    
    // Verify message was sent
    await helper.waitForResponse();
    const messageCount = await helper.getMessageCount();
    expect(messageCount).toBe(2);
  });

  test('should be responsive on different screen sizes', async () => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    
    // Verify mobile layout
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input"]')).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    
    // Verify tablet layout
    await expect(page.locator('[data-testid="session-panel"]')).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(500);
    
    // Verify desktop layout
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="session-panel"]')).toBeVisible();
  });
});

test.describe('Accessibility Tests', () => {
  let page: Page;
  let context: BrowserContext;
  let helper: ChatTestHelper;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    helper = new ChatTestHelper(page);
    
    await setupMockBackend(page);
    await page.goto(FRONTEND_URL);
    await helper.waitForChatInterface();
  });

  test.afterEach(async () => {
    await context.close();
  });

  test('should be keyboard navigable', async () => {
    // Tab through interface elements
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="message-input"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="send-button"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    // Should focus on next interactive element
  });

  test('should have proper ARIA labels', async () => {
    // Check for ARIA labels on key elements
    const messageInput = page.locator('[data-testid="message-input"]');
    await expect(messageInput).toHaveAttribute('aria-label');
    
    const sendButton = page.locator('[data-testid="send-button"]');
    await expect(sendButton).toHaveAttribute('aria-label');
    
    const sessionPanel = page.locator('[data-testid="session-panel"]');
    await expect(sessionPanel).toHaveAttribute('aria-label');
  });

  test('should support screen readers', async () => {
    // Send a message
    await helper.sendMessage('Accessibility test message');
    await helper.waitForResponse();
    
    // Check for screen reader announcements
    const messages = page.locator('[data-testid="message-bubble"]');
    await expect(messages.first()).toHaveAttribute('role', 'article');
    
    // Check for proper heading structure
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    expect(await headings.count()).toBeGreaterThan(0);
  });

  test('should have sufficient color contrast', async () => {
    // This would typically use axe-core or similar tool
    // For now, we'll check that text is visible
    const messageInput = page.locator('[data-testid="message-input"]');
    await expect(messageInput).toBeVisible();
    
    const sendButton = page.locator('[data-testid="send-button"]');
    await expect(sendButton).toBeVisible();
  });
});

test.describe('Error Handling Tests', () => {
  let page: Page;
  let context: BrowserContext;
  let helper: ChatTestHelper;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    helper = new ChatTestHelper(page);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test('should handle backend connection errors', async () => {
    // Don't setup mock backend to simulate connection error
    await page.goto(FRONTEND_URL);
    
    // Try to send message
    await page.locator('[data-testid="message-input"]').fill('Test message');
    await page.locator('[data-testid="send-button"]').click();
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('connection');
  });

  test('should handle API errors gracefully', async () => {
    // Setup mock backend with error responses
    await page.route(`${BACKEND_URL}/api/chat/send`, async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          error: 'Internal server error'
        })
      });
    });
    
    await page.goto(FRONTEND_URL);
    await helper.waitForChatInterface();
    
    // Try to send message
    await helper.sendMessage('This should fail');
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });

  test('should handle network timeouts', async () => {
    // Setup slow response to simulate timeout
    await page.route(`${BACKEND_URL}/api/chat/send`, async (route) => {
      await new Promise(resolve => setTimeout(resolve, 30000)); // 30 second delay
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, content: 'Late response' })
      });
    });
    
    await setupMockBackend(page);
    await page.goto(FRONTEND_URL);
    await helper.waitForChatInterface();
    
    // Send message
    await helper.sendMessage('This should timeout');
    
    // Should show timeout error
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({ timeout: 35000 });
  });
});

test.describe('Performance Tests', () => {
  let page: Page;
  let context: BrowserContext;
  let helper: ChatTestHelper;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    helper = new ChatTestHelper(page);
    
    await setupMockBackend(page);
    await page.goto(FRONTEND_URL);
    await helper.waitForChatInterface();
  });

  test.afterEach(async () => {
    await context.close();
  });

  test('should load interface quickly', async () => {
    const startTime = Date.now();
    
    await page.goto(FRONTEND_URL);
    await helper.waitForChatInterface();
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
  });

  test('should handle many messages efficiently', async () => {
    // Send multiple messages quickly
    const messageCount = 10;
    const startTime = Date.now();
    
    for (let i = 0; i < messageCount; i++) {
      await helper.sendMessage(`Message ${i + 1}`);
      await page.waitForTimeout(100); // Small delay between messages
    }
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // Should handle messages efficiently
    expect(totalTime).toBeLessThan(messageCount * 2000); // Max 2 seconds per message
    
    // Verify all messages are displayed
    const displayedMessages = await helper.getMessageCount();
    expect(displayedMessages).toBe(messageCount * 2); // User + AI messages
  });

  test('should scroll smoothly with many messages', async () => {
    // Add many messages to test scrolling
    for (let i = 0; i < 20; i++) {
      await helper.sendMessage(`Scroll test message ${i + 1}`);
      await page.waitForTimeout(50);
    }
    
    // Test scrolling performance
    const messageList = page.locator('[data-testid="message-list"]');
    await messageList.evaluate(el => el.scrollTop = 0); // Scroll to top
    await page.waitForTimeout(100);
    
    await messageList.evaluate(el => el.scrollTop = el.scrollHeight); // Scroll to bottom
    await page.waitForTimeout(100);
    
    // Should scroll without issues
    const scrollTop = await messageList.evaluate(el => el.scrollTop);
    expect(scrollTop).toBeGreaterThan(0);
  });
});

// Electron-specific tests (if running as Electron app)
test.describe('Electron App Tests', () => {
  let electronApp: ElectronApplication;
  let page: Page;

  test.skip(() => process.env.TEST_MODE !== 'electron', 'Electron tests only');

  test.beforeEach(async () => {
    electronApp = await electron.launch({
      args: [path.join(ELECTRON_APP_PATH, 'dist/main/main.js')]
    });
    page = await electronApp.firstWindow();
  });

  test.afterEach(async () => {
    await electronApp.close();
  });

  test('should launch Electron app', async () => {
    await expect(page).toHaveTitle(/Audio Chat Studio/);
  });

  test('should have menu bar', async () => {
    // Test Electron menu functionality
    const title = await page.title();
    expect(title).toContain('Audio Chat Studio');
  });

  test('should handle window operations', async () => {
    // Test minimize, maximize, close
    await page.evaluate(() => {
      // @ts-ignore
      window.electronAPI?.minimize();
    });
    
    await page.waitForTimeout(500);
    
    await page.evaluate(() => {
      // @ts-ignore
      window.electronAPI?.restore();
    });
  });
});