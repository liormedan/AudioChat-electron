/**
 * Accessibility E2E Tests
 * בדיקות נגישות E2E
 * 
 * This file contains comprehensive accessibility tests to ensure
 * the chat interface is usable by people with disabilities.
 */

import { test, expect, Page } from '@playwright/test';
import { injectAxe, checkA11y, getViolations } from 'axe-playwright';

class AccessibilityHelper {
  constructor(private page: Page) {}

  async injectAxe() {
    await injectAxe(this.page);
  }

  async checkAccessibility(options?: any) {
    const violations = await getViolations(this.page, null, options);
    return violations;
  }

  async checkKeyboardNavigation() {
    // Test tab navigation
    const focusableElements = await this.page.locator('[tabindex]:not([tabindex="-1"]), button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href]').all();
    
    let currentIndex = 0;
    for (const element of focusableElements) {
      await this.page.keyboard.press('Tab');
      const focused = await this.page.locator(':focus').first();
      
      // Verify the correct element is focused
      const isSameElement = await element.evaluate((el, focusedEl) => {
        return el === focusedEl;
      }, await focused.elementHandle());
      
      if (!isSameElement) {
        console.warn(`Tab navigation issue at index ${currentIndex}`);
      }
      
      currentIndex++;
    }
  }

  async checkAriaLabels() {
    // Check for missing ARIA labels on interactive elements
    const interactiveElements = await this.page.locator('button, input, select, textarea, [role="button"], [role="textbox"]').all();
    
    const missingLabels = [];
    for (const element of interactiveElements) {
      const hasAriaLabel = await element.getAttribute('aria-label');
      const hasAriaLabelledBy = await element.getAttribute('aria-labelledby');
      const hasLabel = await element.locator('xpath=//label[@for="' + await element.getAttribute('id') + '"]').count() > 0;
      
      if (!hasAriaLabel && !hasAriaLabelledBy && !hasLabel) {
        const tagName = await element.evaluate(el => el.tagName);
        const id = await element.getAttribute('id');
        const className = await element.getAttribute('class');
        missingLabels.push({ tagName, id, className });
      }
    }
    
    return missingLabels;
  }

  async checkColorContrast() {
    // This would typically use a color contrast analyzer
    // For now, we'll check that text is visible
    const textElements = await this.page.locator('p, span, div, h1, h2, h3, h4, h5, h6, button, input, label').all();
    
    const lowContrastElements = [];
    for (const element of textElements) {
      const isVisible = await element.isVisible();
      if (!isVisible) {
        const text = await element.textContent();
        if (text && text.trim().length > 0) {
          lowContrastElements.push(text.substring(0, 50));
        }
      }
    }
    
    return lowContrastElements;
  }

  async checkScreenReaderContent() {
    // Check for proper heading structure
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').all();
    const headingLevels = [];
    
    for (const heading of headings) {
      const tagName = await heading.evaluate(el => el.tagName);
      const level = parseInt(tagName.charAt(1));
      headingLevels.push(level);
    }
    
    // Check for proper heading hierarchy
    let previousLevel = 0;
    const hierarchyIssues = [];
    
    for (let i = 0; i < headingLevels.length; i++) {
      const currentLevel = headingLevels[i];
      if (currentLevel > previousLevel + 1) {
        hierarchyIssues.push(`Heading level jump from h${previousLevel} to h${currentLevel} at position ${i}`);
      }
      previousLevel = currentLevel;
    }
    
    return { headingLevels, hierarchyIssues };
  }
}

test.describe('Accessibility Tests', () => {
  let page: Page;
  let a11yHelper: AccessibilityHelper;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    a11yHelper = new AccessibilityHelper(page);
    
    // Navigate to the application
    await page.goto('/');
    await page.waitForSelector('[data-testid="chat-interface"]', { timeout: 10000 });
    
    // Inject axe-core for accessibility testing
    await a11yHelper.injectAxe();
  });

  test('should pass axe-core accessibility audit', async () => {
    // Run full accessibility audit
    const violations = await a11yHelper.checkAccessibility();
    
    // Log violations for debugging
    if (violations.length > 0) {
      console.log('Accessibility violations found:');
      violations.forEach((violation, index) => {
        console.log(`${index + 1}. ${violation.id}: ${violation.description}`);
        console.log(`   Impact: ${violation.impact}`);
        console.log(`   Help: ${violation.help}`);
        console.log(`   Elements: ${violation.nodes.length}`);
      });
    }
    
    // Fail test if critical violations found
    const criticalViolations = violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    expect(criticalViolations).toHaveLength(0);
  });

  test('should have proper keyboard navigation', async () => {
    // Test tab navigation through interface
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
    
    // Test that all interactive elements are reachable
    const interactiveElements = await page.locator('button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])').count();
    
    let tabCount = 0;
    let lastFocused = null;
    
    for (let i = 0; i < interactiveElements + 5; i++) { // +5 for safety
      await page.keyboard.press('Tab');
      const currentFocused = await page.locator(':focus').first();
      
      if (await currentFocused.isVisible()) {
        const currentElement = await currentFocused.evaluate(el => el.outerHTML.substring(0, 100));
        if (currentElement !== lastFocused) {
          tabCount++;
          lastFocused = currentElement;
        }
      }
    }
    
    expect(tabCount).toBeGreaterThan(0);
  });

  test('should support keyboard shortcuts', async () => {
    // Test Enter key to send message
    const messageInput = page.locator('[data-testid="message-input"]');
    await messageInput.fill('Test keyboard shortcut');
    await messageInput.press('Enter');
    
    // Should send the message (or show some response)
    await page.waitForTimeout(1000);
    
    // Test Ctrl+Enter shortcut
    await messageInput.fill('Test Ctrl+Enter');
    await messageInput.press('Control+Enter');
    
    // Should also send the message
    await page.waitForTimeout(1000);
    
    // Test Escape key to clear input
    await messageInput.fill('Text to clear');
    await messageInput.press('Escape');
    
    const inputValue = await messageInput.inputValue();
    expect(inputValue).toBe('');
  });

  test('should have proper ARIA labels and roles', async () => {
    // Check for missing ARIA labels
    const missingLabels = await a11yHelper.checkAriaLabels();
    
    if (missingLabels.length > 0) {
      console.log('Elements missing ARIA labels:');
      missingLabels.forEach(element => {
        console.log(`  ${element.tagName} - ID: ${element.id}, Class: ${element.className}`);
      });
    }
    
    // Allow some missing labels but not too many
    expect(missingLabels.length).toBeLessThan(5);
    
    // Check specific important elements
    await expect(page.locator('[data-testid="message-input"]')).toHaveAttribute('aria-label');
    await expect(page.locator('[data-testid="send-button"]')).toHaveAttribute('aria-label');
    
    // Check for proper roles
    const messageList = page.locator('[data-testid="message-list"]');
    if (await messageList.count() > 0) {
      await expect(messageList).toHaveAttribute('role', 'log');
    }
  });

  test('should have proper heading structure', async () => {
    const { headingLevels, hierarchyIssues } = await a11yHelper.checkScreenReaderContent();
    
    // Should have at least one heading
    expect(headingLevels.length).toBeGreaterThan(0);
    
    // Should start with h1
    if (headingLevels.length > 0) {
      expect(headingLevels[0]).toBe(1);
    }
    
    // Log hierarchy issues
    if (hierarchyIssues.length > 0) {
      console.log('Heading hierarchy issues:');
      hierarchyIssues.forEach(issue => console.log(`  ${issue}`));
    }
    
    // Allow some hierarchy issues but not too many
    expect(hierarchyIssues.length).toBeLessThan(3);
  });

  test('should support screen readers', async () => {
    // Check for screen reader specific attributes
    const liveRegions = await page.locator('[aria-live]').count();
    expect(liveRegions).toBeGreaterThan(0);
    
    // Check for proper landmarks
    const landmarks = await page.locator('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], main, nav, header, footer').count();
    expect(landmarks).toBeGreaterThan(0);
    
    // Check for descriptive text
    const ariaDescribedBy = await page.locator('[aria-describedby]').count();
    // This is optional but good to have
    
    // Check that dynamic content updates are announced
    const statusRegions = await page.locator('[role="status"], [aria-live="polite"], [aria-live="assertive"]').count();
    expect(statusRegions).toBeGreaterThan(0);
  });

  test('should have sufficient color contrast', async () => {
    // This is a basic visibility check
    // In a real implementation, you'd use a color contrast analyzer
    
    const textElements = [
      '[data-testid="message-input"]',
      '[data-testid="send-button"]',
      '[data-testid="session-title"]',
      'p', 'span', 'div', 'button'
    ];
    
    for (const selector of textElements) {
      const elements = page.locator(selector);
      const count = await elements.count();
      
      for (let i = 0; i < count; i++) {
        const element = elements.nth(i);
        if (await element.isVisible()) {
          // Check that text is readable (not transparent or same color as background)
          const styles = await element.evaluate(el => {
            const computed = window.getComputedStyle(el);
            return {
              color: computed.color,
              backgroundColor: computed.backgroundColor,
              opacity: computed.opacity
            };
          });
          
          // Basic checks
          expect(styles.opacity).not.toBe('0');
          expect(styles.color).not.toBe('transparent');
        }
      }
    }
  });

  test('should work with high contrast mode', async () => {
    // Simulate high contrast mode
    await page.addStyleTag({
      content: `
        * {
          background: black !important;
          color: white !important;
          border-color: white !important;
        }
        button, input, select, textarea {
          background: black !important;
          color: white !important;
          border: 1px solid white !important;
        }
      `
    });
    
    // Wait for styles to apply
    await page.waitForTimeout(500);
    
    // Verify interface is still usable
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="send-button"]')).toBeVisible();
    
    // Test basic functionality still works
    const messageInput = page.locator('[data-testid="message-input"]');
    await messageInput.fill('High contrast test');
    await expect(messageInput).toHaveValue('High contrast test');
  });

  test('should support reduced motion preferences', async () => {
    // Simulate reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    
    // Check that animations are disabled or reduced
    const animatedElements = await page.locator('[class*="animate"], [class*="transition"]').all();
    
    for (const element of animatedElements) {
      const styles = await element.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          animationDuration: computed.animationDuration,
          transitionDuration: computed.transitionDuration
        };
      });
      
      // Animations should be disabled or very short
      if (styles.animationDuration !== 'none' && styles.animationDuration !== '0s') {
        const duration = parseFloat(styles.animationDuration);
        expect(duration).toBeLessThan(0.2); // Less than 200ms
      }
      
      if (styles.transitionDuration !== 'none' && styles.transitionDuration !== '0s') {
        const duration = parseFloat(styles.transitionDuration);
        expect(duration).toBeLessThan(0.2); // Less than 200ms
      }
    }
  });

  test('should handle focus management correctly', async () => {
    // Test focus trap in modals
    const settingsButton = page.locator('[data-testid="settings-button"]');
    if (await settingsButton.count() > 0) {
      await settingsButton.click();
      
      // Focus should be trapped within the modal
      const modal = page.locator('[role="dialog"], [data-testid="settings-modal"]');
      if (await modal.count() > 0) {
        // Tab through modal elements
        await page.keyboard.press('Tab');
        const focusedElement = page.locator(':focus');
        
        // Focus should be within the modal
        const isWithinModal = await focusedElement.evaluate((focused, modalEl) => {
          return modalEl.contains(focused);
        }, await modal.elementHandle());
        
        expect(isWithinModal).toBe(true);
        
        // Close modal and check focus returns
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        
        // Focus should return to settings button or another appropriate element
        const newFocused = page.locator(':focus');
        await expect(newFocused).toBeVisible();
      }
    }
  });

  test('should provide clear error messages', async () => {
    // Test error message accessibility
    // This would typically involve triggering an error condition
    
    // For now, check that error elements have proper ARIA attributes
    const errorElements = page.locator('[role="alert"], [aria-live="assertive"], .error, [data-testid*="error"]');
    const count = await errorElements.count();
    
    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const element = errorElements.nth(i);
        
        // Error messages should be announced to screen readers
        const hasRole = await element.getAttribute('role');
        const hasAriaLive = await element.getAttribute('aria-live');
        
        expect(hasRole === 'alert' || hasAriaLive === 'assertive' || hasAriaLive === 'polite').toBe(true);
      }
    }
  });
});