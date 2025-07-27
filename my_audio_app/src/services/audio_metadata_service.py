import os
import numpy as np
import librosa
import librosa.display
from typing import Dict, Any, Optional, List, Tuple
import warnings
import tempfile
import json
from datetime import datetime

# Suppress librosa warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning, module='librosa')

class AudioMetadataService:
    """Advanced audio metadata extraction service using librosa."""
    
    def __init__(self):
        """Initialize the audio metadata service."""
        self.default_sr = 22050  # Default sample rate for librosa
        self.hop_length = 512    # Default hop length for analysis
        self.n_fft = 2048       # Default FFT window size
    
    def extract_comprehensive_metadata(self, file_path: str, include_advanced: bool = True) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from audio file.
        
        Args:
            file_path: Path to the audio file
            include_advanced: Whether to include computationally expensive features
            
        Returns:
            Dictionary with comprehensive metadata
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            
            # Basic information
            metadata = {
                "success": True,
                "file_info": self._get_file_info(file_path),
                "audio_properties": self._get_audio_properties(y, sr),
                "spectral_features": self._get_spectral_features(y, sr),
                "temporal_features": self._get_temporal_features(y, sr),
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            if include_advanced:
                metadata.update({
                    "advanced_features": self._get_advanced_features(y, sr),
                    "harmonic_analysis": self._get_harmonic_analysis(y, sr),
                    "rhythm_analysis": self._get_rhythm_analysis(y, sr)
                })
            
            return metadata
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract metadata: {str(e)}",
                "file_path": file_path
            }
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information."""
        stat = os.stat(file_path)
        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": stat.st_size,
            "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime,
            "file_extension": os.path.splitext(file_path)[1].lower()
        }
    
    def _get_audio_properties(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Get basic audio properties."""
        duration = librosa.get_duration(y=y, sr=sr)
        
        return {
            "duration": duration,
            "duration_formatted": self._format_duration(duration),
            "sample_rate": sr,
            "samples": len(y),
            "channels": 1 if len(y.shape) == 1 else y.shape[0],
            "bit_depth": "32-bit float (librosa processed)",
            "nyquist_frequency": sr / 2,
            "frame_count": len(y),
            "rms_energy": float(np.sqrt(np.mean(y**2))),
            "max_amplitude": float(np.max(np.abs(y))),
            "dynamic_range": float(np.max(y) - np.min(y))
        }
    
    def _get_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract spectral features."""
        try:
            # Spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCCs (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            return {
                "spectral_centroid": {
                    "mean": float(np.mean(spectral_centroids)),
                    "std": float(np.std(spectral_centroids)),
                    "min": float(np.min(spectral_centroids)),
                    "max": float(np.max(spectral_centroids))
                },
                "spectral_rolloff": {
                    "mean": float(np.mean(spectral_rolloff)),
                    "std": float(np.std(spectral_rolloff)),
                    "min": float(np.min(spectral_rolloff)),
                    "max": float(np.max(spectral_rolloff))
                },
                "spectral_bandwidth": {
                    "mean": float(np.mean(spectral_bandwidth)),
                    "std": float(np.std(spectral_bandwidth)),
                    "min": float(np.min(spectral_bandwidth)),
                    "max": float(np.max(spectral_bandwidth))
                },
                "zero_crossing_rate": {
                    "mean": float(np.mean(zcr)),
                    "std": float(np.std(zcr)),
                    "min": float(np.min(zcr)),
                    "max": float(np.max(zcr))
                },
                "mfcc_features": {
                    "shape": mfccs.shape,
                    "mean_per_coefficient": [float(np.mean(mfcc)) for mfcc in mfccs],
                    "std_per_coefficient": [float(np.std(mfcc)) for mfcc in mfccs]
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to extract spectral features: {str(e)}"}
    
    def _get_temporal_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract temporal features."""
        try:
            # RMS energy over time
            rms = librosa.feature.rms(y=y)[0]
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            # Tempo estimation
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)
            
            return {
                "rms_energy": {
                    "mean": float(np.mean(rms)),
                    "std": float(np.std(rms)),
                    "min": float(np.min(rms)),
                    "max": float(np.max(rms))
                },
                "onsets": {
                    "count": len(onset_times),
                    "times": onset_times.tolist()[:50],  # Limit to first 50 for JSON size
                    "density": len(onset_times) / librosa.get_duration(y=y, sr=sr)
                },
                "tempo": {
                    "bpm": float(tempo),
                    "beat_count": len(beat_times),
                    "beat_times": beat_times.tolist()[:50],  # Limit to first 50
                    "average_beat_interval": float(np.mean(np.diff(beat_times))) if len(beat_times) > 1 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to extract temporal features: {str(e)}"}
    
    def _get_advanced_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract advanced audio features (computationally expensive)."""
        try:
            # Chroma features (pitch class profiles)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Tonnetz (tonal centroid features)
            tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            
            # Poly features
            poly_features = librosa.feature.poly_features(y=y, sr=sr)
            
            return {
                "chroma_features": {
                    "shape": chroma.shape,
                    "mean_per_pitch_class": [float(np.mean(chroma[i])) for i in range(chroma.shape[0])],
                    "dominant_pitch_class": int(np.argmax(np.mean(chroma, axis=1)))
                },
                "tonnetz_features": {
                    "shape": tonnetz.shape,
                    "mean_per_dimension": [float(np.mean(tonnetz[i])) for i in range(tonnetz.shape[0])]
                },
                "spectral_contrast": {
                    "shape": contrast.shape,
                    "mean_per_band": [float(np.mean(contrast[i])) for i in range(contrast.shape[0])]
                },
                "poly_features": {
                    "shape": poly_features.shape,
                    "coefficients": [float(np.mean(poly_features[i])) for i in range(poly_features.shape[0])]
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to extract advanced features: {str(e)}"}
    
    def _get_harmonic_analysis(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Perform harmonic analysis."""
        try:
            # Separate harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            
            # Pitch tracking
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get fundamental frequency estimates
            f0 = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    f0.append(pitch)
            
            return {
                "harmonic_percussive_separation": {
                    "harmonic_energy": float(np.sum(y_harmonic**2)),
                    "percussive_energy": float(np.sum(y_percussive**2)),
                    "harmonic_ratio": float(np.sum(y_harmonic**2) / (np.sum(y_harmonic**2) + np.sum(y_percussive**2)))
                },
                "pitch_analysis": {
                    "fundamental_frequencies": f0[:100],  # Limit for JSON size
                    "pitch_count": len(f0),
                    "mean_f0": float(np.mean(f0)) if f0 else 0,
                    "std_f0": float(np.std(f0)) if f0 else 0,
                    "pitch_range": float(np.max(f0) - np.min(f0)) if f0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to perform harmonic analysis: {str(e)}"}
    
    def _get_rhythm_analysis(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Perform rhythm analysis."""
        try:
            # Tempogram
            hop_length = 512
            tempogram = librosa.feature.tempogram(y=y, sr=sr, hop_length=hop_length)
            
            # Beat tracking with multiple methods
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Dynamic tempo
            tempo_dynamic = librosa.beat.tempo(y=y, sr=sr, aggregate=None)
            
            return {
                "tempogram_analysis": {
                    "shape": tempogram.shape,
                    "tempo_bins": tempogram.shape[0],
                    "time_frames": tempogram.shape[1]
                },
                "beat_tracking": {
                    "global_tempo": float(tempo),
                    "beat_count": len(beats),
                    "beat_consistency": float(np.std(np.diff(beats))) if len(beats) > 1 else 0
                },
                "dynamic_tempo": {
                    "tempo_variation": tempo_dynamic.tolist()[:50] if len(tempo_dynamic) > 0 else [],
                    "tempo_stability": float(np.std(tempo_dynamic)) if len(tempo_dynamic) > 0 else 0,
                    "mean_tempo": float(np.mean(tempo_dynamic)) if len(tempo_dynamic) > 0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to perform rhythm analysis: {str(e)}"}
    
    def extract_waveform_data(self, file_path: str, max_points: int = 1000) -> Dict[str, Any]:
        """
        Extract waveform data for visualization.
        
        Args:
            file_path: Path to the audio file
            max_points: Maximum number of points to return for visualization
            
        Returns:
            Dictionary with waveform data
        """
        try:
            y, sr = librosa.load(file_path, sr=None)
            
            # Downsample for visualization if needed
            if len(y) > max_points:
                step = len(y) // max_points
                y_downsampled = y[::step]
            else:
                y_downsampled = y
            
            # Time axis
            time_axis = np.linspace(0, len(y) / sr, len(y_downsampled))
            
            return {
                "success": True,
                "waveform": y_downsampled.tolist(),
                "time_axis": time_axis.tolist(),
                "sample_rate": sr,
                "duration": len(y) / sr,
                "original_samples": len(y),
                "downsampled_samples": len(y_downsampled)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract waveform data: {str(e)}"
            }
    
    def extract_spectrogram_data(self, file_path: str, n_fft: int = 2048, hop_length: int = 512) -> Dict[str, Any]:
        """
        Extract spectrogram data for visualization.
        
        Args:
            file_path: Path to the audio file
            n_fft: FFT window size
            hop_length: Hop length for STFT
            
        Returns:
            Dictionary with spectrogram data
        """
        try:
            y, sr = librosa.load(file_path, sr=None)
            
            # Compute spectrogram
            D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
            magnitude = np.abs(D)
            
            # Convert to dB
            magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
            
            # Frequency and time axes
            freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
            times = librosa.frames_to_time(np.arange(magnitude.shape[1]), sr=sr, hop_length=hop_length)
            
            return {
                "success": True,
                "spectrogram": magnitude_db.tolist(),
                "frequencies": freqs.tolist(),
                "times": times.tolist(),
                "shape": magnitude_db.shape,
                "sample_rate": sr,
                "n_fft": n_fft,
                "hop_length": hop_length
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract spectrogram data: {str(e)}"
            }
    
    def _format_duration(self, duration: float) -> str:
        """Format duration in human-readable format."""
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        milliseconds = int((duration % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        else:
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def get_audio_summary(self, file_path: str) -> Dict[str, Any]:
        """
        Get a quick summary of audio file characteristics.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with audio summary
        """
        try:
            # Extract basic metadata without expensive computations
            metadata = self.extract_comprehensive_metadata(file_path, include_advanced=False)
            
            if not metadata["success"]:
                return metadata
            
            # Create summary
            audio_props = metadata["audio_properties"]
            spectral = metadata["spectral_features"]
            temporal = metadata["temporal_features"]
            
            summary = {
                "success": True,
                "file_name": metadata["file_info"]["file_name"],
                "duration": audio_props["duration_formatted"],
                "sample_rate": f"{audio_props['sample_rate']} Hz",
                "file_size": f"{metadata['file_info']['file_size_mb']} MB",
                "brightness": self._classify_brightness(spectral["spectral_centroid"]["mean"]),
                "energy_level": self._classify_energy(audio_props["rms_energy"]),
                "tempo": f"{temporal['tempo']['bpm']:.1f} BPM" if "tempo" in temporal else "Unknown",
                "onset_density": f"{temporal['onsets']['density']:.2f} onsets/sec" if "onsets" in temporal else "Unknown",
                "dynamic_range": self._classify_dynamic_range(audio_props["dynamic_range"])
            }
            
            return summary
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate audio summary: {str(e)}"
            }
    
    def _classify_brightness(self, spectral_centroid: float) -> str:
        """Classify audio brightness based on spectral centroid."""
        if spectral_centroid < 1000:
            return "Dark"
        elif spectral_centroid < 2000:
            return "Warm"
        elif spectral_centroid < 4000:
            return "Balanced"
        elif spectral_centroid < 8000:
            return "Bright"
        else:
            return "Very Bright"
    
    def _classify_energy(self, rms_energy: float) -> str:
        """Classify audio energy level."""
        if rms_energy < 0.01:
            return "Very Low"
        elif rms_energy < 0.05:
            return "Low"
        elif rms_energy < 0.1:
            return "Medium"
        elif rms_energy < 0.2:
            return "High"
        else:
            return "Very High"
    
    def _classify_dynamic_range(self, dynamic_range: float) -> str:
        """Classify dynamic range."""
        if dynamic_range < 0.5:
            return "Compressed"
        elif dynamic_range < 1.0:
            return "Limited"
        elif dynamic_range < 1.5:
            return "Good"
        else:
            return "Wide"