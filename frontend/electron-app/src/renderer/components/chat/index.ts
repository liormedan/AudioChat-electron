// Chat Components
export { SessionManager } from './session-manager';
export { ChatInterface } from './chat-interface';
export { CompactChatInterface } from './compact-chat-interface';
export { CompactChatInterfaceDemo } from './compact-chat-interface-demo';
export { MessageList } from './message-list';
export { InputArea } from './input-area';
export { SessionSidebar } from './session-sidebar';
export { HistoryPanel } from './history-panel';
export { SearchPanel } from './search-panel';
export { AdvancedSettingsPanel } from './settings-panel';
export { PerformanceMonitor } from './performance-monitor';

// Audio Chat Components
export { AudioChatMessage } from './AudioChatMessage';
export { AudioCommandSuggestions } from './audio-command-suggestions';
export { AudioPreview } from './audio-preview';
export { AudioProcessingStatus } from './audio-processing-status';

// Legacy export for backward compatibility
export { default as AudioChatMessageSimple } from './audio-chat-message';