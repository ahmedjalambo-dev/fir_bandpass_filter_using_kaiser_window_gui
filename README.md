## FIR Bandpass Filter GUI

This project is a Python-based desktop application that provides a graphical user interface (GUI) for speech noise reduction system based on a Finite Impulse Response (FIR) bandpass filter designed using the Kaiser Window method. Targeting the 80 Hz – 6 kHz range, the filter suppresses low-frequency hums and high-frequency hiss while preserving speech clarity and intelligibility. 

Users can load a `.wav` file, define the filter's parameters, process the audio, and then visualize the results. The application also allows for playback of both the original and filtered audio and saving the processed audio to a new file.

### 📱 Screenshot

<img width="1590" height="927" alt="image" src="https://github.com/user-attachments/assets/9d294085-3193-42a4-8c78-dd9fa701bf77" />


### ⚡ Features

  * **Load Audio:** Browse and load `.wav` audio files. The application automatically reads the sample rate and converts the audio to a normalized float format.
  * **Filter Parameter Control:** Interactively adjust filter parameters using sliders and entry boxes:
      * Lower Cutoff Frequency (Hz)
      * Upper Cutoff Frequency (Hz)
      * Transition Width (Hz)
      * Stopband Attenuation (dB)
  * **Kaiser Window Design:** Automatically calculates the required filter order (M) and beta parameter for the Kaiser window based on the specified parameters.
  * **Filter Application:** Applies the designed FIR filter to the audio data using a zero-phase `filtfilt` (forward-backward) filter to prevent phase distortion.
  * **Visual Analysis:** Generates a 3-panel Matplotlib plot embedded within the GUI:
    1.  **Original Audio Waveform** (zoomed)
    2.  **Filtered Audio Waveform** (zoomed)
    3.  **Filter Frequency Response** (in dB), showing the filter's shape, passband, and cutoff frequencies.
  * **Audio Playback:**
      * Play the original, unprocessed audio.
      * Play the newly filtered audio to hear the changes immediately.
      * Stop playback at any time.
  * **Save Filtered Audio:** Export the processed audio as a new `.wav` file.
  * **Threading:** Audio processing is run in a separate thread to prevent the GUI from freezing during computation.

### 🔧 How to Run

1.  **Install Dependencies:**
    This project requires Python and several scientific libraries. You can install them using pip:

    ```sh
    pip install numpy scipy matplotlib pygame
    ```

    (Tkinter is typically included with standard Python installations).

2.  **Run the Application:**
    Navigate to the project's root directory and run the `__main__.py` file:

    ```sh
    python .
    ```

    or

    ```sh
    python __main__.py
    ```

### 📁 Project Structure

  * **`__main__.py`**: The main entry point for the application. It initializes the Tkinter root and the `FIRFilterGUI` class.
  * **`gui.py`**: The core of the application. This file defines the `FIRFilterGUI` class, which builds all Tkinter UI elements, manages user input, and coordinates calls to the logic, plotting, and audio utility modules.
  * **`filter_logic.py`**: Contains the core digital signal processing (DSP) functions:
      * `design_kaiser_bandpass_filter()`: Uses `scipy.signal.firwin` to design the filter coefficients based on user parameters.
      * `apply_fir_filter()`: Uses `scipy.signal.filtfilt` to apply the filter to the audio data.
  * **`plotting.py`**:
      * `generate_analysis_plot()`: Uses Matplotlib to create the 3-panel figure comparing original/filtered waveforms and showing the filter's frequency response (calculated with `scipy.signal.freqz`).
  * **`audio_utils.py`**:
      * Manages all audio playback using `pygame.mixer`.
      * Handles saving the filtered audio to a `.wav` file using `scipy.io.wavfile.write`.

      * Manages the creation and cleanup of temporary files used for playback.

