# Audio Chat Studio - Electron Version

Modern Electron application built with React, TypeScript, and Vite.

## Features

- ⚡ Fast development with Vite
- 🔒 Security-first approach with context isolation
- 🎨 Modern React 18 with TypeScript
- 🛡️ Strict TypeScript configuration
- 📱 Cross-platform desktop application
- 🔄 Hot reload for development

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building

```bash
# Build for production
npm run build

# Package for distribution
npm run package
```

## Project Structure

```
electron-app/
├── src/
│   ├── main/           # Electron main process
│   ├── renderer/       # React application
│   ├── preload/        # Preload scripts
│   └── shared/         # Shared types and utilities
├── dist/               # Built application
└── release/            # Packaged distributables
```

## Security

This application follows Electron security best practices:

- Context isolation enabled
- Node integration disabled
- Secure preload scripts
- IPC message validation
- Content Security Policy

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run package` - Create distributable packages
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking