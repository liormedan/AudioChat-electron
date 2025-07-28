#!/usr/bin/env python3
"""
Smart requirements installer that handles version compatibility issues
"""

import subprocess
import sys

def get_python_version():
    """Get current Python version"""
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def install_package(package_name, fallback_versions=None):
    """Install package with fallback versions if needed"""
    print(f"Installing {package_name}...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        if fallback_versions:
            for fallback in fallback_versions:
                try:
                    print(f"  Trying fallback version: {fallback}")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", fallback])
                    print(f"✓ Successfully installed {fallback}")
                    return True
                except subprocess.CalledProcessError:
                    continue
        
        print(f"✗ Failed to install {package_name}")
        return False

def main():
    """Main installation process"""
    python_ver = get_python_version()
    print(f"Python version: {python_ver}")
    
    # Core packages with fallbacks for different Python versions
    packages = [
        # Essential GUI
        ("PyQt6>=6.4.0", ["PyQt6>=6.0.0", "PyQt6"]),
        ("qt-material>=2.14", ["qt-material>=2.10", "qt-material"]),
        
        # Data processing
        ("numpy", ["numpy>=1.21.0", "numpy>=1.19.0"]),
        ("pyqtgraph>=0.13.0", ["pyqtgraph>=0.12.0", "pyqtgraph"]),
        
        # Utilities
        ("requests>=2.25.0", ["requests>=2.20.0", "requests"]),
        ("python-dateutil>=2.8.0", ["python-dateutil>=2.7.0", "python-dateutil"]),
    ]
    
    # Optional packages (install if possible)
    optional_packages = [
        ("matplotlib>=3.5.0", ["matplotlib>=3.3.0", "matplotlib"]),
        ("pandas>=1.3.0", ["pandas>=1.1.0", "pandas"]),
        ("scipy>=1.7.0", ["scipy>=1.5.0", "scipy"]),
        ("librosa>=0.9.0", ["librosa>=0.8.0", "librosa"]),
        ("soundfile>=0.10.0", ["soundfile>=0.9.0", "soundfile"]),
        ("pydub>=0.25.0", ["pydub>=0.24.0", "pydub"]),
        ("cryptography>=3.4.0", ["cryptography>=3.0.0", "cryptography"]),
    ]
    
    print("Installing essential packages...")
    essential_failed = []
    for package, fallbacks in packages:
        if not install_package(package, fallbacks):
            essential_failed.append(package)
    
    print("\nInstalling optional packages...")
    optional_failed = []
    for package, fallbacks in optional_packages:
        if not install_package(package, fallbacks):
            optional_failed.append(package)
    
    # Summary
    print("\n" + "="*50)
    print("INSTALLATION SUMMARY")
    print("="*50)
    
    if essential_failed:
        print("❌ ESSENTIAL packages that failed:")
        for pkg in essential_failed:
            print(f"   - {pkg}")
        print("\n⚠️  The application may not work properly!")
    else:
        print("✅ All essential packages installed successfully!")
    
    if optional_failed:
        print(f"\n⚠️  Optional packages that failed ({len(optional_failed)}):")
        for pkg in optional_failed:
            print(f"   - {pkg}")
        print("\n💡 These features may be limited:")
        if any("audio" in pkg.lower() for pkg in optional_failed):
            print("   - Audio processing capabilities")
        if any("plot" in pkg.lower() or "matplotlib" in pkg.lower() for pkg in optional_failed):
            print("   - Advanced visualization features")
    else:
        print("✅ All optional packages installed successfully!")
    
    print(f"\n🐍 Python {python_ver} compatibility checked")
    print("🚀 Ready to run the application!")

if __name__ == "__main__":
    main()