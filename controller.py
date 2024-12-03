"""
All controller logic (e.g., file and plot handling)
Authors:
    - Zackariah A.
    - Aidan H.
"""

import os
from model import (check_file_format, convert_mp3_to_wav, ensure_single_channel, strip_metadata, get_audio_length,
                   read_audio, plot_intensity, plot_waveform, plot_individual_rt60, plot_combined_rt60)

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

"""Data Analysis and Visualization"""
def analyze_audio(filepath, output_dir, timestamp):
    """
    Perform full analysis on the audio file.

    Parameters:
        filepath (str): Path to the processed WAV audio file.
        output_dir (str): Directory to save plots and results.
        timestamp (str): Timestamp to uniquely name the output directory.

    Returns:
        dict: Analysis results including RT60 values, peak frequency, and plot paths.
    """
    results = {}

    try:
        # Use the provided timestamp to create the subdirectory
        output_subdir = os.path.join(output_dir, timestamp)
        os.makedirs(output_subdir, exist_ok=True)

        # Step 1: Identify frequency with the greatest amplitude
        #   print(f"Step 1: Peak frequency identified at {peak_frequency:.2f} Hz.")

        # Step 2: Calculate RT60 values for low, mid, and high-frequency ranges
        #   print("Step 2: RT60 values calculated.")

        # Step 3: Generate Intensity Graph
        #   print(f"Step 3: Intensity Graph saved at {intensity_graph}.")

        # Step 4: Generate Waveform Graph
        #   print(f"Step 4: Waveform Graph saved at {waveform_graph}.")

        # Step 5: Generate Individual RT60 Graphs (Low, Medium, High)
        #   print(f"Step 5: Individual RT60 Graphs saved at {rt60_graphs}.")

        # Step 6: Generate Combined RT60 Graphs (Low, Medium, High)
        #   print(f"Step 5: Combined RT60 Graphs saved at {rt60_graph}.")

        # return results, output_subdir

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return None, None
