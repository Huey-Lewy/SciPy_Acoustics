"""
All controller logic (e.g., file and plot handling)
Authors:
    - Zackariah A.
"""

import os

import numpy as np

from model import (
    check_file_format,
    convert_mp3_to_wav,
    ensure_single_channel,
    strip_metadata,
    get_audio_length,
    frequency_check, target_frequency, find_nearest_value
)
from scipy.io import wavfile
from matplotlib import pyplot as plt


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
        sample_rate, data = wavfile.read(filepath)
        spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024)
        db_data = frequency_check(freqs, spectrum)

        # Find max value and max value index
        max_index = np.argmax(db_data)
        max_value = db_data[max_index]

        # Slice max value array -5
        sliced_array = db_data[:max_index]
        max_minus_5_value = max_value - 5

        max_minus_5_value = find_nearest_value(sliced_array, max_minus_5_value)
        max_minus_5_index = np.where(db_data == max_minus_5_value)

        # Slice max value array -25
        max_minus_25_value = max_value - 25
        max_minus_25_value = find_nearest_value(sliced_array, max_minus_25_value)
        max_minus_25_index = np.where(db_data == max_minus_25_value)

        # Find RT20
        rt20 = (t[max_minus_5_index] - t[max_minus_25_index])[0]
        rt60 = rt20 * 3
    except ValueError as e:
        # Handle file and directory-related errors
        print(f"Error during processing: {e}")
        return None
    except Exception as e:
        # Handle unexpected exceptions (e.g., file I/O issues)
        print(f"An unexpected error occurred: {e}")
        return None


def plot_rt60(filepath):
    try:
        # Step 0: Check if file and output directory exist
        if not os.path.exists(filepath):
            raise ValueError(f"File '{filepath}' not found.")

        # Step 1: Read wav file
        sample_rate, data = wavfile.read(filepath)
        spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024)
        db_data = frequency_check(freqs, spectrum)

        plt.figure()

        plt.plot(t, db_data, linewidth=2, alpha=0.5, color='r')

        plt.xlabel('Time (s)')
        plt.ylabel('Power (dB)')

        # Find max value and max value index
        max_index = np.argmax(db_data)
        max_value = db_data[max_index]
        plt.plot(t[max_index], db_data[max_index],'go')

        # Slice max value array -5
        sliced_array = db_data[max_index:]
        max_minus_5_value = max_value - 5

        max_minus_5_value = find_nearest_value(sliced_array, max_minus_5_value)
        max_minus_5_index = np.where(db_data == max_minus_5_value)
        plt.plot(t[max_minus_5_index], db_data[max_minus_5_index],'yo')

        # Slice max value array -25
        max_minus_25_value = max_value - 25
        max_minus_25_value = find_nearest_value(sliced_array, max_minus_25_value)
        max_minus_25_index = np.where(db_data == max_minus_25_value)

        plt.plot(t[max_minus_25_index], db_data[max_minus_25_index],'ro')

        # Find RT20
        rt20 = (t[max_minus_5_index] - t[max_minus_25_index])[0]
        rt60 = rt20 * 3

        plt.grid()
        plt.show()

        print(f'The RT60 at frequency {int(target_frequency)}Hz is {round(abs(rt60), 2)} seconds')

    except ValueError as e:
        # Handle file and directory-related errors
        print(f"Error during processing: {e}")
        return None
    except Exception as e:
        # Handle unexpected exceptions (e.g., file I/O issues)
        print(f"An unexpected error occurred: {e}")
        return None
    
    
    
    
