# audio_utils.py

import os
import glob
import numpy as np
import pygame
from scipy.io import wavfile
import tempfile
import time


def init_audio():
    pygame.mixer.init()


def play_audio(audio_data, fs):
    stop_audio()
    if np.max(np.abs(audio_data)) > 1.0:
        audio_data = audio_data / np.max(np.abs(audio_data))
    audio_int = (audio_data * 32767).astype(np.int16)

    temp_file = f"temp_playback_{int(time.time() * 1000)}.wav"
    wavfile.write(temp_file, fs, audio_int)
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    return temp_file


def stop_audio():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()


def cleanup_temp_files():
    for temp_file in glob.glob("temp_playback_*.wav"):
        try:
            os.remove(temp_file)
        except:
            pass


def save_wav(file_path, audio_data, fs):
    if np.max(np.abs(audio_data)) > 1.0:
        audio_data = audio_data / np.max(np.abs(audio_data))
    audio_int = (audio_data * 32767).astype(np.int16)
    wavfile.write(file_path, fs, audio_int)
