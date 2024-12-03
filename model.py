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
import matplotlib.pyplot as plt

# Global parameters
FIGURE_SIZE = (10, 6)   # Figure Size

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


"""Data Analysis and Calculations"""
def read_audio(filepath):
    """
    Read and preprocess audio data from a file.

    Parameters:
        filepath (str): Path to the audio file.

    Returns:
        tuple: Sample rate and audio data as a NumPy array.
    """
    sample_rate, data = wavfile.read(filepath)
    # Normalize audio data
    data = data.astype(np.float32) / np.max(np.abs(data))
    return sample_rate, data

def filter_and_calculate_energy(data, sample_rate, freq_range):
    """
    Apply a bandpass filter and calculate energy in dB for the specified frequency range.

    Parameters:
        data (np.ndarray): Audio data.
        sample_rate (int): Sampling rate of the audio.
        freq_range (tuple): Low and high cutoff frequencies (Hz).

    Returns:
        np.ndarray: Energy in dB for the filtered audio.
    """
    # Normalize frequency range using the Nyquist frequency
    nyquist = 0.5 * sample_rate
    low = freq_range[0] / nyquist
    high = freq_range[1] / nyquist

    # Create a second-order bandpass filter
    b, a = butter(2, [low, high], btype='band')

    # Apply the bandpass filter to the audio data
    filtered_data = lfilter(b, a, data)

    # Compute energy as the square of the filtered signal
    energy = filtered_data ** 2

    # Convert energy to decibels (logarithmic scale)
    energy_db = 10 * np.log10(energy + 1e-10)  # Add small value to avoid log(0)

    return energy_db

def calculate_rt60(data, sample_rate, freq_range):
    """
    Calculate the RT60 reverberation time for a given frequency range.

    Parameters:
        data (np.ndarray): Audio data (1D array).
        sample_rate (int): Sampling rate of the audio.
        freq_range (tuple): Low and high cutoff frequencies (Hz) as a tuple.

    Returns:
        float: Estimated RT60 value in seconds.
    """
    # Get energy in dB for the specified frequency range
    energy_db = filter_and_calculate_energy(data, sample_rate, freq_range)

    # Find the peak energy level and its index
    max_db = np.max(energy_db)
    max_idx = np.argmax(energy_db)

    # Calculate thresholds for -5dB and -25dB below the peak
    threshold_5db = max_db - 5
    threshold_25db = max_db - 25

    # Locate the time indices where the energy falls below each threshold
    idx_5db = np.where(energy_db[max_idx:] < threshold_5db)[0][0] + max_idx
    idx_25db = np.where(energy_db[max_idx:] < threshold_25db)[0][0] + max_idx

    # Compute RT20 as the time difference between the two points
    time_5db = idx_5db / sample_rate
    time_25db = idx_25db / sample_rate
    rt20 = time_25db - time_5db

    # Scale RT20 to RT60 (standard approximation)
    return rt20 * 3

def process_frequency_range(data, sample_rate, freq_range):
    """
    Filter the data for the given frequency range and calculate energy in dB over time.

    Parameters:
        data (np.ndarray): Audio data.
        sample_rate (int): Sampling rate of the audio.
        freq_range (tuple): Low and high cutoff frequencies (Hz).

    Returns:
        tuple: Time array (np.ndarray) and energy in dB (np.ndarray).
    """
    # Get energy in dB for the specified frequency range
    energy_db = filter_and_calculate_energy(data, sample_rate, freq_range)

    # Create a time axis for the energy data
    n_samples = len(energy_db)
    duration = n_samples / sample_rate
    time = np.linspace(0, duration, n_samples)

    return time, energy_db

"""Data Visualization"""
def plot_intensity(filepath, output_dir):
    """Generate and save an Intensity Graph (Spectrogram)."""
    sample_rate, data = read_audio(filepath)

    plt.figure(figsize=FIGURE_SIZE)
    plt.specgram(data, Fs=sample_rate, NFFT=1024, noverlap=512, cmap='viridis')
    plt.colorbar(label='Intensity (dB)')
    plt.title('Frequency Graph')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency (Hz)')

    plot_path = os.path.join(output_dir, "intensity_graph.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path

def plot_waveform(filepath, output_dir):
    """Generate and save a Waveform Graph."""
    sample_rate, data = read_audio(filepath)
    time = np.linspace(0, len(data) / sample_rate, num=len(data))

    plt.figure(figsize=FIGURE_SIZE)
    plt.plot(time, data, linewidth=1)
    plt.title('Waveform Graph')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')

    plot_path = os.path.join(output_dir, "waveform_graph.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path

def plot_individual_rt60(filepath, output_dir, freq_ranges):
    """Generate Individual RT60 graphs for Low, Medium, and High Frequencies."""
    sample_rate, data = read_audio(filepath)
    plot_paths = {}
    labels = ['Low', 'Medium', 'High']

    for freq_range, label in zip(freq_ranges, labels):
        time, energy_db = process_frequency_range(data, sample_rate, freq_range)

        plt.figure(figsize=FIGURE_SIZE)
        plt.plot(time, energy_db, linewidth=1)
        plt.title(f'{label} RT60 Graph')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Power (dB)')

        plot_path = os.path.join(output_dir, f"{label.lower()}_rt60_graph.png")
        plt.savefig(plot_path)
        plt.close()
        plot_paths[label.lower()] = plot_path

    return plot_paths

def plot_combined_rt60(filepath, output_dir, freq_ranges):
    """Generate Combined RT60 graphs for Low, Medium, and High Frequencies."""
    sample_rate, data = read_audio(filepath)
    labels = ['Low', 'Medium', 'High']
    colors = ['blue', 'green', 'red']

    plt.figure(figsize=FIGURE_SIZE)

    for freq_range, label, color in zip(freq_ranges, labels, colors):
        time, energy_db = process_frequency_range(data, sample_rate, freq_range)

        plt.plot(time, energy_db, label=f'{label} Frequency', linewidth=1, color=color)

    plt.title('Combined RT60 Graph')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Power (dB)')
    plt.legend()

    plot_path = os.path.join(output_dir, "combined_rt60_graph.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path
