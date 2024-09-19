



from tkinter import *
import tkinter as tk
from tkintermapview import TkinterMapView 
from tkinter import Label
from tkinter import filedialog
from PIL import Image, ImageTk
import os 
import shutil

main_window = Tk()

program_name = "Image Geo Navigator"

def main():

    create_main_window()



    main_window.mainloop()


# upload photos 
def upload_photo():
    file_path = filedialog.askopenfilename(filetypes= [("Image files", "*.jpg; *.jpeg; *.png")])
    if file_path:
        save_photo(file_path)

# save photos to folder called saved photos
def save_photo(file_path):
    save_folder = "saved_photos"
    os.makedirs(save_folder, exist_ok = True)

    shutil.copy(file_path, os.path.join(save_folder, os.path.basename(file_path)))

# create the photo window with the upload button 
def create_photo_window():
    photo_window = tk.Toplevel(background = "lemonchiffon")
    photo_window.title("Photos")
    photo_window.geometry("600x400")
    label = Label(photo_window).pack()
    
    # upload button
    button = Button(photo_window, text="Upload", command= upload_photo).pack(anchor = "center", side = "bottom", pady = 40)

# create a map window that displays the map
def create_map_window():
    map_window = Toplevel()
    map_window.title("Map")
    map_window.geometry("600x400")
    
    # map widget
    map_widget = TkinterMapView(map_window, width = 600, height = 400, corner_radius = 0)
    map_widget.pack(fill = "both", expand = True)

# quit button is directed here to close program
def close_program():
    main_window.destroy()

# main window with buttons, earth icon, header with program title
def create_main_window():
   
    main_window.geometry("780x780")
    main_window.title("Image Geo Navigator")

    main_window.config(background = "lemonchiffon")

    earth_icon = PhotoImage(file = "images/128px-Earth_icon_2.png")
    main_window.iconphoto(True, earth_icon)

    # header frame
    header_frame =tk.Frame(main_window, height=30, bg = "navajowhite")
    header_frame.pack(fill = "x", pady = (0,10))
    header_label =tk.Label(header_frame, text = program_name, bg = "navajowhite", font = ("Helvetica", 48 ))
    header_label.pack(pady = 10)


    # buttons for other windows DONT FORGET TO FIX THE ISSUE WITH CLOSING!!!!!!!!!!

    # frame 
    frame = tk.Frame(main_window)
    frame.pack(anchor = "center", expand=True)

    Button(main_window, text = "Photos", command=create_photo_window, bg = "paleturquoise", font=("Helvetica", 18), width = 30, height = 3).pack(anchor = "center", expand = True, ipady = 5)
    Button(main_window, text= "Map", command=create_map_window, bg = "paleturquoise", font=("Helvetica", 18), width = 30, height = 3).pack(anchor = "center", expand = True, ipady = 5)
    Button(main_window, text = "Quit", command=close_program, bg = "paleturquoise", font=("Helvetica", 18), width = 30, height = 3).pack(anchor = "center", expand = True, ipady = 5)

    return main_window



main()

