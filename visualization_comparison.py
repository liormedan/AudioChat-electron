"""
Comparison of different visualization libraries for audio waveforms
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget

# PyQtGraph - High performance, real-time plotting
try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False

# Plotly - Interactive web-based charts
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Matplotlib - Traditional plotting
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PyQtGraphWaveform(QWidget):
    """High-performance waveform using PyQtGraph"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('black')
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Enable mouse interaction
        self.plot_widget.setMouseEnabled(x=True, y=False)  # Only horizontal zoom/pan
        
        layout.addWidget(self.plot_widget)
        
        # Generate sample waveform data
        self.generate_sample_data()
        
    def generate_sample_data(self):
        """Generate sample audio waveform data"""
        # Simulate 5 seconds of audio at 44.1kHz sample rate
        sample_rate = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create complex waveform with multiple frequencies and noise
        waveform = (
            0.5 * np.sin(2 * np.pi * 440 * t) +  # A4 note
            0.3 * np.sin(2 * np.pi * 880 * t) +  # A5 note
            0.1 * np.random.normal(0, 1, len(t))  # Noise
        )
        
        # Add some amplitude modulation for visual interest
        envelope = np.exp(-t / 2) * (1 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
        waveform *= envelope
        
        # Downsample for display (show every 100th sample for performance)
        display_step = 100
        t_display = t[::display_step]
        waveform_display = waveform[::display_step]
        
        # Plot the waveform
        pen = pg.mkPen(color='cyan', width=1)
        self.plot_widget.plot(t_display, waveform_display, pen=pen, name='Waveform')
        
        # Add playback position indicator
        self.position_line = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('red', width=2))
        self.plot_widget.addItem(self.position_line)
        
        # Add selection region
        self.selection_region = pg.LinearRegionItem(values=[1.0, 2.5], brush=pg.mkBrush(255, 255, 0, 50))
        self.plot_widget.addItem(self.selection_region)
        
    def set_playback_position(self, position):
        """Update playback position indicator"""
        self.position_line.setPos(position)
        
    def get_selection(self):
        """Get current selection region"""
        return self.selection_region.getRegion()


class MatplotlibWaveform(QWidget):
    """Traditional waveform using Matplotlib"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 4), facecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: black;")
        
        layout.addWidget(self.canvas)
        
        # Generate sample data
        self.generate_sample_data()
        
    def generate_sample_data(self):
        """Generate sample audio waveform data"""
        # Same data generation as PyQtGraph version
        sample_rate = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        waveform = (
            0.5 * np.sin(2 * np.pi * 440 * t) +
            0.3 * np.sin(2 * np.pi * 880 * t) +
            0.1 * np.random.normal(0, 1, len(t))
        )
        
        envelope = np.exp(-t / 2) * (1 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
        waveform *= envelope
        
        # Downsample for display
        display_step = 100
        t_display = t[::display_step]
        waveform_display = waveform[::display_step]
        
        # Create plot
        ax = self.figure.add_subplot(111, facecolor='black')
        ax.plot(t_display, waveform_display, color='cyan', linewidth=0.8)
        ax.set_xlabel('Time (s)', color='white')
        ax.set_ylabel('Amplitude', color='white')
        ax.grid(True, alpha=0.3)
        ax.tick_params(colors='white')
        
        # Add playback position
        ax.axvline(x=1.5, color='red', linewidth=2, label='Playback Position')
        
        # Add selection region
        ax.axvspan(1.0, 2.5, alpha=0.2, color='yellow', label='Selection')
        
        ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()


class VisualizationComparison(QMainWindow):
    """Main window comparing different visualization approaches"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Visualization Comparison")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                border-bottom: 2px solid #4CAF50;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add PyQtGraph tab (recommended)
        if PYQTGRAPH_AVAILABLE:
            pyqtgraph_widget = PyQtGraphWaveform()
            tab_widget.addTab(pyqtgraph_widget, "PyQtGraph (Recommended)")
        
        # Add Matplotlib tab (fallback)
        if MATPLOTLIB_AVAILABLE:
            matplotlib_widget = MatplotlibWaveform()
            tab_widget.addTab(matplotlib_widget, "Matplotlib (Fallback)")
        
        layout.addWidget(tab_widget)


def main():
    app = QApplication(sys.argv)
    
    # Check available libraries
    print("Available visualization libraries:")
    print(f"- PyQtGraph: {'✓' if PYQTGRAPH_AVAILABLE else '✗'}")
    print(f"- Plotly: {'✓' if PLOTLY_AVAILABLE else '✗'}")
    print(f"- Matplotlib: {'✓' if MATPLOTLIB_AVAILABLE else '✗'}")
    
    if not any([PYQTGRAPH_AVAILABLE, MATPLOTLIB_AVAILABLE]):
        print("No visualization libraries available. Please install pyqtgraph or matplotlib.")
        return
    
    window = VisualizationComparison()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()