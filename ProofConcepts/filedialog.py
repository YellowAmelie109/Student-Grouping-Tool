from tkinter import Tk
from tkinter import filedialog

#include excel files???
root = Tk()
root.withdraw()  # Hide the root window, not needed if GUI is already open
filename = filedialog.askopenfile(filetypes=[("Text and CSV files",".txt .csv")]) # show an "Open" dialog box and return the path to the selected file
#Validation to ensure the file is opened correctly
if filename is None:
    print("No file selected.")
else:
    print("File selected:", filename.name)
    # You can read from the file if needed
    # For example, to read the first line:
    print(filename.readline())