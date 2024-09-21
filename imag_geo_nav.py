from tkinter import *
import tkinter as tk
from tkintermapview import TkinterMapView 
from tkinter import Label
from tkinter import filedialog
from PIL import Image, ImageTk
import os 
import shutil

def main():

    app = GeoNavApplication() 

    app.mainloop()


class MapWindow:
    def __init__( self ):
        self.create_map_window()

    def create_map_window( self ):
        self.map_window = Toplevel()
        self.map_window.title("Map")
        self.map_window.geometry("600x400")
    
        # map widget
        self.map_widget = TkinterMapView( self.map_window,
            width = 600,
            height = 400,
            corner_radius = 0
        )
        self.map_widget.pack(fill = "both", expand = True)

class PhotoWindow:

    def __init__( self ):

        self.saved_photos_dir = os.getcwd()+"/saved_photos"

        self.create_photo_window()


    def add_photos_from_dir( self ):

        file_path = filedialog.askopenfilename()#( filetypes = [
            #("Image files", "*.jpg; *.jpeg")
        #])

        if not file_path:
            print("No file path selected!")
            return
    
        os.makedirs( self.saved_photos_dir, exist_ok = True )

        shutil.copy( file_path, os.path.join( self.saved_photos_dir, os.path.basename(file_path) ) )

        # update the photo info since we added photos to our saved dir 
        self.update_photo_info()

    def clear_photos_from_dir( self ):
        files = os.listdir(self.saved_photos_dir)

        image_files = [f for f in files if f.lower().endswith ((".jpg", ".jpeg"))]

        for image in image_files:
            full_image_path = f"{self.saved_photos_dir}/{image}"
            print( f"removing {full_image_path}..." )
            os.remove(full_image_path) 


        # update the photo info since we added photos to our saved dir 
        self.update_photo_info()

    # reads the added photo infomation and updates the internal photo data 
    def update_photo_info( self ):

        # delete the listbox if one was there already
        if self.photo_listbox:
            self.photo_listbox.delete(0, tk.END)

        # exit early if saved photos dir doesn't exist 
        if not os.path.exists(self.saved_photos_dir):
            print( f"Folder {self.saved_photos_dir} not found." )
            return

        files = os.listdir(self.saved_photos_dir)

        image_files = [f for f in files if f.lower().endswith ((".jpg", ".jpeg"))]

        for image in image_files:
            self.photo_listbox.insert( tk.END, image )

            print( f"current image is {image}" )

    def create_photo_window( self ):

        self.photo_window = tk.Toplevel( background = "lemonchiffon" )

        # create photo window
        self.photo_window.title( "Photos" )
        self.photo_window.geometry( "600x400" )
        
        # add button
        button = Button(
            self.photo_window,
            text    = "Add Photos",
            command = self.add_photos_from_dir 
        )
        button.pack(anchor = "center", side = "bottom", pady = 40)
        
        # clear button
        button = Button(
            self.photo_window,
            text    = "Clear Photos",
            command = self.clear_photos_from_dir 
        )
        button.pack(anchor = "center", side = "bottom", pady = 40)

        # create listbox 
        self.photo_listbox = tk.Listbox(self.photo_window, width = 100, height = 75)
        self.photo_listbox.pack(pady = 10)
    
        # update the photo info in case theres already photos in the saved dir
        self.update_photo_info()



# Root of Geo Nav Application 
class GeoNavApplication:

    def __init__( self ):

        self.images_dir = file = os.getcwd()+"/images"

        self.create_main_window()

    # main window with buttons, earth icon, header with program title
    def create_main_window( self ):
        self.main_window = Tk()
    
        self.main_window.geometry("780x780")
        self.main_window.title("Image Geo Navigator")

        self.main_window.config(background = "lemonchiffon")

        # icon for all windows

        earth_icon = PhotoImage( file = f"{self.images_dir}/128px-Earth_icon_2.png" )

        self.main_window.iconphoto( True, earth_icon )

        # header frame
        header_frame = tk.Frame( self.main_window,
            height = 30,
            bg     = "navajowhite"
        )
        header_frame.pack(
            fill = "x",
            pady = (0,10)
        )

        # header label
        header_label = tk.Label(header_frame,
            text = "Image Geo Navigator",
            bg   = "navajowhite",
            font = ("Helvetica", 48 )
        )
        header_label.pack(
            pady = 10
        )

        # buttons for other windows DONT FORGET TO FIX THE ISSUE WITH CLOSING!!!!!!!!!!

        # frame 
        frame = tk.Frame(self.main_window)
        frame.pack(
            anchor = "center",
            expand = True
        )

        # Photos Button
        Button( self.main_window,
            text    = "Photos",
            command = self.create_photo_window,
            bg      = "paleturquoise",
            font    = ("Helvetica", 18),
            width   = 30,
            height  = 3
        ).pack(
            anchor = "center",
            expand = True,
            ipady = 5
        )

        # Map Button    
        Button( self.main_window,
            text    = "Map",
            command = self.create_map_window,
            bg      = "paleturquoise",
            font    = ("Helvetica", 18),
            width = 30,
            height = 3
        ).pack(
            anchor = "center",
            expand = True,
            ipady = 5
        )

        # Quit Button
        Button(self.main_window,
            text    = "Quit",
            command = self.close_program,
            bg      = "paleturquoise",
            font    = ("Helvetica", 18), 
            width   = 30,
            height  = 3
        ).pack(
            anchor = "center",
            expand = True,
            ipady = 5
        )

    def close_program( self ):
        self.main_window.destroy()
    
    def create_map_window( self ):
        self.map_window = MapWindow()

    def create_photo_window( self ):
        self.photo_window = PhotoWindow()

    def mainloop( self ):
        self.main_window.mainloop()

main()

