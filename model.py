"""
All data models (e.g., audio processing and RT60 calculations)
Authors:
    - Zackariah A.
    - Aidan H.
"""

import os
from pydub import AudioSegment
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from scipy import fftpack
import matplotlib.pyplot as plt


"""Data Cleaning & Processing"""
def check_file_format(filepath):
    # Define allowed file formats for processing
    allowed_formats = ('.wav', '.mp3')
    # Extract file extension and convert it to lowercase for comparison
    file_extension = os.path.splitext(filepath)[1].lower()

    # Check if the file extension is valid
    if file_extension in allowed_formats:
        # Return the valid file extension for further processing
        return file_extension
    else:
        # Raise an error if the file format is unsupported
        raise ValueError(f"Unsupported file format '{file_extension}'. Please use WAV or MP3 files.")

def convert_mp3_to_wav(mp3_filepath, output_dir):
    # Load the MP3 file using pydub
    audio = AudioSegment.from_mp3(mp3_filepath)

    # Create the output path for the WAV file
    wav_filepath = os.path.join(output_dir, os.path.splitext(os.path.basename(mp3_filepath))[0] + ".wav")

    # Export the MP3 content as a WAV file
    audio.export(wav_filepath, format="wav")

    # Return the path to the converted WAV file
    return wav_filepath

def ensure_single_channel(wav_filepath):
    # Load the WAV file using pydub
    audio = AudioSegment.from_wav(wav_filepath)

    # Check if the audio has more than one channel
    if audio.channels > 1:
        # Convert multi-channel audio to single-channel (mono)
        mono_audio = audio.set_channels(1)

        # Overwrite the original file with the mono version
        mono_audio.export(wav_filepath, format="wav")

    # Return the path to the single-channel WAV file
    return wav_filepath

def strip_metadata(wav_filepath):
    # Load the WAV file (with potential metadata) using pydub
    audio = AudioSegment.from_file(wav_filepath, format="wav")

    # Overwrite the original file without any metadata (tags=None)
    stripped_filepath = wav_filepath
    audio.export(stripped_filepath, format="wav", tags=None)

    # Return the path to the metadata-free WAV file
    return stripped_filepath

def get_audio_length(filepath):
    # Load the audio file using pydub
    audio = AudioSegment.from_file(filepath)

    # Get the length of the audio in milliseconds
    # Divide by 1000.0 (Float) to convert to seconds
    length_in_seconds = len(audio) / 1000.0

    # Return the audio duration in seconds
    return length_in_seconds


"""Data Analysis and Visualization"""
def calculate_rt60(audio_data, sample_rate):
    """
    Calculate the RT60 (reverberation time) using the Schroeder method.

    Parameters:
        audio_data (numpy.ndarray): Audio signal data.
        sample_rate (int): Sampling rate of the audio data.

    Returns:
        float: RT60 value in seconds, or 0.0 if insufficient decay is detected.
    """
    # Normalize audio_data to prevent overflow during squaring
    audio_data = audio_data / np.max(np.abs(audio_data))
    audio_data = audio_data.astype(np.float64)  # Ensure float64 precision

    # Square of the signal for energy
    energy = audio_data ** 2

    # Reverse cumulative sum to get the energy decay curve
    energy_rev = np.flip(energy)
    energy_decay = np.cumsum(energy_rev)
    energy_decay = np.flip(energy_decay)

    # Convert to decibels
    energy_db = 10 * np.log10(energy_decay / np.max(energy_decay) + 1e-10)  # Add epsilon to avoid log(0)

    # Find indices where the decay crosses -5 dB and -35 dB
    try:
        idx_5db = np.where(energy_db <= -5)[0][0]
        idx_35db = np.where(energy_db <= -35)[0][0]
    except IndexError:
        # If the signal doesn't decay enough, return 0.0
        return 0.0

    t_5db = idx_5db / sample_rate
    t_35db = idx_35db / sample_rate

    # Calculate RT60 using the decay time between -5 dB and -35 dB
    rt60 = (t_35db - t_5db) * 2  # Extrapolate to -60 dB

    return rt60

def bandpass_filter(audio_data, sample_rate, lowcut, highcut, order=4):
    """
    Apply a Butterworth bandpass filter to the audio data.

    Parameters:
        audio_data (numpy.ndarray): Audio signal data.
        sample_rate (int): Sampling rate.
        lowcut (float): Low frequency cutoff.
        highcut (float): High frequency cutoff.
        order (int): Order of the filter.

    Returns:
        numpy.ndarray: Filtered audio data.
    """
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist

    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, audio_data)

    return y

def calculate_rt60_frequency_ranges(filepath, freq_ranges=None):
    """
    Calculate RT60 values for specified frequency ranges.

    Parameters:
        filepath (str): Path to the WAV audio file.
        freq_ranges (dict): Optional dictionary of frequency ranges.
                            Defaults to low, mid, and high ranges.

    Returns:
        dict: RT60 values for each specified frequency range.
    """
    # Load the audio data
    try:
        sample_rate, data = wavfile.read(filepath)
    except Exception as e:
        raise IOError(f"Failed to read audio file '{filepath}': {e}")

    # Normalize data to float32 with safety checks
    epsilon = 1e-10
    max_val = np.max(np.abs(data))
    if max_val > epsilon:
        data = data.astype(np.float32) / max_val
    else:
        data = np.zeros_like(data)

    # Default frequency ranges
    if freq_ranges is None:
        freq_ranges = {
            'low': (20, 250),
            'mid': (250, 2000),
            'high': (2000, 20000)
        }

    rt60_values = {}

    for key, (lowcut, highcut) in freq_ranges.items():
        filtered_data = bandpass_filter(data, sample_rate, lowcut, highcut)
        rt60 = calculate_rt60(filtered_data, sample_rate)
        rt60_values[key] = rt60

    return rt60_values

def get_frequency_with_greatest_amplitude(filepath):
    """
    Identify the frequency with the greatest amplitude in the audio file.

    Parameters:
        filepath (str): Path to the WAV audio file.

    Returns:
        float: Frequency in Hz with the greatest amplitude.
    """
    sample_rate, data = wavfile.read(filepath)

    # If stereo, take one channel
    if len(data.shape) > 1:
        data = data[:, 0]

    # Apply FFT with windowing to reduce spectral leakage
    window = np.hanning(len(data))
    data_windowed = data * window
    yf = fftpack.fft(data_windowed)
    xf = fftpack.fftfreq(len(data), 1 / sample_rate)

    # Take only the positive frequencies
    idxs = np.where(xf >= 0)
    xf = xf[idxs]
    yf = np.abs(yf[idxs])

    # Find the frequency with the highest amplitude
    idx = np.argmax(yf)
    freq = xf[idx]

    return freq

def plot_waveform(filepath, output_dir):
    """
    Plot the waveform of the audio file and save the figure.

    Parameters:
        filepath (str): Path to the WAV audio file.
        output_dir (str): Directory to save the plot.

    Returns:
        str: Path to the saved plot image.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sample_rate, data = wavfile.read(filepath)
    times = np.arange(len(data)) / float(sample_rate)

    plt.figure(figsize=(10, 4))
    plt.plot(times, data)
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()

    plot_path = os.path.join(output_dir, 'waveform.png')
    plt.savefig(plot_path)
    plt.close()

    return plot_path

def plot_rt60_values(rt60_values, output_dir):
    """
    Plot the RT60 values for different frequency ranges.

    Parameters:
        rt60_values (dict): RT60 values with keys 'low', 'mid', 'high'.
        output_dir (str): Directory to save the plot.

    Returns:
        str: Path to the saved plot image.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frequency_ranges = list(rt60_values.keys())
    rt60_list = [rt60_values[fr] for fr in frequency_ranges]

    plt.figure(figsize=(6, 4))
    plt.bar(frequency_ranges, rt60_list, color='skyblue')
    plt.title('RT60 Values')
    plt.xlabel('Frequency Range')
    plt.ylabel('RT60 (s)')
    plt.tight_layout()

    plot_path = os.path.join(output_dir, 'rt60_values.png')
    plt.savefig(plot_path)
    plt.close()

    return plot_path

def plot_intensity_spectrum(filepath, output_dir):
    """
    Plot the intensity spectrum of the audio file.

    Parameters:
        filepath (str): Path to the WAV audio file.
        output_dir (str): Directory to save the plot.

    Returns:
        str: Path to the saved plot image.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sample_rate, data = wavfile.read(filepath)

    # Normalize data
    epsilon = 1e-10
    max_val = np.max(np.abs(data))
    if max_val > epsilon:
        data = data.astype(np.float32) / max_val
    else:
        data = np.zeros_like(data)

    num_samples = len(data)
    window = np.hanning(num_samples)
    data_windowed = data * window
    yf = fftpack.fft(data_windowed)
    xf = fftpack.fftfreq(num_samples, 1 / sample_rate)

    # Take only the positive frequencies
    idxs = np.where(xf >= 0)
    xf = xf[idxs]
    yf = np.abs(yf[idxs])

    plt.figure(figsize=(10, 4))
    plt.plot(xf, yf)
    plt.title('Intensity Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.tight_layout()

    plot_path = os.path.join(output_dir, 'intensity_spectrum.png')
    plt.savefig(plot_path)
    plt.close()

    return plot_path
