"""
All data models (e.g., audio processing and RT60 calculations)
Authors:
    - Zackariah A.
"""

import os
from matplotlib import pyplot as plt
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




'''
CALCULATING RT60 SECTION

WIP-NOT FUNCTIONAL AS OF NOW

"""Calculate RT60."""
sample_rate, data = wavfile.read(stripped_filepath)
spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024)


def find_target_frequency(freqs):
    for x in freqs:
        if x > 1000:
            break
    return x

def frequency_check():
    global target_frequency
    target_frequency = find_target_frequency(freqs)
    index_of_frequency = np.where(freqs == target_frequency)[0][0]
    data_for_frequency = spectrum[index_of_frequency]
    db_data_fun = 10 * np.log10(data_for_frequency)
    return db_data_fun
db_data = frequency_check()

# Find max value and max value index
max_index = np.argmax(db_data)
max_value = db_data[max_index]

# Slice max value array -5
sliced_array = db_data[:max_index]
max_minus_5_value = max_value - 5

def find_nearest_value(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

max_minus_5_value = find_nearest_value(sliced_array, max_minus_5_value)
max_minus_5_index = np.where(db_data == max_minus_5_value)

# Slice max value array -25
max_minus_25_value = max_value - 25
max_minus_25_value = find_nearest_value(sliced_array, max_minus_25_value)
max_minus_25_index = np.where(db_data == max_minus_25_value)

# Find RT20
rt20 = max_minus_5_index[0]-max_minus_25_index[0]
rt60 = rt20 * 3

print(f'The RT60 at frequency {int(target_frequency)}Hz is {round(abs(rt60), 2)} seconds')


'''