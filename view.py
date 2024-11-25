# GUI components and plotting functions
#   Author: Joseph E.
#   Helper: Zackariah A.

import os                       # Used to handle file paths
import tkinter as tk            # Used for the GUI interface
from tkinter import filedialog  # File dialog for browsing files
from pydub import AudioSegment  # To handle audio processing

class AudioGUI:
    def __init__(self, master):
        self.audiofile = None  # Placeholder for the selected audio file
        self.fn_label = None   # Placeholder for file name label
        self.af_button = None  # Placeholder for Analyze File button
        self.info = None       # Placeholder for Info label
        self.master = master   # Renamed from root to avoid name shadowing
        self.setup_gui()
    def browse_files(self):
        # Opens a file dialog to select an audio file
        self.audiofile = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("WAVE files", "*.wav"), ("All files", "*.*"))
        )
        if self.audiofile:
            self.fn_label.config(text=f"File Opened: {os.path.basename(self.audiofile)}")
            self.af_button.place(relx=0.85, relwidth=0.15, relheight=0.5)

    def analyze_file(self):
        if not self.audiofile:
            self.info.config(text="No file selected.", font=5)
            return

        try:
            # Load the audio file using pydub
            audio = AudioSegment.from_file(self.audiofile)
            file_length = int(len(audio) / 1000)  # Length in seconds

            # Update the information label
            self.info.config(
                text=f"File Length: {file_length}s\nResonant Frequency: __Hz\nDifference: _._s",
                font=5
            )
            self.af_button.place_forget()
        except Exception as e:
            self.info.config(text=f"Error analyzing file: {str(e)}", font=5)

    def setup_gui(self):
        # Forms the canvas for everything to be held in
        canvas = tk.Canvas(self.master, height=900, width=1000)
        canvas.pack()

        # Forms the file selection frame
        file_frame = tk.Frame(self.master, bg="#D3D3D3", bd=5)
        file_frame.place(relx=0.5, rely=0.04, relwidth=0.75, relheight=0.1, anchor="n")

        # Browse File button & Analyze File button
        bf_button = tk.Button(file_frame, text="Select File", command=self.browse_files, font=5)
        bf_button.place(relx=0.001, relwidth=0.15, relheight=0.5)
        self.af_button = tk.Button(file_frame, text="Analyze File", command=self.analyze_file, font=5)

        # File Name Label
        self.fn_label = tk.Label(file_frame, text="File Opened: None")
        self.fn_label.place(relwidth=0.35, relheight=0.35, relx=0.35, rely=0.5)

        # Graph Frame
        graph = tk.Frame(canvas, bg="light blue", bd=5)
        graph.place(relx=0.5, rely=0.15, relwidth=0.75, relheight=0.5, anchor="n")

        # Bottom Frame for Info and Buttons
        ui = tk.Frame(canvas, bg="#D3D3D3", bd=10)
        ui.place(relx=0.5, rely=0.67, relwidth=0.75, relheight=0.3, anchor="n")

        # Buttons for Graphs
        intensity_button = tk.Button(ui, text="Intensity Graph", font=5)
        waveform_button = tk.Button(ui, text="Waveform Graph", font=5)
        cycle_rt60_button = tk.Button(ui, text="Cycle RT60 Graphs", font=5)
        combine_button = tk.Button(ui, text="Combine RT60 Graphs", font=5)

        intensity_button.place(relx=0.2, rely=0.01, relwidth=0.3, relheight=0.15, anchor="n")
        waveform_button.place(relx=0.6, rely=0.01, relwidth=0.3, relheight=0.15, anchor="n")
        cycle_rt60_button.place(relx=0.2, rely=0.33, relwidth=0.3, relheight=0.15, anchor="n")
        combine_button.place(relx=0.6, rely=0.33, relwidth=0.3, relheight=0.15, anchor="n")

        # Info Label
        self.info = tk.Label(ui, text="File Length: 0s\nResonant Frequency: __Hz\nDifference: _._s", font=5)
        self.info.place(relx=0.5, rely=0.5, relwidth=0.75, relheight=0.5, anchor="n")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioGUI(root)
    root.mainloop()
