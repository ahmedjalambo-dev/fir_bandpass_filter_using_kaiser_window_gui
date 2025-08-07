import numpy as np
from scipy import signal


def design_kaiser_bandpass_filter(
    lowcut, highcut, fs, transition_width=100, stopband_attn=60
):
    nyquist = fs / 2
    low = lowcut / nyquist
    high = highcut / nyquist
    delta = 10 ** (-stopband_attn / 20)
    A = -20 * np.log10(delta)

    if A > 50:
        beta = 0.1102 * (A - 8.7)
    elif A >= 21:
        beta = 0.5842 * (A - 21) ** 0.4 + 0.07886 * (A - 21)
    else:
        beta = 0.0

    transition_norm = transition_width / nyquist
    M = int(np.ceil((A - 8) / (2.285 * transition_norm * np.pi)))
    if M % 2 == 0:
        M += 1

    coeffs = signal.firwin(M, [low, high], window=("kaiser", beta), pass_zero=False)
    return coeffs, beta, M


def apply_fir_filter(audio_data, filter_coeffs):
    return signal.filtfilt(filter_coeffs, 1, audio_data)
