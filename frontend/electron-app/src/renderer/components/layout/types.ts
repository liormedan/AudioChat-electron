export interface LayoutConfiguration {
  screenSize: {
    width: number;
    height: number;
  };
  columns: {
    sidebar: number;
    content: number[];
  };
  components: {
    header: ComponentConfig;
    fileUploader: ComponentConfig;
    waveformPlayer: ComponentConfig;
    chatInterface: ComponentConfig;
    fileManager: ComponentConfig;
  };
}

export interface ComponentConfig {
  height: number;
  width?: number;
  visible: boolean;
  collapsed?: boolean;
  position: {
    column: number;
    row: number;
  };
}

export interface ResponsiveBreakpoints {
  desktop: number; // 1920px
  laptop: number; // 1366px
  tablet: number; // 768px
  mobile: number; // 480px
}

export const DEFAULT_BREAKPOINTS: ResponsiveBreakpoints = {
  desktop: 1920,
  laptop: 1366,
  tablet: 768,
  mobile: 480
};

export const DEFAULT_COMPONENT_HEIGHTS = {
  fileUploader: 200,
  waveformPlayer: 300,
  chatInterface: 400,
  fileManager: 400,
  header: 60
} as const;

export type BreakpointName = keyof ResponsiveBreakpoints;
export type ComponentName = keyof typeof DEFAULT_COMPONENT_HEIGHTS;