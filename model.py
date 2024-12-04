"""
All data models (e.g., audio processing and RT60 calculations)
Authors:
    - Zackariah A.
    - Aidan H.
"""

import os
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, spectrogram
from scipy.io import wavfile

# Global parameters
FIGURE_SIZE = (8, 4)   # Figure Size

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
    data = data.astype(np.float32) / np.max(np.abs(data))
    return sample_rate, data

def process_frequency_range(data, sample_rate, freq_range, epsilon=1e-10):
    """
    Enhanced frequency range processing with improved numerical stability.

    Args:
        data (np.ndarray): Input audio data
        sample_rate (int): Audio sampling rate
        freq_range (tuple): Low and high cutoff frequencies (Hz)
        epsilon (float): Small value to prevent log(0)

    Returns:
        tuple: Times and normalized energy decay in decibels
    """
    # Nyquist frequency calculation
    nyquist = 0.5 * sample_rate
    low = freq_range[0] / nyquist
    high = freq_range[1] / nyquist

    # Bandpass filter creation
    b, a = butter(2, [low, high], btype='band')
    filtered_data = lfilter(b, a, data)

    # Energy calculation
    energy = filtered_data ** 2
    energy_db = 10 * np.log10(energy + epsilon)  # Avoid log(0)

    # Create a time axis for the data
    n_samples = len(data)
    duration = n_samples / sample_rate
    time = np.linspace(0, duration, num=n_samples)

    return time, energy_db

def find_target_frequency(freqs):
    for x in freqs:
        if x > set_target_frequency(input_cycle):
            break
    return x

input_cycle = 0
def cycle_frequency_input():
    global input_cycle
    if 3 > input_cycle > 0:
        input_cycle+= 1
    else:
        input_cycle = 1

def frequency_check(freqs,spectrum):

    target_frequency = find_target_frequency(freqs)
    index_of_frequency = np.where(freqs == target_frequency)[0][0]
    data_for_frequency = spectrum[index_of_frequency]
    db_data_fun = 10 * np.log10(data_for_frequency)
    return db_data_fun

def set_target_frequency(cycle):
    global target_frequency
    if cycle == 1:
        target_frequency = 250
        return 250
    elif cycle == 2:
        target_frequency = 1000
        return 1000
    elif cycle == 3:
        target_frequency = 1750
        return 1750
    else:
        return 9



def find_nearest_value(array, value):
    idx = (np.abs(array - value)).argmin()
    return array[idx]
def calculate_rt60(filepath):
    try:
        if not os.path.exists(filepath):
            raise ValueError(f"File '{filepath}' not found.")
        sample_rate, data = wavfile.read(filepath)
        spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024, cmap=plt.get_cmap('jet'))
        db_data = frequency_check(freqs, spectrum)

        # Find max value and max value index
        max_index = np.argmax(db_data)
        max_value = db_data[max_index]

        # Slice max value array -5
        sliced_array = db_data[:max_index]
        max_minus_5_value = max_value - 5
        sliced_array = db_data[max_index:]

        max_minus_5_value = max_value - 5
        max_minus_5_value = find_nearest_value(sliced_array, max_minus_5_value)
        max_minus_5_index = np.where(db_data == max_minus_5_value)
        max_minus_5_index = np.where(db_data == max_minus_5_value)[0]
        if len(max_minus_5_index) == 0:
            raise ValueError("No values found for -5dB threshold.")

        # Slice max value array -25
        max_minus_25_value = max_value - 25
        max_minus_25_value = find_nearest_value(sliced_array, max_minus_25_value)
        max_minus_25_index = np.where(db_data == max_minus_25_value)
        max_minus_25_index = np.where(db_data == max_minus_25_value)[0]
        if len(max_minus_25_index) == 0:
            raise ValueError("No values found for -5dB threshold.")

        # Find RT20
        rt20 = (t[max_minus_5_index] - t[max_minus_25_index])[0]
        rt20 = (t[max_minus_5_index[0]] - t[max_minus_25_index[0]])  # Access first element of the index array
        rt60 = rt20 * 3
        return rt60
    except ValueError as e:
        # Handle file and directory-related errors
        print(f"Error during processing: {e}")
        return None
    except Exception as e:
        # Handle unexpected exceptions (e.g., file I/O issues)
        print(f"An unexpected error occurred: {e}")
        return None

"""Data Visualization"""
def plot_intensity(filepath, output_dir):
    """Generate and save an Intensity Graph (Spectrogram) using SciPy."""
    sample_rate, data = read_audio(filepath)

    # Compute the spectrogram using SciPy
    frequencies, times, Sxx = spectrogram(data, fs=sample_rate, nperseg=1024, noverlap=512)

    # Convert power to dB scale, avoiding log of zero by adding a small offset
    Sxx_db = 10 * np.log10(Sxx + 1e-10)

    plt.figure(figsize=FIGURE_SIZE)
    plt.pcolormesh(times, frequencies, Sxx_db, shading='gouraud', cmap='nipy_spectral')
    plt.colorbar(label='Intensity (dB)')
    plt.title('Frequency Graph (SciPy Spectrogram)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency (Hz)')

    plot_path = os.path.join(output_dir, "intensity_graph_scipy.png")
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
