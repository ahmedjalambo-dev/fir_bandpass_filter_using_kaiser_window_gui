# gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import numpy as np
from scipy.io import wavfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from filter_logic import design_kaiser_bandpass_filter, apply_fir_filter
from audio_utils import init_audio, play_audio, stop_audio, cleanup_temp_files, save_wav
from plotting import generate_analysis_plot


class FIRFilterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FIR Bandpass Filter using Kaiser Window")
        self.root.geometry("1600x900")
        self.root.configure(bg="#f0f0f0")

        init_audio()

        # Audio and filter attributes
        self.input_file = None
        self.original_audio = None
        self.filtered_audio = None
        self.fs = None
        self.filter_coeffs = None
        self.current_plot_fig = None
        self.current_temp_file = None

        # Filter parameter variables
        self.lowcut = tk.DoubleVar(value=80)
        self.highcut = tk.DoubleVar(value=6000)
        self.transition_width = tk.DoubleVar(value=40)
        self.stopband_attn = tk.DoubleVar(value=100)

        self.setup_ui()

    def setup_ui(self):
        self.setup_title()
        self.setup_main_content()

    def setup_title(self):
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill="x", padx=10, pady=(10, 0))
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text="FIR Bandpass Filter using Kaiser Window",
            font=("Arial", 20),
            fg="white",
            bg="#2c3e50",
        ).pack(pady=15)

    def setup_main_content(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_left_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        panel = tk.Frame(self.main_frame, bg="#ecf0f1", width=400)
        panel.pack(side="left", fill="y", padx=(0, 10))
        panel.pack_propagate(False)

        # File selection
        file_section = tk.LabelFrame(
            panel, text="File Selection", font=("Arial", 12, "bold"), bg="#ecf0f1"
        )
        file_section.pack(fill="x", padx=10, pady=10)

        tk.Button(
            file_section,
            text="📂 Browse Input Audio File",
            command=self.browse_input_file,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            height=2,
        ).pack(pady=10, fill="x", padx=10)

        self.input_label = tk.Label(
            file_section, text="No file selected", bg="#ecf0f1", font=("Arial", 9)
        )
        self.input_label.pack(pady=5)

        # Parameters
        params_section = tk.LabelFrame(
            panel, text="🎛️ Filter Parameters", font=("Arial", 12, "bold"), bg="#ecf0f1"
        )
        params_section.pack(fill="x", padx=10, pady=10)

        self.create_parameter_control(
            params_section, "Lower Cutoff (Hz):", self.lowcut, 20, 1000
        )
        self.create_parameter_control(
            params_section, "Upper Cutoff (Hz):", self.highcut, 1000, 20000
        )
        self.create_parameter_control(
            params_section, "Transition Width (Hz):", self.transition_width, 10, 200
        )
        self.create_parameter_control(
            params_section, "Stopband Attenuation (dB):", self.stopband_attn, 40, 120
        )

        tk.Button(
            params_section,
            text="🔄 Reset to Default Values",
            command=self.reset_to_defaults,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=(10, 5), fill="x", padx=10)

        tk.Button(
            params_section,
            text="🚀 Process Audio",
            command=self.process_audio,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
        ).pack(pady=10, fill="x", padx=10)

        self.progress = ttk.Progressbar(params_section, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=5)

        self.status_label = tk.Label(
            params_section,
            text="Ready to process audio",
            bg="#ecf0f1",
            font=("Arial", 9),
            fg="#7f8c8d",
        )
        self.status_label.pack(pady=5)

        # Playback and save
        self.setup_playback_section(panel)

    def setup_playback_section(self, parent):
        playback_section = tk.LabelFrame(
            parent, text="🎧 Playback & Save", font=("Arial", 12, "bold"), bg="#ecf0f1"
        )
        playback_section.pack(fill="x", padx=10, pady=(0, 10))

        frame = tk.Frame(playback_section, bg="#ecf0f1")
        frame.pack(pady=5, fill="x")

        tk.Button(
            frame,
            text="▶️ Play Original",
            command=self.play_original,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            frame,
            text="▶️ Play Filtered",
            command=self.play_filtered,
            bg="#27ae60",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            frame,
            text="⏹️ Stop",
            command=stop_audio,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            playback_section,
            text="💾 Save Filtered Audio",
            command=self.save_audio,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=10, fill="x", padx=10)

    def setup_right_panel(self):
        self.results_canvas_frame = tk.Frame(self.main_frame, bg="white")
        self.results_canvas_frame.pack(
            side="right", fill="both", expand=True, padx=10, pady=(0, 10)
        )

        tk.Label(
            self.results_canvas_frame,
            text="Select an audio file and click 'Process Audio' to see results here",
            font=("Arial", 11),
            fg="#7f8c8d",
            bg="white",
        ).pack(expand=True)

    def create_parameter_control(self, parent, label, variable, min_val, max_val):
        frame = tk.Frame(parent, bg="#ecf0f1")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text=label, bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w")

        control = tk.Frame(frame, bg="#ecf0f1")
        control.pack(fill="x")

        tk.Scale(
            control,
            from_=min_val,
            to=max_val,
            variable=variable,
            orient="horizontal",
            bg="#ecf0f1",
            font=("Arial", 9),
        ).pack(side="left", fill="x", expand=True)

        tk.Entry(control, textvariable=variable, width=8, font=("Arial", 9)).pack(
            side="right", padx=(5, 0)
        )

    def reset_to_defaults(self):
        self.lowcut.set(80)
        self.highcut.set(6000)
        self.transition_width.set(40)
        self.stopband_attn.set(100)
        self.status_label.config(text="Filter parameters reset to default values.")

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if file_path:
            self.input_file = file_path
            self.input_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.load_audio_info()

    def load_audio_info(self):
        try:
            self.fs, audio_data = wavfile.read(self.input_file)
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            self.original_audio = audio_data
            duration = len(audio_data) / self.fs
            self.status_label.config(
                text=f"Sample Rate: {self.fs} Hz | Duration: {duration:.2f}s"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not load audio file: {str(e)}")

    def process_audio(self):
        if not self.input_file:
            messagebox.showwarning(
                "Warning", "Please select an input audio file first."
            )
            return

        thread = threading.Thread(target=self._process_audio_thread)
        thread.daemon = True
        thread.start()

    def _process_audio_thread(self):
        try:
            self.root.after(0, self.progress.start)
            self.root.after(
                0, lambda: self.status_label.config(text="Processing audio...")
            )

            coeffs, _, _ = design_kaiser_bandpass_filter(
                self.lowcut.get(),
                self.highcut.get(),
                self.fs,
                self.transition_width.get(),
                self.stopband_attn.get(),
            )

            self.filter_coeffs = coeffs
            self.filtered_audio = apply_fir_filter(self.original_audio, coeffs)

            self.root.after(0, self._update_results)
            self.root.after(0, self.progress.stop)
            self.root.after(
                0, lambda: self.status_label.config(text="Processing completed!")
            )
        except Exception as e:
            self.root.after(0, self.progress.stop)
            self.root.after(
                0, lambda: messagebox.showerror("Error", f"Processing failed: {str(e)}")
            )

    def _update_results(self):
        for widget in self.results_canvas_frame.winfo_children():
            widget.destroy()

        fig = generate_analysis_plot(
            self.original_audio,
            self.filtered_audio,
            self.fs,
            self.filter_coeffs,
            self.lowcut.get(),
            self.highcut.get(),
        )

        self.current_plot_fig = fig

        toolbar_frame = tk.Frame(self.results_canvas_frame, bg="#f0f0f0", height=50)
        toolbar_frame.pack(side="top", fill="x")
        toolbar_frame.pack_propagate(False)

        canvas = FigureCanvasTkAgg(fig, master=self.results_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=(0, 5))

        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        toolbar.config(bg="#f0f0f0")
        toolbar.pack(side="top", anchor="w", padx=5, pady=2)

    def play_original(self):
        if self.original_audio is not None:
            self.current_temp_file = play_audio(self.original_audio, self.fs)
        else:
            messagebox.showwarning("Warning", "No original audio loaded.")

    def play_filtered(self):
        if self.filtered_audio is not None:
            self.current_temp_file = play_audio(self.filtered_audio, self.fs)
        else:
            messagebox.showwarning(
                "Warning", "No filtered audio available. Process audio first."
            )

    def save_audio(self):
        if self.filtered_audio is None:
            messagebox.showwarning(
                "Warning", "No filtered audio to save. Process audio first."
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Filtered Audio",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if file_path:
            try:
                save_wav(file_path, self.filtered_audio, self.fs)
                messagebox.showinfo(
                    "Success", f"Filtered audio saved successfully!\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not save audio: {str(e)}")

    def cleanup(self):
        stop_audio()
        cleanup_temp_files()
