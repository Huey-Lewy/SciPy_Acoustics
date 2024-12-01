"""
All controller logic (e.g., file and plot handling)
Authors:
    - Zackariah A.
"""

import os
import statistics

import numpy as np
from scipy.cluster.hierarchy import average

from model import (
    check_file_format,
    convert_mp3_to_wav,
    ensure_single_channel,
    strip_metadata,
    get_audio_length,
    frequency_check, target_frequency, find_nearest_value, set_target_frequency, input_cycle, cycle_frequency_input,
    cycle_frequency_number, find_target_frequency
)
from scipy.io import wavfile
from matplotlib import pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



def process_audio_file(filepath, output_dir):
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

        # Ensure the output directory exists or attempt to create it
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)  # Create output directory if missing
                print(f"Output directory '{output_dir}' created.")
            except Exception as e:
                raise ValueError(f"Failed to create output directory '{output_dir}': {e}")

        # Step 1: Check file format and get extension
        file_extension = check_file_format(filepath)
        print(f"Step 1: File format '{file_extension}' is valid.")

        # Step 2: Convert MP3 to WAV if needed
        if file_extension == '.mp3':
            filepath = convert_mp3_to_wav(filepath, output_dir)
            print("Step 2: MP3 converted to WAV.")

        # Step 3: Ensure single-channel audio
        filepath = ensure_single_channel(filepath)
        print("Step 3: Multi-channel audio converted to single-channel.")

        # Step 4: Strip metadata
        filepath = strip_metadata(filepath)
        print("Step 4: Metadata stripped.")

        # Step 5: Get audio length
        audio_length = get_audio_length(filepath)
        print(f"Step 5: Audio length calculated: {audio_length:.2f} seconds.")

        # Indicate successful processing
        print(f"Processing complete. Processed file saved at: {filepath}")
        return filepath, audio_length

    except ValueError as e:
        # Handle file and directory-related errors
        print(f"Error during processing: {e}")
        return None
    except Exception as e:
        # Handle unexpected exceptions (e.g., file I/O issues)
        print(f"An unexpected error occurred: {e}")
        return None



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
        sliced_array = db_data[max_index:]

        max_minus_5_value = max_value - 5
        max_minus_5_value = find_nearest_value(sliced_array, max_minus_5_value)
        max_minus_5_index = np.where(db_data == max_minus_5_value)[0]

        if len(max_minus_5_index) == 0:
            raise ValueError("No values found for -5dB threshold.")

        # Slice max value array -25
        max_minus_25_value = max_value - 25
        max_minus_25_value = find_nearest_value(sliced_array, max_minus_25_value)
        max_minus_25_index = np.where(db_data == max_minus_25_value)[0]

        if len(max_minus_25_index) == 0:
            raise ValueError("No values found for -5dB threshold.")

        # Find RT20
        rt20 = (t[max_minus_5_index[0]] - t[max_minus_25_index[0]])  # Access first element of the index array
        rt60 = rt20 * 3
        return rt60

    except ValueError as e:
        print(f"Error during processing: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def plot_rt60(filepath):
    try:
        if not os.path.exists(filepath):
            raise ValueError(f"File '{filepath}' not found.")

        sample_rate, data = wavfile.read(filepath)

        spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024,cmap=plt.get_cmap('jet'))
        db_data = frequency_check(freqs, spectrum)

        plt.figure()
        plt.plot(t, db_data, linewidth=2, alpha=0.5, color='r')

        # Find max value and max value index
        max_index = np.argmax(db_data)
        max_value = db_data[max_index]
        plt.plot(t[max_index], db_data[max_index], 'go')

        # Slice max value array -5
        sliced_array = db_data[max_index:]

        max_minus_5_value = max_value - 5
        max_minus_5_value = find_nearest_value(sliced_array, max_minus_5_value)
        max_minus_5_index = np.where(db_data == max_minus_5_value)[0]

        if len(max_minus_5_index) == 0:
            raise ValueError("No values found for -5dB threshold.")

        plt.plot(t[max_minus_5_index], db_data[max_minus_5_index], 'yo')

        # Slice max value array -25
        max_minus_25_value = max_value - 25
        max_minus_25_value = find_nearest_value(sliced_array, max_minus_25_value)
        max_minus_25_index = np.where(db_data == max_minus_25_value)[0]

        if len(max_minus_25_index) == 0:
            raise ValueError("No values found for -5dB threshold.")

        plt.plot(t[max_minus_25_index], db_data[max_minus_25_index], 'ro')

        # Find RT20
        rt20 = (t[max_minus_5_index[0]] - t[max_minus_25_index[0]])  # Access first element of the index array
        rt60 = rt20 * 3

        plt.grid()
        plt.show()


        print(f'The RT60 at {cycle_frequency_number()}Hz is {round(abs(rt60), 2)} seconds')

        # global average_rt60
        global rt60_difference

        r1 = calculate_rt60(filepath)
        cycle_frequency_input()
        r2 = calculate_rt60(filepath)
        cycle_frequency_input()
        r3 = calculate_rt60(filepath)
        cycle_frequency_input()
        average_rt60 = round((round(abs(r1), 2) + round(abs(r2), 2) + round(abs(r3), 2)) / 3, 2)
        print(f'Average Rt60 is: {average_rt60}')
        rt60_difference = round(average_rt60-0.5,2)
        print(f"Rt60 difference is:{rt60_difference}")
    except ValueError as e:
        print(f"Error during processing: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def call_average_rt60(filepath):
    r1 = calculate_rt60(filepath)
    cycle_frequency_input()
    r2 = calculate_rt60(filepath)
    cycle_frequency_input()
    r3 = calculate_rt60(filepath)
    cycle_frequency_input()
    average_rt60 = round((round(abs(r1), 2) + round(abs(r2), 2) + round(abs(r3), 2)) / 3, 2)
    return average_rt60
def call_rt60_difference(filepath):
    var = call_average_rt60(filepath)
    difference = round(var-0.5,2)
    return difference