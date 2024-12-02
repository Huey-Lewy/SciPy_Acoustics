"""
All controller logic (e.g., file and plot handling)
Authors:
    - Zackariah A.
    - Aidan H.
"""

import os
from model import (
    check_file_format, convert_mp3_to_wav, ensure_single_channel, strip_metadata, get_audio_length,
    calculate_rt60_frequency_ranges, get_frequency_with_greatest_amplitude,
    plot_waveform, plot_rt60_values, plot_intensity_spectrum
)

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

        # Step 1: Calculate RT60 values for low, mid, and high-frequency ranges
        rt60_values = calculate_rt60_frequency_ranges(filepath)
        results['rt60_values'] = rt60_values
        print("Step 1: RT60 values calculated.")

        # Step 2: Identify frequency with the greatest amplitude
        peak_frequency = get_frequency_with_greatest_amplitude(filepath)
        results['peak_frequency'] = peak_frequency
        print(f"Step 2: Peak frequency identified at {peak_frequency:.2f} Hz.")

        # Step 3: Generate waveform plot
        waveform_plot = plot_waveform(filepath, output_subdir)
        results['waveform_plot'] = waveform_plot
        print(f"Step 3: Waveform plot saved at {waveform_plot}.")

        # Step 4: Generate RT60 values plot
        rt60_plot = plot_rt60_values(rt60_values, output_subdir)
        results['rt60_plot'] = rt60_plot
        print(f"Step 4: RT60 plot saved at {rt60_plot}.")

        # Step 5: Generate intensity spectrum plot
        intensity_plot = plot_intensity_spectrum(filepath, output_subdir)
        results['intensity_plot'] = intensity_plot
        print(f"Step 5: Intensity spectrum plot saved at {intensity_plot}.")

        return results, output_subdir

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return None, None

"""Generate Report & Output"""
def generate_report(results, output_subdir):
    """
    Generate a text report summarizing the analysis results.

    Parameters:
        results (dict): Analysis results from `analyze_audio`.
        output_subdir (str): Directory to save the report.

    Returns:
        str: Path to the saved report file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(output_subdir, exist_ok=True)

        # Path for the report
        report_path = os.path.join(output_subdir, "analysis_report.txt")

        # Write report content
        with open(report_path, 'w') as report:
            # Write RT60 values
            rt60_values = results.get('rt60_values', {})
            report.write("RT60 Values (seconds):\n")
            for freq_range, value in rt60_values.items():
                report.write(f"  {freq_range.capitalize()}: {value:.2f}s\n")

            # Write peak frequency
            peak_frequency = results.get('peak_frequency', None)
            report.write(f"\nPeak Frequency: {peak_frequency:.2f} Hz\n" if peak_frequency else "\nPeak Frequency: N/A\n")

            # Write paths to plots
            report.write("\nPlots:\n")
            report.write(f"  Waveform: {results.get('waveform_plot', 'N/A')}\n")
            report.write(f"  RT60 Plot: {results.get('rt60_plot', 'N/A')}\n")
            report.write(f"  Intensity Spectrum: {results.get('intensity_plot', 'N/A')}\n")

        print(f"Report generated at {report_path}.")
        return report_path

    except Exception as e:
        print(f"Failed to generate report: {e}")
        return None
