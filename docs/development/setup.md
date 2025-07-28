# Installation Guide - Audio Chat Studio

## Quick Fix for Current Issues

### Problem 1: sqlite3 Error
The error `ERROR: No matching distribution found for sqlite3` occurs because sqlite3 is built into Python and shouldn't be in requirements.txt.

### Problem 2: Python 3.13 Compatibility
Some packages don't support Python 3.13 yet. We've updated requirements with compatible versions.

## Installation Steps

### Option 1: Smart Installer (Recommended)
```bash
cd my_audio_app
python install_requirements.py
```

### Option 2: Minimal Installation
```bash
cd my_audio_app
pip install -r requirements_minimal.txt
```

### Option 3: Manual Installation
```bash
# Essential packages
pip install PyQt6 qt-material numpy pyqtgraph requests python-dateutil

# Optional audio packages (install if needed)
pip install matplotlib pandas scipy librosa soundfile pydub cryptography
```

### Option 4: Step-by-step Installation
```bash
# 1. Core GUI
pip install PyQt6>=6.4.0
pip install qt-material>=2.14

# 2. Data processing
pip install numpy>=1.21.0
pip install pyqtgraph>=0.13.0

# 3. Utilities
pip install requests>=2.25.0
pip install python-dateutil>=2.8.0

# 4. Optional: Audio processing (may fail on Python 3.13)
pip install matplotlib>=3.5.0
pip install librosa>=0.9.0
pip install soundfile>=0.10.0
pip install pydub>=0.25.0
```

## Verification

After installation, test if the basic components work:

```python
# Test basic imports
python -c "import PyQt6; print('PyQt6: OK')"
python -c "import qt_material; print('qt-material: OK')"
python -c "import numpy; print('numpy: OK')"
python -c "import pyqtgraph; print('pyqtgraph: OK')"

# Test visualization
python visualization_comparison.py
```

## Troubleshooting

### If librosa fails to install:
```bash
# Try older version
pip install librosa==0.9.2

# Or skip audio processing for now
# The app will work without it
```

### If scipy fails:
```bash
# Try older version
pip install scipy==1.9.3
```

### If matplotlib fails:
```bash
# Try older version
pip install matplotlib==3.6.0
```

## What's Working vs What's Optional

### ✅ Essential (Must Work)
- PyQt6 - GUI framework
- qt-material - Dark theme
- numpy - Data processing
- pyqtgraph - High-performance plotting
- requests - HTTP requests
- python-dateutil - Date utilities

### 🔶 Optional (Nice to Have)
- matplotlib - Fallback plotting
- librosa - Advanced audio analysis
- soundfile - Audio file I/O
- pydub - Audio manipulation
- scipy - Scientific computing
- pandas - Data analysis

### 🚀 Ready to Start
Once you have the essential packages installed, you can:

1. Run the visualization demo: `python visualization_comparison.py`
2. Start implementing the audio components from the spec
3. Begin with Task 1: "Set up audio processing foundation"

The application will work with just the essential packages, and you can add audio processing capabilities later when the compatibility issues are resolved.