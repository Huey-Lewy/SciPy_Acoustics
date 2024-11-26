"""
All controller logic (e.g., file and plot handling)
Authors:
    - Zackariah A.
"""

import os
from model import (
    check_file_format,
    convert_mp3_to_wav,
    ensure_single_channel,
    strip_metadata,
    get_audio_length
)


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
