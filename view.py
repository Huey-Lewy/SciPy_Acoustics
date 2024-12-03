"""
GUI components and plotting functions
Authors:
    - Joseph E.
    - Zackariah A.
    - Aidan H.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from controller import process_audio_file, analyze_audio, generate_report


class AudioGUI:
    def __init__(self, root):
        self.audiofile = None           # Selected audio file path
        self.analysis_results = None    # Analysis results dictionary
        self.timestamp = None           # Timestamp for analysis session
        self.output_subdir = None       # Output subdirectory path
        self.canvas = None      # Main canvas
        self.plot_frame = None  # Frame to display plots
        self.info = None        # Information label
        self.fn_label = None    # File name label
        self.af_button = None   # Analyze File button
        self.button_font = ("Arial Bold", 12)   # Global font for buttons
        self.master = root                      # Main Tkinter window
        self.setup_gui()                        # Initialize GUI components

    def browse_files(self):
        """Opens a file dialog to select an audio file."""
        self.audiofile = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*"))
        )
        if self.audiofile:
            self.fn_label.config(text=f"File Opened: {os.path.basename(self.audiofile)}")

    def analyze_file(self):
        """Processes and analyzes the selected audio file."""
        if not self.audiofile:
            self.info.config(text="No file selected.", font=self.button_font)
            return

        try:
            # Define output directory
            output_dir = "data/outputs"

            # Generate and store the timestamp
            import datetime
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.output_subdir = os.path.join(output_dir, self.timestamp)

            # Ensure the output subdirectory exists
            os.makedirs(self.output_subdir, exist_ok=True)

            # Process the audio file
            processed_file, file_length = process_audio_file(self.audiofile, self.output_subdir)
            if processed_file is None:
                self.info.config(text="Error processing the file.", font=self.button_font)
                return

            # Analyze the processed file
            self.analysis_results, _ = analyze_audio(processed_file, output_dir, self.timestamp)
            if not self.analysis_results:
                self.info.config(text="Error analyzing the file.", font=self.button_font)
                return

            # Update the information label with results
            rt60_values = self.analysis_results['rt60_values']
            peak_frequency = self.analysis_results['peak_frequency']
            self.info.config(text=(f"File Length: {file_length:.2f}s\n"
                                   f"Peak Freq: {peak_frequency:.2f} Hz\n"
                                   f"RT60 High: {rt60_values['high']:.2f}s\n"
                                   f"RT60 Mid: {rt60_values['mid']:.2f}s\n"
                                   f"RT60 Low: {rt60_values['low']:.2f}s"), font=self.button_font)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def display_intensity_graph(self):
        """Displays the intensity (spectrogram) graph."""
        # Placeholder: Will require updates in controller/model.py
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results available. Analyze a file first.")
            return

        # Example usage: plot_path = self.analysis_results['spectrogram_plot']
        self.show_placeholder("Intensity Graph")

    def display_waveform_graph(self):
        """Displays the waveform graph."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results available. Analyze a file first.")
            return

        plot_path = self.analysis_results['waveform_plot']
        self.show_image(plot_path)

    def display_cycle_rt60_graphs(self):
        """Cycles through low, mid, and high RT60 graphs."""
        # Placeholder: Logic to cycle through RT60 graphs
        self.show_placeholder("Cycle RT60 Graphs")

    def display_combined_rt60_graphs(self):
        """Displays the combined RT60 graph."""
        # Placeholder: Combined RT60 graph logic
        self.show_placeholder("Combined RT60 Graphs")

    def show_image(self, plot_path):
        """Displays an image in the GUI."""
        if not os.path.exists(plot_path):
            messagebox.showerror("Error", f"Plot file not found at {plot_path}")
            return

        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        try:
            photo = tk.PhotoImage(file=plot_path)
            img_label = tk.Label(self.plot_frame, image=photo)
            img_label.image = photo  # Keep a reference
            img_label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to display the image: {str(e)}")

    def show_placeholder(self, graph_name):
        """Displays a placeholder for functionality not yet implemented."""
        messagebox.showinfo("Placeholder", f"{graph_name} functionality is not yet implemented.")

    def setup_gui(self):
        """Sets up the GUI layout."""
        # Canvas
        self.canvas = tk.Canvas(self.master, height=800, width=1000)
        self.canvas.pack()

        # File selection frame
        file_frame = tk.Frame(self.master, bg="#D3D3D3", bd=5)
        file_frame.place(relx=0.5, rely=0.02, relwidth=0.75, relheight=0.1, anchor="n")

        # File selection button and label
        bf_button = tk.Button(file_frame, text="Select File", command=self.browse_files, font=self.button_font)
        bf_button.place(relx=0.01, rely=0.1, relwidth=0.2, relheight=0.8)

        self.af_button = tk.Button(file_frame, text="Analyze File", command=self.analyze_file, font=self.button_font)
        self.af_button.place(relx=0.79, rely=0.1, relwidth=0.2, relheight=0.8)

        # File name label with dynamic text shrinking
        self.fn_label = tk.Label(file_frame,text=" File Opened: None",anchor="w",bg="#F5F5F5",
                                 font=self.button_font,wraplength=400)
        self.fn_label.place(relx=0.23, rely=0.1, relwidth=0.54, relheight=0.8)

        # Plot frame to display images
        self.plot_frame = tk.Frame(self.master, bg="white", bd=5)
        self.plot_frame.place(relx=0.5, rely=0.15, relwidth=0.75, relheight=0.5, anchor="n")

        # Control frame
        ui = tk.Frame(self.master, bg="#D3D3D3", bd=10)
        ui.place(relx=0.5, rely=0.7, relwidth=0.75, relheight=0.25, anchor="n")

        # Visualization buttons
        intensity_button = tk.Button(ui, text="Intensity Graph", font=self.button_font,
                                      command=self.display_intensity_graph)
        waveform_button = tk.Button(ui, text="Waveform Graph", font=self.button_font,
                                     command=self.display_waveform_graph)
        cycle_rt60_button = tk.Button(ui, text="Cycle RT60 Graphs", font=self.button_font,
                                       command=self.display_cycle_rt60_graphs)
        combined_rt60_button = tk.Button(ui, text="Combine RT60 Graphs", font=self.button_font,
                                          command=self.display_combined_rt60_graphs)

        intensity_button.place(relx=0.03, rely=0.1, relwidth=0.27, relheight=0.35)
        waveform_button.place(relx=0.33, rely=0.1, relwidth=0.27, relheight=0.35)
        cycle_rt60_button.place(relx=0.03, rely=0.55, relwidth=0.27, relheight=0.35)
        combined_rt60_button.place(relx=0.33, rely=0.55, relwidth=0.27, relheight=0.35)

        # Information frame
        info_frame = tk.Frame(ui, bg="white", bd=2)
        info_frame.place(relx=0.65, rely=0.1, relwidth=0.32, relheight=0.8)

        # Information label
        self.info = tk.Label(info_frame, text="Select a file to begin processing.", font=self.button_font,
                             wraplength=200, justify="center", bg="white")
        self.info.place(relwidth=1, relheight=1)


if __name__ == "__main__":
    master = tk.Tk()
    master.title("Audio Analysis Tool")
    app = AudioGUI(master)
    master.mainloop()
