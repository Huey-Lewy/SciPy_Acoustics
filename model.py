"""
All data models (e.g., audio processing and RT60 calculations)
Authors:
    - Zackariah A.
"""

import os
import matplotlib.pyplot as plt
from pydub import AudioSegment
import numpy as np
from scipy.io import wavfile

"""Check if the file format is WAV or MP3."""
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


'''Calculate RT60.'''
target_frequency = 250
def set_target_frequency(cycle):
    global target_frequency
    if cycle == 1:
        target_frequency = 250
    elif cycle == 2:
        target_frequency = 1000
    elif cycle == 3:
        target_frequency = 1750

def find_target_frequency(freqs):
    for x in freqs:
        if x > target_frequency:
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
    
    set_target_frequency(input_cycle)
    index_of_frequency = np.where(freqs == target_frequency)[0][0]
    data_for_frequency = spectrum[index_of_frequency]
    db_data_fun = 10 * np.log10(data_for_frequency)
    return db_data_fun

def find_nearest_value(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


