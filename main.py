"""
Main Application Entry Point
This module initializes and runs the main application for the SciPy Acoustics project.
Authors:
    - Zackariah A.
    - Joseph E.
    - Aidan H.
    - Steven R.
"""

import tkinter as tk
from view import AudioGUI  # Import the GUI class

def main():
    """
    Initializes and starts the GUI application.
    """
    master = tk.Tk()  # Create the main Tkinter window
    master.title("SciPy Acoustics Project")  # Set the window title
    app = AudioGUI(master)  # Instantiate the GUI class
    master.mainloop()  # Run the main GUI loop

if __name__ == "__main__":
    main()
