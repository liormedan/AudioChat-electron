
import '@testing-library/jest-dom';

// Mock scrollIntoView for JSDOM environment
if (typeof Element !== 'undefined') {
  Element.prototype.scrollIntoView = vi.fn();
}
