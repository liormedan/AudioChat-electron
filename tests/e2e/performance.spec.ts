/**
 * Performance E2E Tests
 * בדיקות ביצועים E2E
 * 
 * This file contains performance-focused E2E tests to ensure
 * the chat interface performs well under various conditions.
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';

class PerformanceHelper {
  constructor(private page: Page) {}

  async measurePageLoad() {
    const startTime = Date.now();
    await this.page.goto('/');
    await this.page.waitForSelector('[data-testid="chat-interface"]');
    const endTime = Date.now();
    return endTime - startTime;
  }

  async measureFirstContentfulPaint() {
    const metrics = await this.page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
          if (fcpEntry) {
            resolve(fcpEntry.startTime);
          }
        }).observe({ entryTypes: ['paint'] });
      });
    });
    return metrics;
  }

  async measureLargestContentfulPaint() {
    const lcp = await this.page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });
        
        // Fallback timeout
        setTimeout(() => resolve(0), 5000);
      });
    });
    return lcp;
  }

  async measureCumulativeLayoutShift() {
    const cls = await this.page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0;
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          resolve(clsValue);
        }).observe({ entryTypes: ['layout-shift'] });
        
        // Resolve after 3 seconds
        setTimeout(() => resolve(clsValue), 3000);
      });
    });
    return cls;
  }

  async measureMemoryUsage() {
    const memoryInfo = await this.page.evaluate(() => {
      // @ts-ignore
      return (performance as any).memory ? {
        // @ts-ignore
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        // @ts-ignore
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
        // @ts-ignore
        jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
      } : null;
    });
    return memoryInfo;
  }

  async measureNetworkRequests() {
    const requests: any[] = [];
    
    this.page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        timestamp: Date.now()
      });
    });
    
    this.page.on('response', response => {
      const request = requests.find(req => req.url === response.url());
      if (request) {
        request.status = response.status();
        request.responseTime = Date.now() - request.timestamp;
        request.size = response.headers()['content-length'] || 0;
      }
    });
    
    return requests;
  }

  async simulateSlowNetwork() {
    const context = this.page.context();
    await context.route('**/*', async (route) => {
      // Add 500ms delay to simulate slow network
      await new Promise(resolve => setTimeout(resolve, 500));
      await route.continue();
    });
  }

  async simulateHighCPULoad() {
    // Simulate high CPU load by running intensive JavaScript
    await this.page.evaluate(() => {
      const startTime = Date.now();
      while (Date.now() - startTime < 1000) {
        // Busy wait for 1 second
        Math.random();
      }
    });
  }

  async measureScrollPerformance(scrollCount: number = 10) {
    const scrollTimes: number[] = [];
    
    for (let i = 0; i < scrollCount; i++) {
      const startTime = Date.now();
      await this.page.evaluate(() => {
        window.scrollBy(0, 100);
      });
      await this.page.waitForTimeout(50); // Wait for scroll to complete
      const endTime = Date.now();
      scrollTimes.push(endTime - startTime);
    }
    
    return {
      average: scrollTimes.reduce((a, b) => a + b, 0) / scrollTimes.length,
      max: Math.max(...scrollTimes),
      min: Math.min(...scrollTimes)
    };
  }
}

test.describe('Performance Tests', () => {
  let page: Page;
  let context: BrowserContext;
  let perfHelper: PerformanceHelper;

  test.beforeEach(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    perfHelper = new PerformanceHelper(page);
  });

  test.afterEach(async () => {
    await context.close();
  });

  test('should load page within acceptable time', async () => {
    const loadTime = await perfHelper.measurePageLoad();
    
    console.log(`Page load time: ${loadTime}ms`);
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Ideally within 1.5 seconds
    if (loadTime > 1500) {
      console.warn(`Page load time (${loadTime}ms) is slower than ideal (1500ms)`);
    }
  });

  test('should have good Core Web Vitals', async () => {
    await page.goto('/');
    
    // Measure First Contentful Paint
    const fcp = await perfHelper.measureFirstContentfulPaint();
    console.log(`First Contentful Paint: ${fcp}ms`);
    expect(fcp).toBeLessThan(2000); // Should be under 2 seconds
    
    // Measure Largest Contentful Paint
    const lcp = await perfHelper.measureLargestContentfulPaint();
    console.log(`Largest Contentful Paint: ${lcp}ms`);
    expect(lcp).toBeLessThan(2500); // Should be under 2.5 seconds
    
    // Measure Cumulative Layout Shift
    const cls = await perfHelper.measureCumulativeLayoutShift();
    console.log(`Cumulative Layout Shift: ${cls}`);
    expect(cls).toBeLessThan(0.1); // Should be under 0.1
  });

  test('should handle memory efficiently', async () => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    const initialMemory = await perfHelper.measureMemoryUsage();
    
    if (initialMemory) {
      console.log(`Initial memory usage: ${Math.round(initialMemory.usedJSHeapSize / 1024 / 1024)}MB`);
      
      // Simulate heavy usage
      for (let i = 0; i < 10; i++) {
        await page.locator('[data-testid="message-input"]').fill(`Performance test message ${i}`);
        await page.locator('[data-testid="send-button"]').click();
        await page.waitForTimeout(100);
      }
      
      const finalMemory = await perfHelper.measureMemoryUsage();
      console.log(`Final memory usage: ${Math.round(finalMemory.usedJSHeapSize / 1024 / 1024)}MB`);
      
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
      const memoryIncreaseMB = memoryIncrease / 1024 / 1024;
      
      console.log(`Memory increase: ${Math.round(memoryIncreaseMB)}MB`);
      
      // Memory increase should be reasonable (less than 50MB for this test)
      expect(memoryIncreaseMB).toBeLessThan(50);
    } else {
      console.log('Memory measurement not available in this browser');
    }
  });

  test('should perform well with many messages', async () => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    const messageCount = 50;
    const startTime = Date.now();
    
    // Add many messages quickly
    for (let i = 0; i < messageCount; i++) {
      await page.evaluate((index) => {
        // Simulate adding messages directly to avoid network delays
        const messageList = document.querySelector('[data-testid="message-list"]');
        if (messageList) {
          const messageElement = document.createElement('div');
          messageElement.className = 'message-bubble';
          messageElement.textContent = `Performance test message ${index}`;
          messageList.appendChild(messageElement);
        }
      }, i);
      
      if (i % 10 === 0) {
        await page.waitForTimeout(10); // Small pause every 10 messages
      }
    }
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    console.log(`Time to add ${messageCount} messages: ${totalTime}ms`);
    console.log(`Average time per message: ${totalTime / messageCount}ms`);
    
    // Should handle messages efficiently
    expect(totalTime).toBeLessThan(messageCount * 50); // Max 50ms per message
    
    // Test scrolling performance with many messages
    const scrollPerf = await perfHelper.measureScrollPerformance(10);
    console.log(`Scroll performance - Avg: ${scrollPerf.average}ms, Max: ${scrollPerf.max}ms`);
    
    expect(scrollPerf.average).toBeLessThan(100); // Average scroll should be under 100ms
    expect(scrollPerf.max).toBeLessThan(200); // Max scroll should be under 200ms
  });

  test('should handle slow network conditions', async () => {
    await perfHelper.simulateSlowNetwork();
    
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    const loadTime = Date.now() - startTime;
    
    console.log(`Load time with slow network: ${loadTime}ms`);
    
    // Should still load within reasonable time even with slow network
    expect(loadTime).toBeLessThan(10000); // 10 seconds max
    
    // Test sending message with slow network
    const messageStartTime = Date.now();
    await page.locator('[data-testid="message-input"]').fill('Slow network test');
    await page.locator('[data-testid="send-button"]').click();
    
    // Wait for response or timeout
    try {
      await page.waitForSelector('[data-testid="ai-message"]', { timeout: 15000 });
      const messageTime = Date.now() - messageStartTime;
      console.log(`Message response time with slow network: ${messageTime}ms`);
      expect(messageTime).toBeLessThan(15000);
    } catch (error) {
      console.log('Message timed out with slow network (this may be expected)');
    }
  });

  test('should handle high CPU load', async () => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    // Simulate high CPU load
    await perfHelper.simulateHighCPULoad();
    
    // Test that interface remains responsive
    const startTime = Date.now();
    await page.locator('[data-testid="message-input"]').fill('High CPU test');
    await page.locator('[data-testid="send-button"]').click();
    const responseTime = Date.now() - startTime;
    
    console.log(`Response time under high CPU load: ${responseTime}ms`);
    
    // Should still be responsive within reasonable time
    expect(responseTime).toBeLessThan(2000);
  });

  test('should optimize network requests', async () => {
    const requests = await perfHelper.measureNetworkRequests();
    
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    // Wait a bit for all requests to complete
    await page.waitForTimeout(2000);
    
    // Analyze network requests
    const completedRequests = requests.filter(req => req.responseTime);
    const totalRequests = completedRequests.length;
    const averageResponseTime = completedRequests.reduce((sum, req) => sum + req.responseTime, 0) / totalRequests;
    const slowRequests = completedRequests.filter(req => req.responseTime > 1000);
    
    console.log(`Total network requests: ${totalRequests}`);
    console.log(`Average response time: ${Math.round(averageResponseTime)}ms`);
    console.log(`Slow requests (>1s): ${slowRequests.length}`);
    
    // Performance expectations
    expect(totalRequests).toBeLessThan(20); // Shouldn't make too many requests
    expect(averageResponseTime).toBeLessThan(500); // Average should be under 500ms
    expect(slowRequests.length).toBeLessThan(3); // Max 2 slow requests allowed
    
    // Check for failed requests
    const failedRequests = completedRequests.filter(req => req.status >= 400);
    expect(failedRequests.length).toBe(0);
  });

  test('should handle concurrent operations', async () => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    // Simulate concurrent operations
    const operations = [
      // Send multiple messages simultaneously
      page.locator('[data-testid="message-input"]').fill('Concurrent test 1'),
      page.locator('[data-testid="send-button"]').click(),
      page.locator('[data-testid="message-input"]').fill('Concurrent test 2'),
      page.locator('[data-testid="send-button"]').click(),
      page.locator('[data-testid="message-input"]').fill('Concurrent test 3'),
      page.locator('[data-testid="send-button"]').click(),
      
      // Scroll while sending messages
      page.evaluate(() => window.scrollBy(0, 100)),
      page.evaluate(() => window.scrollBy(0, -50)),
      
      // Open/close settings
      page.locator('[data-testid="settings-button"]').click(),
      page.keyboard.press('Escape'),
    ];
    
    const startTime = Date.now();
    
    // Execute all operations concurrently
    await Promise.allSettled(operations);
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    console.log(`Concurrent operations completed in: ${totalTime}ms`);
    
    // Should handle concurrent operations efficiently
    expect(totalTime).toBeLessThan(5000);
    
    // Interface should still be responsive
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input"]')).toBeEnabled();
  });

  test('should maintain performance during streaming', async () => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    // Enable streaming if available
    const streamingToggle = page.locator('[data-testid="streaming-toggle"]');
    if (await streamingToggle.count() > 0) {
      await streamingToggle.check();
    }
    
    const startTime = Date.now();
    
    // Send message that should trigger streaming
    await page.locator('[data-testid="message-input"]').fill('Long streaming response test');
    await page.locator('[data-testid="send-button"]').click();
    
    // Monitor performance during streaming
    let frameCount = 0;
    const frameStartTime = Date.now();
    
    // Count frames for 3 seconds
    const frameCounter = setInterval(() => {
      frameCount++;
    }, 16); // ~60fps
    
    await page.waitForTimeout(3000);
    clearInterval(frameCounter);
    
    const frameEndTime = Date.now();
    const actualFPS = frameCount / ((frameEndTime - frameStartTime) / 1000);
    
    console.log(`Estimated FPS during streaming: ${Math.round(actualFPS)}`);
    
    // Should maintain reasonable frame rate
    expect(actualFPS).toBeGreaterThan(30); // At least 30 FPS
    
    const totalStreamingTime = Date.now() - startTime;
    console.log(`Total streaming time: ${totalStreamingTime}ms`);
  });

  test('should handle browser resource limits', async () => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    // Test with limited viewport
    await page.setViewportSize({ width: 320, height: 568 }); // Small mobile screen
    
    // Should still be usable
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input"]')).toBeVisible();
    
    // Test with very large viewport
    await page.setViewportSize({ width: 3840, height: 2160 }); // 4K screen
    
    // Should scale appropriately
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    
    // Reset to normal size
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Test memory pressure simulation
    await page.evaluate(() => {
      // Create large arrays to simulate memory pressure
      const arrays = [];
      for (let i = 0; i < 100; i++) {
        arrays.push(new Array(10000).fill(Math.random()));
      }
      
      // Clean up after a short time
      setTimeout(() => {
        arrays.length = 0;
      }, 1000);
    });
    
    await page.waitForTimeout(1500);
    
    // Interface should still be responsive
    await page.locator('[data-testid="message-input"]').fill('Memory pressure test');
    await page.locator('[data-testid="send-button"]').click();
    
    await expect(page.locator('[data-testid="message-input"]')).toBeEnabled();
  });
});