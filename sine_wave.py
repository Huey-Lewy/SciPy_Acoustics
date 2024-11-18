# sine_wave.py
"""
This module generates and plots a sine wave.
"""

import numpy as np
import matplotlib.pyplot as plt

def generate_sine_wave(frequency=440.0, amplitude=1.0, duration=1.0, sample_rate=4410):
    """
    Generates a sine wave of given frequency and amplitude.

    Args:
        frequency (float): The frequency of the sine wave.
        amplitude (float): The amplitude of the sine wave.
        duration (float): The duration of the sine wave.
        sample_rate (int): The sample rate of the sine wave.

    Returns:
        tuple: Times values (np.ndarry) and sine wave values (np.ndarray).
    """

    times_values = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    sine_wave_values = amplitude * np.sin(2 * np.pi * frequency * times_values)

    return times_values, sine_wave_values

def plot_sine_wave(times_values, sine_wave_values):
    """
    Plots a sine wave of given frequency and amplitude.

    Args:
        times_values (np.ndarry): The times values of the sine wave.
        sine_wave_values (np.ndarry): The sine wave values.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(times_values, sine_wave_values)
    plt.title("Sine Wave")
    plt.xlabel("Times (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Example usages
    wave_frequency = 25         # Audio Frequency (in Hz)
    wave_amplitude = 1          # Arbitrary units (normalized amplitude)
    wave_duration = 1.16        # Duration of sound file (in seconds)
    wave_sample_rate = 44100    # Audio Sample Rate (in Hz)

    # Give visual representation
    time, wave = generate_sine_wave(wave_frequency, wave_amplitude, wave_duration, wave_sample_rate)
    plot_sine_wave(time, wave)
