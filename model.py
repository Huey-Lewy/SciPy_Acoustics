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


"""Data Analysis and Visualization"""
def read_audio(filepath):
    """
    Read and preprocess audio data from a file.

    Parameters:
        filepath (str): Path to the audio file.

    Returns:
        tuple: Sample rate and audio data as a NumPy array.
    """
    sample_rate, data = wavfile.read(filepath)

    # Ensure data is mono (redundancy check removed)
    data = data.astype(np.float32) / np.max(np.abs(data))   # Normalize data
    return sample_rate, data

def plot_intensity(filepath, output_dir):
    """Generate and save an Intensity Graph (Spectrogram)."""

    # return plot_path

def plot_waveform(filepath, output_dir):
    """Generate and save a Waveform Graph."""

    # return plot_path

def plot_individual_rt60(filepath, output_dir, freq_ranges):
    """Generate RT60 graphs for Low, Medium, and High Frequencies."""

    # return plot_paths

def plot_combined_rt60(filepath, output_dir, freq_ranges):
    """Generate a combined RT60 graph for low, Medium, and High Frequencies."""

    # return plot_path
