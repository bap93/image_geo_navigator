from tkinter import *
from tkinter import font as tkFont
import tkinter as tk
from tkintermapview import TkinterMapView 
from tkinter import filedialog
from PIL import Image, ImageTk
import os 
import math
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


class PhotoTable():
    def __init__(self, parent, data):
        self.parent = parent
        self.data   = data 
        self.font   = tkFont.Font(family="Helvetica", size=12)

        self.RESULTS_PER_PAGE = 10
        self.PAGE_FIRST       = 0 
        self.PAGE_BACKWARD    = 1 
        self.PAGE_FORWARD     = 2
        self.PAGE_LAST        = 3


        self.table_frame      = None
        self.top_paginator    = None
        self.bottom_paginator = None

        self.current_page     = 0
        self.total_pages      = math.ceil(float(len(self.data) / self.RESULTS_PER_PAGE))
        self.result_start     = 0
        self.result_end       = self.RESULTS_PER_PAGE - 1

        self.create_table()

    def edit_image_exif_data( self, photo ):
        name = photo['name']
        print(f"{name} clicked!")
            

    def change_page( self, action ):

        if( action == self.PAGE_FIRST ):

            # do nothing if already on first page 
            if( self.current_page == 0 ):
                return

            self.current_page = 0

        elif( action == self.PAGE_BACKWARD ):

            # do nothing if already on first page 
            if( self.current_page == 0 ):
                return
            
            self.current_page = self.current_page - 1

        
        elif( action == self.PAGE_FORWARD ):

            # do nothing if already on last page
            if( self.current_page == ( self.total_pages - 1 ) ):
                return
            
            self.current_page = self.current_page + 1

        elif( action == self.PAGE_LAST ):
            # do nothing if already on last page
            if( self.current_page == ( self.total_pages - 1 ) ):
                return
            
            self.current_page = self.total_pages - 1

        self.create_table()


    def create_paginator( self ):

        # Create Paginator Frame
        paginator_frame = tk.Frame( self.parent,
            pady   = 4
        )
        paginator_frame.grid(
            sticky = "ew"
        )

        # Page Display Column
        paginator_frame.grid_columnconfigure(0, weight=1)

        # Button Columns
        paginator_frame.grid_columnconfigure(1, weight=1)
        paginator_frame.grid_columnconfigure(2, weight=1)
        paginator_frame.grid_columnconfigure(3, weight=1)
        paginator_frame.grid_columnconfigure(4, weight=1)

        # Count Display Column
        paginator_frame.grid_columnconfigure(5, weight=1)

        # Create the Page Display
        page_display_frame = tk.Frame( paginator_frame, 
            pady   = 4
        )
        page_display_frame.grid(
            row    = 0, 
            sticky = "ew",
            column = 0
        )

        tk.Label( page_display_frame, 
            text = f"Page {self.current_page + 1} of {self.total_pages}",
            font = self.font 
        ).grid(
            padx  = (10, 0)
        )


        # Create Paginator Buttons
        paginator_buttons = [{
            "text": "<<",
            "action": self.PAGE_FIRST
        },{
            "text": "<",
            "action": self.PAGE_BACKWARD
        },{
            "text": ">",
            "action": self.PAGE_FORWARD
        },{
            "text": ">>",
            "action": self.PAGE_LAST
        }]

        for paginator_index, paginator_button in enumerate( paginator_buttons, start = 1 ):
            text   = paginator_button['text']
            action = paginator_button['action']

            # Add Button Column
            button_frame = tk.Frame( paginator_frame )
            
            button_frame.grid(
                row    = 0, 
                sticky = "ew",
                column = paginator_index 
            )
            
            tk.Button( button_frame,
                text    = text, 
                command = lambda action = action: self.change_page( action ),
                font    = self.font 
            ).grid(
                padx  = (10, 0)
            )

       # Create the Count Display
        count_display_frame = tk.Frame( paginator_frame, 
            pady   = 4
        )
        count_display_frame.grid(
            row    = 0, 
            sticky = "ew",
            column = 5
        )

        tk.Label( count_display_frame, 
            text = f"{self.result_start + 1} - {self.result_end} of {len(self.data)}",
            font = self.font 
        ).grid()

        return paginator_frame

    def get_page_of_data( self ):

        self.result_start =  self.current_page * self.RESULTS_PER_PAGE
        self.result_end   =  self.result_start + self.RESULTS_PER_PAGE

        # if result end is greater than the total results set the end to the total
        if( self.result_end > len(self.data) ):
            self.result_end = len(self.data)

        return self.data[self.result_start:self.result_end] 


    def create_table(self):

        # clean up existing table if there is one
        self.destroy()
        
        # Get Current Page of Data 
        page_of_data = self.get_page_of_data()

        # Create the Top Paginator
        self.top_paginator = self.create_paginator()


        # Create the Table's Frame
        self.table_frame = Frame(self.parent,
            background = "yellow"
        )
        self.table_frame.grid(
            sticky = "ew"
        )

        self.table_frame.grid_columnconfigure(0, weight=3)
        self.table_frame.grid_columnconfigure(1, weight=3)
        self.table_frame.grid_columnconfigure(2, weight=3)
        self.table_frame.grid_columnconfigure(3, weight=1)

        # Create Headers
        headers = [{
            "name": "Photo Name",
        },{
            "name": "Latitude",
        },{
            "name": "Longitude",
        },{
            "name": "Exif Data"            
        }]

        header_background = "dim gray"
        for column_index, header in enumerate( headers ):
            name = header['name']

            header_frame = tk.Frame( self.table_frame,
                bg     = header_background 
            )
            
            header_frame.grid(
                row    = 0, 
                sticky = "ew",
                column = column_index,
            )

            tk.Label( header_frame, 
                text       = name,
                background = header_background,
                height     = 2,
                font       = self.font 
            ).grid(
                padx  = (10, 0)
            )

        # Create Rows
        for row_index, photo in enumerate( page_of_data, start = 1 ):
            name      = photo['name']
            latitude  = photo.get('latitude', "")
            longitude = photo.get('longitude', "")

            # alternate row colors
            background_color = "whitesmoke"
            if( row_index % 2 == 0 ):
                background_color = "gainsboro"

            # Add Photo Name Column 
            name_frame = tk.Frame( self.table_frame,
                bg = background_color
            )
            
            name_frame.grid(
                row    = row_index,
                sticky = "ew",
                column = 0
            )

            tk.Label( name_frame, 
                text       = name,
                background = background_color,
                fg         = "grey15",
                height     = 2,
                font       = self.font 
            ).grid(
                padx  = (10, 0)
            )

            # Add Latitude Column 
            latitude_frame = tk.Frame( self.table_frame,
                bg = background_color
            )
            
            latitude_frame.grid(
                row    = row_index,
                sticky = "ew",
                column = 1
            )

            tk.Label( latitude_frame, 
                text       = latitude,
                background = background_color,
                fg         = "grey15",
                height     = 2,
                font       = self.font 
            ).grid(
                padx  = (10, 0)
            )

            # Add Longitude Column
            longitude_frame = tk.Frame( self.table_frame,
                bg = background_color
            )
            
            longitude_frame.grid(
                row    = row_index,
                sticky = "ew",
                column = 2
            )

            tk.Label( longitude_frame, 
                text       = longitude,
                background = background_color,
                fg         = "grey15",
                height     = 2,
                font       = self.font 
            ).grid(
                padx  = (10, 0)
            )


            # Add Edit Exif Data Button Column
            button_frame = tk.Frame( self.table_frame,
                bg     = background_color,
                pady   = 4
            )
            
            button_frame.grid(
                row    = row_index,
                sticky = "ew",
                column = 3
            )
            
            tk.Button( button_frame,
                text                = "Edit Exif Data",
                background          = background_color,
                highlightbackground = background_color,
                command             = lambda photo = photo: self.edit_image_exif_data( photo ),
                font                = self.font 
            ).grid(
                padx  = (10, 0)
            )

        # Add the Bottom Paginator    
        self.bottom_paginator = self.create_paginator()

            
    def destroy( self ):
        if self.top_paginator is not None:
            self.top_paginator.destroy()

        if self.table_frame is not None:
            self.table_frame.destroy()

        if self.bottom_paginator is not None:
            self.bottom_paginator.destroy()



class PhotoWindow:

    def __init__( self ):

        self.scrollbar = None
        self.table_frame = None
        self.scrollable_photo_canvas = None
        self.font = tkFont.Font(family="Helvetica", size=12)

        self.photo_table       = None
        self.photo_table_frame = None

        self.saved_photos_dir = os.getcwd()+"/saved_photos"

        self.create_photo_window()


    def add_photos_from_dir( self ):

        file_paths = filedialog.askopenfilenames(
            title     = "Select Images", 
            filetypes = [
                ("Images", "*.jpg *.jpeg"),
            ]
        )

        if not file_paths:
            print("No files selected!")
            return
    
        os.makedirs( self.saved_photos_dir, exist_ok = True )

        for file_path in file_paths:
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

    def create_photo_table( self ):
        if( self.photo_table_frame is not None):
            self.photo_table_frame.destroy()

        # Create a frame for the table
        self.photo_table_frame = tk.Frame( self.photo_window,
            bg     = "navajowhite"
        )
        self.photo_table_frame.grid(
            column = 0,
            padx   = 10,
            sticky = "ew"
        )
        self.photo_table_frame.grid_columnconfigure(0, weight=1)

        self.photo_table = PhotoTable( self.photo_table_frame, self.get_photos( as_list=True ) )

    # reads the added photo infomation and updates the internal photo data 
    def update_photo_info( self ):

        # exit early if saved photos dir doesn't exist 
        if not os.path.exists(self.saved_photos_dir):
            print( f"Folder {self.saved_photos_dir} not found." )
            return

        # read all the jpeg images form the saved directory
        files = os.listdir(self.saved_photos_dir)

        image_files = [f for f in files if f.lower().endswith ((".jpg", ".jpeg"))]

        # recreate the photos dict for accessing the info throughout the class
        self._photos = {}
        for image in image_files:
            self._photos[image] = {
                "name": image,
                "full_path": f"{self.saved_photos_dir}/{image}"
            }

        # recreate the photo list box with the updated info
        #self.create_photo_list_box()
        self.create_photo_table()

    # method for helping get image information
    def get_photos( self, as_list=False, image_name=None ):

        # if they passed in the image_name parameter just return the image dict 
        # associated with that image
        if( image_name is not None ):
            return self._photos[image_name]

        # if they passed in the as_list parameter covert the self._photos to a list
        # sorted by the image name and return that
        if( as_list ):
            photo_list = []
            photo_keys = list(self._photos.keys())

            photo_keys.sort()
            for photo_key in photo_keys:
                photo_list.append(self._photos[photo_key])

            return photo_list

        # if no parameters were passed just return the photos dict 
        return self._photos 


    def create_photo_window( self ):

        self.photo_window = tk.Toplevel( background = "lemonchiffon" )

        # create photo window
        self.photo_window.title( "Photos" )
        self.photo_window.geometry( "1000x700" )
        self.photo_window.grid()
        self.photo_window.grid_columnconfigure(0, weight=1)

        # header frame
        self.button_frame = tk.Frame( self.photo_window,
            bg     = "navajowhite"
        )
        self.button_frame.grid()
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        
        # Add Photos Button
        Button(
            self.button_frame,
            text    = "Add Photos",
            highlightbackground = "lemonchiffon",
            command = self.add_photos_from_dir 
        ).grid(
            row    = 0,
            sticky = "ew",
            column = 1
        )
        
        # Clear Photos Button
        Button(
            self.button_frame,
            text    = "Clear Photos",
            highlightbackground = "lemonchiffon",
            command = self.clear_photos_from_dir 
        ).grid(
            row    = 0,
            sticky = "ew",
            column = 2
        )

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

