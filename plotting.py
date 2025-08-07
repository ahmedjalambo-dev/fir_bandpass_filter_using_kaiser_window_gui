# plotting.py

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz


def generate_analysis_plot(original_audio, filtered_audio, fs, coeffs, lowcut, highcut):
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))
    fig.patch.set_facecolor("white")

    zoom_samples = min(int(0.05 * fs), 2000, len(original_audio))
    t = np.arange(zoom_samples) / fs

    # Original waveform
    axes[0].plot(t, original_audio[:zoom_samples], color="gray")
    axes[0].set_title("Original Audio (Zoomed In)")
    axes[0].set_xlabel("Time [s]")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True, alpha=0.3)

    # Filtered waveform
    axes[1].plot(t, filtered_audio[:zoom_samples], color="blue")
    axes[1].set_title("Filtered Audio (Zoomed In)")
    axes[1].set_xlabel("Time [s]")
    axes[1].set_ylabel("Amplitude")
    axes[1].grid(True, alpha=0.3)

    # Frequency response
    w, h = freqz(coeffs, worN=8000, fs=fs)
    axes[2].plot(w, 20 * np.log10(np.abs(h)), color="purple")
    axes[2].axvline(
        lowcut, color="red", linestyle="--", label=f"Lower cutoff: {lowcut:.0f} Hz"
    )
    axes[2].axvline(
        highcut, color="red", linestyle="--", label=f"Upper cutoff: {highcut:.0f} Hz"
    )
    axes[2].set_title("Bandpass Filter Frequency Response")
    axes[2].set_xlabel("Frequency [Hz]")
    axes[2].set_ylabel("Magnitude [dB]")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    return fig
