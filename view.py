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
        self.fn_label = None            # File name label
        self.af_button = None           # Analyze File button
        self.master = root              # Main Tkinter window
        self.canvas = None              # Main canvas
        self.plot_frame = None          # Frame to display plots
        self.info = None                # Information label
        self.timestamp = None           # Timestamp for analysis session
        self.output_subdir = None       # Output subdirectory path
        self.setup_gui()                # Initialize GUI components

    def browse_files(self):
        """Opens a file dialog to select an audio file."""
        self.audiofile = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("Audio files", "*.wav *.mp3"), ("All files", "*.*"))
        )
        if self.audiofile:
            self.fn_label.config(text=f"File Opened: {os.path.basename(self.audiofile)}")
            self.af_button.place(relx=0.85, relwidth=0.15, relheight=0.5)

    def analyze_file(self):
        """Processes and analyzes the selected audio file."""
        if not self.audiofile:
            self.info.config(text="No file selected.", font=5)
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
                self.info.config(text="Error processing the file.", font=5)
                return

            # Analyze the processed file
            self.analysis_results, _ = analyze_audio(processed_file, output_dir, self.timestamp)
            if not self.analysis_results:
                self.info.config(text="Error analyzing the file.", font=5)
                return

            # Update the information label with results
            rt60_values = self.analysis_results['rt60_values']
            peak_frequency = self.analysis_results['peak_frequency']
            self.info.config(
                text=(
                    f"File Length: {file_length:.2f}s\n"
                    f"Peak Frequency: {peak_frequency:.2f} Hz\n"
                    f"RT60 Low: {rt60_values['low']:.2f}s\n"
                    f"RT60 Mid: {rt60_values['mid']:.2f}s\n"
                    f"RT60 High: {rt60_values['high']:.2f}s"
                ),
                font=5
            )

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def generate_report(self):
        """Generates a report based on the analysis results."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results available. Analyze a file first.")
            return

        try:
            # Save report in the same directory as the plots
            report_path = generate_report(self.analysis_results, self.output_subdir)
            if report_path:
                messagebox.showinfo("Success", f"Report generated at {report_path}")
            else:
                messagebox.showerror("Error", "Failed to generate report.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the report: {str(e)}")

    def display_waveform(self):
        """Displays the waveform plot in the GUI."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results available. Analyze a file first.")
            return

        plot_path = self.analysis_results['waveform_plot']
        self.show_image(plot_path)

    def display_rt60_plot(self):
        """Displays the RT60 plot in the GUI."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results available. Analyze a file first.")
            return

        plot_path = self.analysis_results['rt60_plot']
        self.show_image(plot_path)

    def display_intensity_spectrum(self):
        """Displays the intensity spectrum plot in the GUI."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results available. Analyze a file first.")
            return

        plot_path = self.analysis_results['intensity_plot']
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
            photo = tk.PhotoImage(file=plot_path)
            img_label = tk.Label(self.plot_frame, image=photo)
            img_label.image = photo  # Keep a reference
            img_label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to display the image: {str(e)}")

    def setup_gui(self):
        """Sets up the GUI layout."""
        # Canvas
        self.canvas = tk.Canvas(self.master, height=600, width=800)
        self.canvas.pack()

        # File selection frame
        file_frame = tk.Frame(self.master, bg="#D3D3D3", bd=5)
        file_frame.place(relx=0.5, rely=0.02, relwidth=0.75, relheight=0.1, anchor="n")

        # File selection button and label
        bf_button = tk.Button(file_frame, text="Select File", command=self.browse_files, font=5)
        bf_button.place(relx=0.001, relwidth=0.15, relheight=0.5)
        self.af_button = tk.Button(file_frame, text="Analyze File", command=self.analyze_file, font=5)

        self.fn_label = tk.Label(file_frame, text="File Opened: None")
        self.fn_label.place(relwidth=0.35, relheight=0.35, relx=0.2, rely=0.5)

        # Plot frame to display images
        self.plot_frame = tk.Frame(self.master, bg="white", bd=5)
        self.plot_frame.place(relx=0.5, rely=0.15, relwidth=0.75, relheight=0.5, anchor="n")

        # Control frame
        ui = tk.Frame(self.master, bg="#D3D3D3", bd=10)
        ui.place(relx=0.5, rely=0.7, relwidth=0.75, relheight=0.25, anchor="n")

        # Visualization and report buttons
        waveform_button = tk.Button(ui, text="View Waveform", font=5, command=self.display_waveform)
        rt60_button = tk.Button(ui, text="View RT60 Plot", font=5, command=self.display_rt60_plot)
        intensity_button = tk.Button(ui, text="View Intensity Spectrum", font=5, command=self.display_intensity_spectrum)
        report_button = tk.Button(ui, text="Generate Report", font=5, command=self.generate_report)

        waveform_button.place(relx=0.15, rely=0.1, relwidth=0.3, relheight=0.3)
        rt60_button.place(relx=0.55, rely=0.1, relwidth=0.3, relheight=0.3)
        intensity_button.place(relx=0.15, rely=0.5, relwidth=0.3, relheight=0.3)
        report_button.place(relx=0.55, rely=0.5, relwidth=0.3, relheight=0.3)

        self.info = tk.Label(ui, text="Select a file to begin processing.", font=5)
        self.info.place(relx=0.5, rely=0.85, anchor="n")

if __name__ == "__main__":
    master = tk.Tk()
    master.title("Audio Analysis Tool")
    app = AudioGUI(master)
    master.mainloop()
