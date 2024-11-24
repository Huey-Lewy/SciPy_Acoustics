import os #Only used to remove file path from file name when printed on GUI
import tkinter as tk
from tkinter import filedialog #Used to allow file exploration
from mutagen.wave import WAVE #Used to print MP3 length

def browseFiles():
    global audiofile
    audiofile = filedialog.askopenfilename(initialdir = "/",title = "Select a File",filetypes=(("WAVE files", "*.wav"), ("MP3 files", "*.mp3"),("all files","*.*")))
    fn_label.configure(text="File Opened: " + os.path.basename(audiofile))
    af_button.place(relx=0.85, relwidth=0.15, relheight=0.5)
def analyzeFile():
    audio = WAVE(audiofile)
    file_length = int(audio.info.length)
    info.configure(text="File Length: "+ str(file_length) +"s\nResonant Frequency: __Hz\nDifference: _._s", font=5)
    af_button.place_forget()


#Browser
root = tk.Tk()

#Forms the canvas for everything to be held in
canvas = tk.Canvas(root, height=900, width = 1000)
canvas.pack()

#Forms the frame that hold text
file_frame = tk.Frame(root,bg="#D3D3D3",bd=5)
file_frame.place(relx=0.5, rely=0.04, relwidth=0.75, relheight=0.1, anchor="n")
#Browse File button & Analyze File
bf_button = tk.Button(file_frame, text = "Select File", command = browseFiles, font = 5)
bf_button.place(relx=0.001, relwidth=0.15, relheight=0.5)
af_button = tk.Button(file_frame, text = "Analyze File", command = analyzeFile, font = 5)

#File Name
fn_label = tk.Label(file_frame, text="File Opened: None")
fn_label.place(relwidth=0.35,relheight=0.35, relx = 0.35, rely = 0.5)

#Forms the top frame where the Graph is held
graph = tk.Frame(canvas, bg="light blue", bd = 5)
graph.place(relx=0.5, rely=0.15, relwidth=0.75, relheight=0.5, anchor="n")

#Forms the bottom frame for the information and buttons
UI = tk.Frame(canvas,bg = "#D3D3D3",bd = 10)
UI.place(relx=0.5, rely=0.67, relwidth=0.75, relheight=0.3, anchor="n")

Intensity_button = tk.Button(UI, text = "Intensity Graph", font = 5)
Waveform_button = tk.Button(UI, text = "Waveform Graph", font = 5)
CycleRT60_button = tk.Button(UI, text = "Cycle RT60 Graphs", font = 5)
Combine_button = tk.Button(UI, text = "Combine RT60 Graphs", font = 5)

Intensity_button.place(relx=0.2, rely=0.01, relwidth=0.3, relheight=0.15, anchor="n")
Waveform_button.place(relx=0.6, rely=0.01, relwidth=0.3, relheight=0.15, anchor="n")
CycleRT60_button.place(relx=0.2, rely=0.33, relwidth=0.3, relheight=0.15, anchor="n")
Combine_button.place(relx=0.6, rely=0.33, relwidth=0.3, relheight=0.15, anchor="n")



info = tk.Label(UI, text = "File Length: 0s\nResonant Frequency: __Hz\nDifference: _._s",font = 5)
info.place(relx=0.5, rely=0.5, relwidth=0.75, relheight=0.5, anchor="n")




root.mainloop()