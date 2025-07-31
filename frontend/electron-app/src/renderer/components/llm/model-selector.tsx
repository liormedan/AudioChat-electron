// Re-export the enhanced model selector as the main ModelSelector
export { EnhancedModelSelector as ModelSelector } from './enhanced-model-selector';

// Also export the enhanced version directly for explicit usage
export { EnhancedModelSelector } from './enhanced-model-selector';

// Export types for external usage
export type {
  ModelMetrics,
  ModelCapability,
  LLMModel,
  ModelRecommendation,
  QuickSwitchOption,
  EnhancedModelSelectorProps as ModelSelectorProps
} from './enhanced-model-selector';