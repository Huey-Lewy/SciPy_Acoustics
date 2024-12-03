"""
All controller logic (e.g., file and plot handling)
Authors:
    - Zackariah A.
    - Aidan H.
"""

import os
import numpy as np
from model import (check_file_format, convert_mp3_to_wav, ensure_single_channel, strip_metadata, get_audio_length,
                   read_audio, calculate_rt60,
                   plot_intensity, plot_waveform, plot_individual_rt60, plot_combined_rt60)

"""Data Cleaning & Processing"""
def process_audio_file(filepath, output_subdir):
    """
    Process an audio file by:
        1. Checking file format.
        2. Converting MP3 to WAV if necessary.
        3. Converting multi-channel WAV to single-channel.
        4. Stripping metadata.
        5. Calculating the audio duration.

    Returns:
        tuple: Processed file path and audio duration in seconds, or None on error.
    """
    try:
        # Step 0: Check if file and output directory exist
        if not os.path.exists(filepath):
            raise ValueError(f"File '{filepath}' not found.")

        # Ensure the output subdirectory exists
        os.makedirs(output_subdir, exist_ok=True)

        # Step 1: Check file format and get extension
        file_extension = check_file_format(filepath)
        print(f"Step 1: File format '{file_extension}' is valid.")

        # Step 2: Convert MP3 to WAV if needed
        if file_extension == '.mp3':
            filepath = convert_mp3_to_wav(filepath, output_subdir)
            print("Step 2: MP3 converted to WAV.")

        # Step 3: Ensure single-channel audio
        filepath = ensure_single_channel(filepath)
        print("Step 3: Multi-channel audio converted to single-channel.")

        # Step 4: Strip metadata
        processed_filepath = os.path.join(output_subdir, os.path.basename(filepath))
        filepath = strip_metadata(filepath)
        os.rename(filepath, processed_filepath)  # Save the processed file in the output directory
        print(f"Step 4: Metadata stripped. Processed file saved as {processed_filepath}.")

        # Step 5: Get audio length
        audio_length = get_audio_length(processed_filepath)
        print(f"Step 5: Audio length calculated: {audio_length:.2f} seconds.")

        # Indicate successful processing
        return processed_filepath, audio_length

    except ValueError as e:
        print(f"Error during processing: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None


"""Data Analysis and Calculations"""
def analyze_audio(filepath, output_dir, timestamp):
    """
    Perform full analysis on the audio file.

    Parameters:
        filepath (str): Path to the processed WAV audio file.
        output_dir (str): Directory to save plots and results.
        timestamp (str): Timestamp to uniquely name the output directory.

    Returns:
        dict: Analysis results including RT60 values and peak frequency.
    """
    try:
        # Read the audio data
        sample_rate, data = read_audio(filepath)

        # Define frequency ranges for low, mid, and high frequencies (in Hz)
        freq_ranges = {
            'low': (20, 250),
            'mid': (250, 2000),
            'high': (2000, 20000)
        }

        # Calculate RT60 values for each frequency range
        rt60_values = {}
        for label, freq_range in freq_ranges.items():
            rt60 = calculate_rt60(data, sample_rate, freq_range)
            rt60_values[label] = rt60

        # Find the frequency with the greatest amplitude
        # Compute the Fourier Transform of the audio signal
        fft_data = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(len(data), d=1/sample_rate)

        # Use only the positive frequencies
        positive_freqs = fft_freq[:len(fft_freq)//2]
        positive_fft_data = np.abs(fft_data[:len(fft_data)//2])

        # Find the peak frequency
        peak_idx = np.argmax(positive_fft_data)
        peak_frequency = positive_freqs[peak_idx]

        # Prepare the analysis results
        results = {
            'rt60_values': rt60_values,
            'peak_frequency': peak_frequency
        }

        return results

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        raise  # Propagate exception

"""Data Visualization"""
def generate_plots(filepath, output_dir, freq_ranges):
    """
    Generate all required plots and save them.

    Parameters:
        filepath (str): Path to the audio file.
        output_dir (str): Directory to save the plots.
        freq_ranges (list of tuples): Frequency ranges for RT60 calculations.

    Returns:
        dict: Plotted graphs ('intensity', 'waveform', 'individual_rt60', & 'combined_rt60') containing file paths.
    """
    return {
        "intensity": plot_intensity(filepath, output_dir),
        "waveform": plot_waveform(filepath, output_dir),
        "individual_rt60": plot_individual_rt60(filepath, output_dir, freq_ranges),
        "combined_rt60": plot_combined_rt60(filepath, output_dir, freq_ranges),
    }
