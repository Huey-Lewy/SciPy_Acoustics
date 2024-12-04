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
from controller import process_audio_file, analyze_audio

class AudioGUI:
    def __init__(self, root):
        self.audiofile = None           # Selected audio file path
        self.analysis_results = None    # Analysis results dictionary
        self.plot_paths = None          # Paths to generated plots
        self.canvas = None      # Placeholder for GUI Canvases
        self.af_button = None   # Placeholder for GUI Buttons
        self.fn_label = None    # Placeholder for GUI Labels
        self.plot_frame = None  # Placeholder for GUI Frames
        self.info = None        # Placeholder for GUI Info
        self.current_rt60_plot = 0      # Index to cycle through RT60 plots
        self.freq_labels = ['low', 'mid', 'high']  # Labels for RT60 plots
        self.button_font = ("Arial Bold", 12)      # Global font for buttons
        self.master = root                           # Main Tkinter window
        self.setup_gui()                             # Initialize GUI components

    def browse_files(self):
        """Open a file dialog to select an audio file."""
        self.audiofile = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*"))
        )
        if self.audiofile:
            self.fn_label.config(text=f"File Opened: {os.path.basename(self.audiofile)}")

    def analyze_file(self):
        """Process and analyze the selected file."""
        if not self.audiofile:
            messagebox.showerror("Error", "No file selected. Please select a file to analyze.")
            return

        try:
            # Define output directory
            output_dir = "data/outputs"
            os.makedirs(output_dir, exist_ok=True)

            # Generate a timestamp for this analysis session
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_subdir = os.path.join(output_dir, timestamp)
            os.makedirs(output_subdir, exist_ok=True)

            # Process the audio file
            processed_file, duration = process_audio_file(self.audiofile, output_subdir)
            if not processed_file:
                messagebox.showerror("Error", "File processing failed.")
                return

            # Analyze the processed file
            self.analysis_results = analyze_audio(processed_file, output_subdir, timestamp)

            # Retrieve plots from the results
            self.plot_paths = self.analysis_results.get('plots', {})

            # Display analysis results
            rt60 = self.analysis_results['rt60_values']
            peak_freq = self.analysis_results['peak_frequency']
            self.info.config(
                text=(
                    f"Duration: {duration:.3f} s\n"
                    f"RT60 Low: {rt60['low']:.3f} s\n"
                    f"RT60 Mid: {rt60['mid']:.3f} s\n"
                    f"RT60 High: {rt60['high']:.3f} s\n"
                    f"Peak Freq: {peak_freq:.3f} Hz"
                )
            )

            messagebox.showinfo("Success", "Analysis complete. You can now view the graphs.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_intensity_graph(self):
        """Displays the intensity (spectrogram) graph."""
        if not self.plot_paths:
            messagebox.showinfo("Info", "No plots available. Analyze a file first.")
            return
        plot_path = self.plot_paths['intensity']
        self.show_image(plot_path)

    def display_waveform_graph(self):
        """Displays the waveform graph."""
        if not self.plot_paths:
            messagebox.showinfo("Info", "No plots available. Analyze a file first.")
            return
        plot_path = self.plot_paths['waveform']
        self.show_image(plot_path)

    def display_cycle_rt60_graphs(self):
        """Cycles through low, mid, and high RT60 graphs."""
        if not self.plot_paths:
            messagebox.showinfo("Info", "No plots available. Analyze a file first.")
            return

        label = self.freq_labels[self.current_rt60_plot]
        plot_path = self.plot_paths['individual_rt60'][label]
        self.show_image(plot_path)

        # Update for next cycle
        self.current_rt60_plot = (self.current_rt60_plot + 1) % len(self.freq_labels)

    def display_combined_rt60_graphs(self):
        """Displays the combined RT60 graph."""
        if not self.plot_paths:
            messagebox.showinfo("Info", "No plots available. Analyze a file first.")
            return
        plot_path = self.plot_paths['combined_rt60']
        self.show_image(plot_path)

    def show_image(self, plot_path):
        """Displays an image in the GUI."""
        if not os.path.exists(plot_path):
            messagebox.showerror("Error", f"Plot file not found at {plot_path}")
            return

        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        try:
            # Load the image
            photo = tk.PhotoImage(file=plot_path)

            # Create the label to hold the image
            img_label = tk.Label(self.plot_frame, image=photo, bg="white")
            img_label.image = photo  # Keep a reference to avoid garbage collection

            # Use place to center the image in the frame
            img_label.place(relx=0.53, rely=0.47, anchor="center")

        except Exception as e:
            messagebox.showerror("Error", f"Unable to display the image: {str(e)}")

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
        self.fn_label = tk.Label(file_frame, text="File Opened: None", anchor="w", bg="#F5F5F5",
                                 font=self.button_font, wraplength=400)
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
        combined_rt60_button = tk.Button(ui, text="Combined RT60 Graph", font=self.button_font,
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
