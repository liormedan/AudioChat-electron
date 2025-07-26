# Audio Chat Studio Repository

This repository hosts two implementations of **Audio Chat Studio**:

- **`my_audio_app/`** – the original PyQt6 application that provides AI‑powered audio editing tools with a Material Design interface.
- **`electron-app/`** – an Electron application built with React, TypeScript and shadcn/ui components for a modern cross‑platform desktop experience.

Each directory contains a detailed README explaining features and development instructions for that version.

## Getting Started

1. **Python (PyQt6 version)**
   - See [`my_audio_app/README.md`](my_audio_app/README.md) for feature overview.
   - Follow [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for environment setup and dependency installation.
   - Run the app with `python my_audio_app/main.py` once dependencies are installed.

2. **Electron (React version)**
   - See [`electron-app/README.md`](electron-app/README.md) for prerequisites and commands.
   - Install Node dependencies with `npm install` and start development with `npm run dev`.

## Specs and Tasks

Development follows spec‑driven planning. Requirements, design notes and task lists can be found under the [`.kiro/specs/`](.kiro/specs) directory. Consult the relevant `requirements.md` and `tasks.md` files before implementing new features.

---

For additional guides and API documentation, browse the `docs/` subdirectory inside `my_audio_app`.
