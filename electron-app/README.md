diff --git a/electron-app/README.md b/electron-app/README.md
index b0967ce643a5af4937b25246975e46f36f0e3cb8..f9a109c460a4d65f13e2fcefaeba9c5307bc9c76 100644
--- a/electron-app/README.md
+++ b/electron-app/README.md
@@ -4,67 +4,74 @@ Modern Electron application built with React, TypeScript, and Vite.
 
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
+
+# Optionally open Electron DevTools on startup
+OPEN_DEVTOOLS=true npm run dev
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
-- `npm run type-check` - Run TypeScript type checking
+- `npm run type-check` - Run TypeScript type checking
+
+By default, DevTools remain closed. Set the `OPEN_DEVTOOLS` environment
+variable to `true` (or `1`) to automatically open them when running in
+development mode.
