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

def calculate_rt60(data, sample_rate, freq_range, decay_points=None):
    """
    Robust RT60 calculation with multiple decay range options.

    Args:
        data (np.ndarray): Audio data
        sample_rate (int): Audio sampling rate
        freq_range (tuple): Target frequency range
        decay_points (tuple, optional): Custom decay start and end points in dB

    Returns:
        float: Estimated RT60 value
    """
    if decay_points is None:
        decay_points = (-5, -25)  # Default to -5dB and -25dB

    time, energy_db = process_frequency_range(data, sample_rate, freq_range)

    # Find the peak energy level and corresponding index
    max_db = np.max(energy_db)
    max_idx = np.argmax(energy_db)

    # Calculate decay thresholds
    start_threshold = max_db + decay_points[0]
    end_threshold = max_db + decay_points[1]

    # Locate time indices for the thresholds
    start_idx = np.where(energy_db[max_idx:] < start_threshold)[0][0] + max_idx
    end_idx = np.where(energy_db[max_idx:] < end_threshold)[0][0] + max_idx

    # Convert indices to times
    t_start = start_idx / sample_rate
    t_end = end_idx / sample_rate

    # Calculate RT60 from RT20 (standard approximation)
    rt20 = t_end - t_start
    rt60 = rt20 * 3

    return rt60

def calculate_rt60_difference(filepath):
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
        rt20 = (t[max_minus_5_index[0]] - t[max_minus_25_index[0]])  # Access first element of the index array
        rt60 = rt20 * 3
        return round(abs(rt60), 3)-0.5

    except ValueError as e:
        # Handle file and directory-related errors
        print(f"Error during processing: {e}")
        return None
    except Exception as e:
        # Handle unexpected exceptions (e.g., file I/O issues)
        print(f"An unexpected error occurred: {e}")
        return None

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
    """Generate Individual RT60 graphs for Low, Medium, and High Frequencies with consistent y-axis range."""
    sample_rate, data = read_audio(filepath)
    plot_paths = {}
    labels = ['Low', 'Mid', 'High']
    colors = ['blue', 'green', 'red']  # Specify colors for each range
    all_energy_db = []

    # Step 1: Calculate energy_db for all frequency ranges to determine global min and max
    for freq_range in freq_ranges:
        _, energy_db = process_frequency_range(data, sample_rate, freq_range)
        all_energy_db.extend(energy_db)  # Collect all energy values

    global_min = min(all_energy_db) - 2
    global_max = max(all_energy_db) + 2

    # Step 2: Generate plots with consistent y-axis range
    for freq_range, label, color in zip(freq_ranges, labels, colors):
        time, energy_db = process_frequency_range(data, sample_rate, freq_range)

        plt.figure(figsize=FIGURE_SIZE)
        plt.plot(time, energy_db, linewidth=1, color=color, label=f'{label} Frequency')  # Add label for legend
        plt.title(f'{label} RT60 Graph')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Power (dB)')

        # Set consistent y-axis limits
        plt.ylim(global_min, global_max)

        # Add legend
        plt.legend(loc='best')  # Automatically place the legend in the best position

        plot_path = os.path.join(output_dir, f"{label.lower()}_rt60_graph.png")
        plt.savefig(plot_path)
        plt.close()
        plot_paths[label.lower()] = plot_path

    return plot_paths

def plot_combined_rt60(filepath, output_dir, freq_ranges):
    """Generate Combined RT60 graphs for Low, Medium, and High Frequencies with consistent y-axis range."""
    sample_rate, data = read_audio(filepath)
    labels = ['Low', 'Mid', 'High']
    colors = ['blue', 'green', 'red']
    all_energy_db = []

    # Step 1: Calculate energy_db for all frequency ranges to determine global min and max
    for freq_range in freq_ranges:
        _, energy_db = process_frequency_range(data, sample_rate, freq_range)
        all_energy_db.extend(energy_db)  # Collect all energy values

    global_min = min(all_energy_db) - 2
    global_max = max(all_energy_db) + 2

    # Step 2: Plot all frequency ranges with consistent y-axis limits
    plt.figure(figsize=FIGURE_SIZE)

    for freq_range, label, color in zip(freq_ranges, labels, colors):
        time, energy_db = process_frequency_range(data, sample_rate, freq_range)
        plt.plot(time, energy_db, label=f'{label} Frequency', linewidth=1, color=color)

    plt.title('Combined RT60 Graph')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Power (dB)')
    plt.ylim(global_min, global_max)  # Set consistent y-axis limits
    plt.legend()

    plot_path = os.path.join(output_dir, "combined_rt60_graph.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path
