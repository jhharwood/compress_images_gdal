# ****************************************************************************
#
# NAME: J. Heath Harwood
# DATE: 11  September 2023
#
#
# DESCRIPTION:  This script compresses images using gdal and LZW compress
#               with multi-cpu support.
#
#
#
# DEPENDENCIES: arcpy, Python 3.9 Standard Library,
#
# SOURCE(S):
#   
##############################################################################

'''
Change log:
2017-March-23 J. Heath Harwood, tool is operational                        

TODO:

'''
############################### IMPORT STATMENTS ##############################

import os
import glob
import multiprocessing
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk 

################################### Classes ####################################

class ThreadJobs(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # get job from queue
            myJob = self.queue.get()
            inCmd = myJob
            os.system(inCmd)

            # signal queue job is done
            self.queue.task_done()


################################# Functions ###################################

''' def select_gdal_path():
    gdal_path = filedialog.askopenfilename(title="Select GDAL Path", filetypes=[("GDAL Executable", "*.exe")])
    gdal_path_entry.delete(0, tk.END)
    gdal_path_entry.insert(0, gdal_path) '''

def select_gdal_path():
    default_path = "C:\\GDAL\\gdaltranslate.exe"  # Replace with your default GDAL path
    gdal_path = filedialog.askopenfilename(
        title="Select GDAL Path",
        filetypes=[("GDAL Executable", "*.exe")],
        initialdir=os.path.dirname(default_path),  # Set the initial directory to the default path's directory
        initialfile=os.path.basename(default_path)  # Set the initial file to the default path's filename
    )

    if gdal_path:
        gdal_path_entry.delete(0, tk.END)
        gdal_path_entry.insert(0, gdal_path)
    else:
        # If the user cancels the file dialog, use the default path
        gdal_path_entry.delete(0, tk.END)
        gdal_path_entry.insert(0, default_path)
    
''' def select_image_folder():
    image_folder = filedialog.askdirectory(title="Select Image Folder")
    image_folder_entry.delete(0, tk.END)
    image_folder_entry.insert(0, image_folder)
 '''
''' def select_image_files():
    image_files = filedialog.askopenfilenames(
        title="Select Image Files",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tif *.tiff")],
    )

    if image_files:
        image_files_entry.delete(0, tk.END)
        image_files_entry.insert(0, ";".join(image_files)) '''

def select_image_files():
    image_files = filedialog.askopenfilenames(
        title="Select Image Files",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tif *.tiff")],
    )

    if image_files:
        # Clear the existing items in the Listbox
        image_files_listbox.delete(0, tk.END)

        # Insert the selected image files into the Listbox
        for image_file in image_files:
            image_files_listbox.insert(tk.END, image_file)

def process_tif_files():
    start = time.time()
    gdalPath = gdal_path_entry.get()
    nProc = int(cpu_scale.get())

    images = image_files_listbox.get(0, tk.END)
    print(images)
    imagePath = os.path.dirname(images[0])
    print(f'Compressing image files in {imagePath}')

    #tiffs = glob.glob(tifPath +'/*.tif')

    outTifDir = '\\'.join( [imagePath, "GDAL_lzw"] )
    if not os.path.isdir(outTifDir):
        os.makedirs(outTifDir)
    print (outTifDir)

    lzwCmd = []

    for image in images:
        print(f"Current {image} file is being processed.")
        infile = image
        outfile = outTifDir + '/'+ os.path.basename(infile)

        lzwCmdStr = f'{gdalPath} -co COMPRESS=LZW {infile} {outfile}'
        print(f'{lzwCmdStr}')
        lzwCmd.append(lzwCmdStr)

    queue = queue = queue = multiprocessing.JoinableQueue()

    def main():
        for i in range(nProc):
            t = ThreadJobs(queue)
            t.setDaemon(True)
            t.start()

        for cmd in lzwCmd:
            queue.put(cmd)

        queue.join()

    main()

    messagebox.showinfo("Complete", f'\nProcessing completed in: {((time.time() - start) / 60)} minutes')
    print(f'\nProcessing completed in: {((time.time() - start) / 60)} minutes')
    del start

# Create the main Tkinter window
root = tk.Tk()
root.title("LZW Image Compression - GDAL")

# Padding for the entire GUI
root.geometry("600x600")  # Adjust the window size as needed

# Create a frame to group widgets with padding
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

# Button to select GDAL path
gdal_path_button = tk.Button(frame, text="Select GDAL Path", command=select_gdal_path)
gdal_path_button.pack(pady=10)

# Label and Entry for GDAL Path
gdal_path_label = tk.Label(frame, text="GDAL Path:")
gdal_path_label.pack()
gdal_path_entry = tk.Entry(frame,width=75)
default_path = f"C:\GDAL\gdal_translate.exe"
gdal_path_entry.insert(0, default_path) 
gdal_path_entry.pack()

# Create a Frame to hold the Listbox and Scrollbar
listbox_frame = tk.Frame(frame)
listbox_frame.pack(pady=10)

# Create a Listbox widget for Image Files
image_files_listbox = tk.Listbox(listbox_frame, width=200, selectmode=tk.MULTIPLE)
image_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a Scrollbar for the Listbox
scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=image_files_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the Listbox to use the Scrollbar
image_files_listbox.config(yscrollcommand=scrollbar.set)

# Button to select Image Files
image_files_button = tk.Button(frame, text="Select Image Files", command=select_image_files)
image_files_button.pack(pady=10)  # Add padding between this button and the next one

''' # Entry for Image Files
image_files_label = tk.Label(frame, text="Image Files:")
image_files_label.pack()
image_files_entry = tk.Entry(frame, width=75)
image_files_entry.pack() '''

# Label and Scale for Number of CPU Cores
cpu_label = tk.Label(frame, text="Number of CPU Cores:")
cpu_label.pack()
cpu_scale = tk.Scale(frame, from_=1, to=multiprocessing.cpu_count(), orient="horizontal")
cpu_scale.pack()

# Button to start the processing
process_button = tk.Button(root, text="Compress Image Files", command=process_tif_files)
process_button.pack(pady=50)

root.mainloop()
