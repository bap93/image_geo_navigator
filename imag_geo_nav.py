from tkinter import *
from tkinter import font as tkFont
import tkinter as tk
from tkintermapview import TkinterMapView 
from tkinter import filedialog
from PIL import Image, ImageTk
import os 
import math
import shutil
import piexif
def main():

    app = GeoNavApplication() 

    app.mainloop()


class MapWindow:
    def __init__( self, app ):
        self.app = app
        self.create_map_window()
      
    # create the map toplevel window, set window size using geometry
    def create_map_window( self ):

        self.app.update_photo_info()

        self.map_window = Toplevel()
        self.map_window.title("Map")
        self.map_window.geometry("800x600")
    
        # map widget from the TkinterMapView library. set the width and height
        self.map_widget = TkinterMapView( self.map_window,
            width = 600,
            height = 400,
            corner_radius = 0
        )
        self.map_widget.pack(fill = "both", expand = True)

        self.map_widget.set_position(39.8283, -98.5795)

        #self.map_widget.set_marker(39.8283, -98.5795)

        self.map_widget.set_zoom(5)

        self.add_points()

    def add_points( self ):
        
        for photo in self.app.get_photos(as_list = True):

            latitude = photo["latitude"]
            longitude = photo["longitude"]
            name = photo["name"]

            self.map_widget.set_marker(latitude, longitude)

            
  


class PhotoTable():
    def __init__(self, parent, data, on_photo_edit):
        
        # setting passed in intilization varaibles as class properties 
        self.parent = parent
        self.data   = data 
        self.on_photo_edit = on_photo_edit
        
        # defining font to use throughout class
        self.font   = tkFont.Font(family="Helvetica", size=12)

        # define results for page constant and page button enums
        self.RESULTS_PER_PAGE = 10 
        self.PAGE_FIRST       = 0  
        self.PAGE_BACKWARD    = 1 
        self.PAGE_FORWARD     = 2
        self.PAGE_LAST        = 3

        # define frames
        self.table_frame      = None
        self.top_paginator    = None
        self.bottom_paginator = None

        # initlize pagination variables to inital values
        self.current_page     = 0
        self.total_pages      = math.ceil(float(len(self.data) / self.RESULTS_PER_PAGE))
        self.result_start     = 0
        self.result_end       = self.RESULTS_PER_PAGE - 1
        

        self.create_table()


    # create the top level window that allows to edit exif data
    # congifure the window size, window title
    def edit_image_exif_data( self, photo):
      
        self.edit_window = Toplevel(self.parent)
        self.edit_window.grid()
        self.edit_window.grid_columnconfigure(0, weight = 1)
        self.edit_window.title(f"Edit Exif data for {photo['name']}")
        self.edit_window.geometry( "300x150" )
       
       # frame that will act as container for the label and entry field widgets
        form_frame = tk.Frame(self.edit_window)
        
        # using Tkinter grid method to position widgets and frame
        form_frame.grid(column = 0, sticky = "ew")
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # creating the label widget to make the label for latitude and longitude
        # also making the entry fields to edit the latitude and longitude in the edit_window toplevel 
        latitude_label = Label(form_frame, text = "Latitude:")
        latitude_label.grid(row = 0, column = 0, sticky = "w", pady = 5)

        self.latitude_entry = Entry(form_frame)
        self.latitude_entry.grid(row = 0, column = 1, sticky = "ew", pady = 5)

        longitude_label = Label(form_frame, text = "Longitude:")
        longitude_label.grid(row = 1, column = 0, sticky = "w", pady = 5)

        self.longitude_entry = Entry(form_frame)
        self.longitude_entry.grid(row = 1, column = 1, sticky = "ew", pady = 5)

        # this button saves the new latitude and longitude
        # you will see the photo window refresh when you click this save
        tk.Button( form_frame,
            text    = "save", 
            command = lambda photo = photo: self.write_exif_data( photo ),
            font    = self.font 
        ).grid( 
            row = 2,
            column = 1,
            padx  = (10, 0),
            sticky = "e", 
            pady = 5
        )

    # convert the latitude and longitude from decimal to dms  
    # https://www.rapidtables.com/convert/number/degrees-to-degrees-minutes-seconds.html resource for the equations to convert
    # latitude and longitude from decimal to dms
    def convert_to_exif_format(self, decimal):
        degrees = int(decimal)
        minutes = int((decimal - degrees) * 60)
        seconds = ((decimal - degrees - minutes/60) * 3600)

        return[(int(degrees), 1), (int(minutes), 1), (int(seconds * 100), 100)]

    # reads user entered latitude and longitude, validates input, writes new latitude and longitude to images exif data
    def write_exif_data(self, photo):
        print(photo['name'])
        
        # validating by casting to a float and checking to see if the latitude and longitude are
        # in the correct range
        try:
            latitude = float(self.latitude_entry.get())
            longitude = float(self.longitude_entry.get())
            if latitude < -90 or latitude > 90:
                raise Exception("Latitude outside of valid range!")
            if longitude < -180 or longitude > 180:
                raise Exception("Longitude is outside of valid range!")
        
        # exception error if the user enters in invalid data, not a float 
        except Exception as e:
            tk.messagebox.showerror("Error", "Latitude must be between -90 and 90!\nLongitude must be between -180 and 180!")
            return
        
        # convert to proper format to write to exif data, write to exif data
        exif_dict = piexif.load(photo["full_path"])
        exif_dict["GPS"] = {
            piexif.GPSIFD.GPSLatitudeRef: "N" if latitude >= 0 else "S",
            piexif.GPSIFD.GPSLatitude: self.convert_to_exif_format(abs(latitude)),
            piexif.GPSIFD.GPSLongitudeRef: "E" if longitude >= 0 else "W",
            piexif.GPSIFD.GPSLongitude: self.convert_to_exif_format(abs(longitude)),
        }

        # saves it 
        image = Image.open(photo["full_path"])
        image.save(photo["full_path"], "jpeg", exif = piexif.dump(exif_dict))
        self.on_photo_edit()
        # closes the window after the save, which is done by clicking the save button and 
        # input is valid
        self.edit_window.destroy()

    # changes page with respect to the button click
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

    # creates paginator and buttons
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
    
    # returns subset of data relative to page user is on
    def get_page_of_data( self ):

        self.result_start =  self.current_page * self.RESULTS_PER_PAGE
        self.result_end   =  self.result_start + self.RESULTS_PER_PAGE

        # if result end is greater than the total results set the end to the total
        if( self.result_end > len(self.data) ):
            self.result_end = len(self.data)

        return self.data[self.result_start:self.result_end] 

    # paginator table 
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
                background_color = "mintcream"

            # Add Photo Name Column 
            name_frame = tk.Frame( self.table_frame,
                bg = background_color
            )
            
            name_frame.grid(
                row    = row_index,
                sticky = "nsew",
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
                sticky = "nsew",
                column = 1,
                pady = (0, 0)
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
                bg = background_color,
                
            )
            
            longitude_frame.grid(
                row    = row_index,
                sticky = "nsew",
                column = 2,
                pady = (0,0)
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
                pady   = 5
            )
            
            button_frame.grid(
                row    = row_index,
                sticky = "nsew",
                column = 3
            )
            
            tk.Button( button_frame,
                text                = "Edit Exif Data",
                background          = background_color,
                highlightbackground = background_color,
                command             = lambda photo = photo: self.edit_image_exif_data( photo ),
                font                = self.font,
                #height = 1
            ).grid(
                #padx  = (10, 0)
            )

        # Add the Bottom Paginator    
        self.bottom_paginator = self.create_paginator()

    # destroys the photo table   
    def destroy( self ):
        if self.top_paginator is not None:
            self.top_paginator.destroy()

        if self.table_frame is not None:
            self.table_frame.destroy()

        if self.bottom_paginator is not None:
            self.bottom_paginator.destroy()


class PhotoWindow:

    def __init__( self, app ):

        self.app = app
        self.scrollbar = None
        self.table_frame = None
        self.scrollable_photo_canvas = None
        self.font = tkFont.Font(family="Helvetica", size=12)

        self.photo_table       = None
        self.photo_table_frame = None

        self.create_photo_window()

    # allows one or more photos from directory and allows to save to saved photos directory
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
    
        os.makedirs( self.app.saved_photos_dir, exist_ok = True )

        for file_path in file_paths:
            shutil.copy( file_path, os.path.join( self.app.saved_photos_dir, os.path.basename(file_path) ) )

       
        # update the photo info since added photos to our saved dir 
        self.app.update_photo_info()


    def clear_photos_from_dir( self ):
        files = os.listdir(self.app.saved_photos_dir)

        image_files = [f for f in files if f.lower().endswith ((".jpg", ".jpeg"))]

        for image in image_files:
            full_image_path = f"{self.app.saved_photos_dir}/{image}"
            print( f"removing {full_image_path}..." )
            os.remove(full_image_path) 


        # update the photo info since added photos to our saved dir 
        self.app.update_photo_info()

    # create the photo table
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

        self.photo_table = PhotoTable( self.photo_table_frame, self.app.get_photos( as_list=True ), self.app.update_photo_info )



    # create the photo window that will display list of photos 
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
        self.app.update_photo_info()


        self.create_photo_table()
        

# Root of Geo Nav Application 
class GeoNavApplication:

    def __init__( self ):

        self.images_dir = file = os.getcwd()+"/images"

        self.saved_photos_dir = os.getcwd()+"/saved_photos"
        
        self.photo_window = None

        self._photos = {}

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
    
    # This will convert the gps from degrees, mins, secs to the longitude and latitude in decimals 
    # resource to help with dms to decimal equations https://www.rapidtables.com/convert/number/degrees-minutes-seconds-to-degrees.html
    def dms_to_decimal(self, dms, ref):
        degrees = dms[0][0] / dms [0][1]
        #print(degrees)
        minutes = dms[1][0] / dms[1][1]
        #print(minutes)
        seconds = dms[2][0] / dms[2][1]
        #print(seconds)
        decimal = degrees + (minutes / 60) + (seconds / 3600)
        #print( f"decimal is {decimal}")
        if ref in ['S', 'W']:

            decimal = -decimal
            #print(f"decimal is {decimal}")
        return decimal
    
     # reads the added photo infomation and updates the internal photo data 
    def update_photo_info( self ):

        # exit early if saved photos dir doesn't exist 
        if not os.path.exists(self.saved_photos_dir):
            print( f"Folder {self.saved_photos_dir} not found." )
            return

        # read all the jpeg images form the saved directory
        files = os.listdir(self.saved_photos_dir)

        image_files = [f for f in files if f.lower().endswith ((".jpg", ".jpeg"))]

        # recreate the photos dict for accessing the info throughout the class, try to get gps coordinates
        self._photos = {}
        for image in image_files:
            full_path = f"{self.saved_photos_dir}/{image}" 
            try:
                image_obj = Image.open(full_path)
                exif_data = piexif.load(image_obj.info.get('exif', b''))

                gps_latitude = exif_data.get("GPS", {}).get(piexif.GPSIFD.GPSLatitude, None)

                gps_latitude_ref = exif_data.get("GPS", {}).get(piexif.GPSIFD.GPSLatitudeRef,b'').decode()

                gps_longitude = exif_data.get("GPS", {}).get(piexif.GPSIFD.GPSLongitude, None)

                gps_longitude_ref = exif_data.get("GPS", {}).get(piexif.GPSIFD.GPSLongitudeRef, b'').decode()
                
                
                if gps_latitude and gps_longitude:
                    latitude = self.dms_to_decimal(gps_latitude, gps_latitude_ref)
                    longitude = self.dms_to_decimal(gps_longitude, gps_longitude_ref)
                else: latitude, longitude = None, None
                    
            except Exception as e:
                print("No GPS data found")
                latitude, longitude = None, None

            self._photos[image] = {
                "name": image,
                "full_path": full_path,
                "latitude": latitude,
                "longitude": longitude,
                }
            
            # Print to see if lat and long is correct
            print(f"photo {image} updated exif data")
            print(f"Your gps coordinates are: {(latitude, longitude)}")

          


    def close_program( self ):
        self.main_window.destroy()
    
    def create_map_window( self ):
        self.map_window = MapWindow( self )

    def create_photo_window( self ):

        self.photo_window = PhotoWindow( self )

    def mainloop( self ):
        self.main_window.mainloop()

main()

