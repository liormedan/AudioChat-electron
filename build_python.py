

import PyInstaller.__main__
import os
import shutil

# The name for our bundled executable and the directory it will be in
APP_NAME = "server_dist"
SCRIPT_PATH = "server.py"
BUILD_DIR = "py_build"

def main():
    print("--- Running PyInstaller ---")

    # Define PyInstaller arguments
    pyinstaller_args = [
        '--name=%s' % APP_NAME,
        '--onefile',
        '--windowed', # Use --noconsole on non-Windows platforms
        '--distpath=%s' % os.path.join(BUILD_DIR, 'dist'),
        '--workpath=%s' % os.path.join(BUILD_DIR, 'build'),
        '--specpath=%s' % BUILD_DIR,
        SCRIPT_PATH,
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

    print("\n--- PyInstaller build complete ---")
    print(f"Executable created in: {os.path.join(BUILD_DIR, 'dist')}")

    # --- Clean up ---
    # We can optionally remove the build and spec files to keep the directory clean
    # shutil.rmtree(os.path.join(BUILD_DIR, 'build'))
    # os.remove(os.path.join(BUILD_DIR, f'{APP_NAME}.spec'))
    # print("Cleaned up temporary build files.")


if __name__ == "__main__":
    main()

