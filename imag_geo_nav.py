from tkinter import *
from tkinter import font as tkFont
import tkinter as tk
from tkintermapview import TkinterMapView 
from tkinter import filedialog
from PIL import Image, ImageTk
import os 
import math
import shutil


from GPSPhoto import gpsphoto


def main():

    app = GeoNavApplication() 

    app.mainloop()

# class that encapsulates the logic around the map window that generates a map 
# and adds pinpoints for each GPS coordinates
class MapWindow:
    def __init__( self, app ):
        self.app = app
        self.create_map_window()
      
    # create the map toplevel window, set window size using geometry
    def create_map_window( self ):

        # creates a new toplevel 
        self.map_window = Toplevel()
        
        # title for the toplevel map window 
        self.map_window.title("Map")
       
       # set the geometry of the window
        self.map_window.geometry("1280x980")
    
        # map widget from the TkinterMapView library. set the width and height
        self.map_widget = TkinterMapView( self.map_window,
            width = 600,
            height = 400,
            corner_radius = 0
        )
        self.map_widget.pack(fill = "both", expand = True)

        # setting the position of the map to start over
        # the middle of the united states, otherwise it starts across the globe
        # Source Used to figure out center of US: https://en.wikipedia.org/wiki/Geographic_center_of_the_United_States#Contiguous_United_States
        # Source Used to get coordinates: https://www.latlong.net/place/lebanon-ks-usa-12280.html#:~:text=Latitude%20and%20longitude%20coordinates%20are,Kansas%2C%20located%20near%20Highway%20281.
        self.map_widget.set_position(39.809860, -98.555183)

        # set map zoom to resonable number so it is not zoom in annoyingly
        self.map_widget.set_zoom(5)

        # this will add points to map, see function below
        self.add_points()


    # function to execute when a marker is clicked
    def on_marker_click( self, marker, photo ):
        print(f"clicked photo: {photo['name']}")

        # Create a new window to hold the image in
        photo_window = tk.Toplevel(self.map_window)
        photo_window.title(f"Image for {photo['name']}")
        photo_window.geometry("400x400")  # Set window size to fit the image

        # Load and resize the image
        image = Image.open(photo['full_path'])
        image = image.resize((400, 400), Image.Resampling.LANCZOS) 
        image_tk = ImageTk.PhotoImage(image)

        # Create a label to display the image
        label = tk.Label(photo_window, image=image_tk)
        label.image = image_tk
        label.pack()

    # function that adds points to the map based on the latitude and longitude that
    # is extracted from the exif data and converted or from the user editing the exif data via the edit exif button 
    def add_points( self ):
        
        for photo in self.app.get_photos(as_list = True):

            latitude  = photo["latitude"]
            longitude = photo["longitude"]

            if( latitude is None or longitude is None ):
                print(f"Photo ({photo['name']}) does not have both latitude and longitude defined, skipping...")
                continue

            self.map_widget.set_marker(latitude, longitude,
                text    = photo['name'],
                command = lambda marker, photo=photo: self.on_marker_click( marker, photo=photo ),
            )


    def destroy( self ):
        self.map_window.destroy()

            
# class that  
class PhotoTable():
    def __init__(self, parent, app):
        
        self.edit_window = None
        
        # setting passed in intilization varaibles as class properties 
        self.parent = parent # the tkinter object to create this phototable within
        self.app    = app    # the main application class 
        self.data   = self.app.get_photos( as_list=True ) # the list of photos to create a table for
        
        # defining font to use throughout class
        self.font   = tkFont.Font(family="Helvetica", size=12)

        # define results for page constant and page button enums
        self.RESULTS_PER_PAGE = 10 # default the results per page to 10
        self.PAGE_FIRST       = 0  # declare enum for moving to first page
        self.PAGE_BACKWARD    = 1  # declare enum for moving backwards one page
        self.PAGE_FORWARD     = 2  # declare enum for moving forwards one page
        self.PAGE_LAST        = 3  # declare enum for moving to last page

        # define frames
        self.table_frame      = None # main table frame
        self.top_paginator    = None # top paginator frame
        self.bottom_paginator = None # bottom paginator frame

        # initlize pagination variables to inital values
        self.current_page     = 0 # default current page to the first page / keeps track of page table is on 
        self.total_pages      = math.ceil(float(len(self.data) / self.RESULTS_PER_PAGE)) # calculate the total pages wrt the number of photos and the results per page set
        self.result_start     = 0 # keeps track of the start of the current page / default to 0
        self.result_end       = self.RESULTS_PER_PAGE - 1 # keeps track of the end of the current page default to results per page -1 ( b/c array is 0-indexed )
        

        self.create_table()


    # create the top level window that allows to edit exif data
    # congifure the window size, window title
    def edit_image_exif_data( self, photo):
        # checks to see if exists, if so destroy to avoid duplicate windows
        if self.edit_window:
            self.edit_window.destroy()
        self.edit_window = Toplevel(self.parent) # frame to hold edit window
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
            padx  = 10,
            sticky = "e", 
            pady = 5
        )

        

    # reads user entered latitude and longitude, validates input, writes new latitude and longitude to images exif data
    def write_exif_data(self, photo):        
        
        # validating by casting to a float and checking to see if the latitude and longitude are
        # in the correct range
        try:
            latitude  = float(self.latitude_entry.get())
            longitude = float(self.longitude_entry.get())

            if latitude < -89.999999 or latitude > 89.999999:
                raise Exception("Latitude outside of valid range!")
            
            if longitude < -179.999999 or longitude > 179.999999:
                raise Exception("Longitude is outside of valid range!")
        
        # exception error if the user enters in invalid data, not a float 
        except Exception as e:
            tk.messagebox.showerror("Error", "Latitude must be between -89.999999 and 89.999999!\nLongitude must be between -179.999999 and 179.999999!")
            return

        # use the gpsphoto modules modGPSData 
        # https://pypi.org/project/gpsphoto/
        gps_photo = gpsphoto.GPSPhoto(photo["full_path"])
        gps_info  = gpsphoto.GPSInfo((latitude, longitude))

        # Modify GPS Data
        gps_photo.modGPSData(gps_info, photo['full_path'])
        self.app.update_photo_info()
        
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

        # loop over list of paginator objects and add a button for each
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

        # create columns headers
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

        self.app = app # main application
        self.font = tkFont.Font(family="Helvetica", size=12) # font to use throughout window

        self.photo_table       = None # refers to the PhotoTable class instance when its created
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

    # function that clears the photos from directory 
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

        self.photo_table = PhotoTable( self.photo_table_frame, self.app )



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
        #self.app.update_photo_info()


        self.create_photo_table()

    def destroy( self ):
        self.photo_window.destroy()

# Root of Geo Nav Application 
class GeoNavApplication:

    def __init__( self ):

        self.images_dir = file = os.getcwd()+"/images"

        self.saved_photos_dir = os.getcwd()+"/saved_photos"
        
        self.photo_window = None
        self.map_window   = None

        self._photos = {}

        self.create_main_window()

        # retrieve photo info in case there are already photos in saved_photos directory
        self.update_photo_info()

    # main window with buttons, earth icon, header with program title
    def create_main_window( self ):
        self.main_window = Tk()
    
        self.main_window.geometry("1600x900")
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
            pady = (10,0)
        )

        add_text = Label(self.main_window,
        text = "Map Your Adventure Through Photos!",
        bg = "lemonchiffon",
        font = ("Helvetica", 32))
        add_text.pack(pady = (50, 0))
       
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
        earth_image = Image.open( "images/earth_icon.png" )
        earth_image = earth_image.resize((150,150))

        earth_image = ImageTk.PhotoImage(earth_image)

        label = Label(self.main_window,
         image = earth_image,
         bg = "lemonchiffon")
        label.pin_point_image = earth_image

        
        window_height = 1280
        image_height = 150

        label.place( x =250 ,
        y = (window_height // 8) - image_height // 4)

        pin_point = Image.open( "images/pin_point.png" )
        pin_point = pin_point.resize((50,50))

        pin_point = ImageTk.PhotoImage(pin_point)

        label = Label(self.main_window,
         image = pin_point,
         bg = "lemonchiffon")
        label.pin_point_image = pin_point

        
        window_height = 1280
        image_height = 75

        label.place( x =1200 ,
        y = (window_height // 8) - image_height // 4)


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
                
                latitude  = None
                longitude = None

                gps_exif_data = gpsphoto.getGPSData(full_path)
                if 'Latitude' in gps_exif_data and 'Longitude' in gps_exif_data:
                    latitude  = gps_exif_data['Latitude']
                    longitude = gps_exif_data['Longitude']

                    
            except Exception as e:
                print("No GPS data found")
                latitude, longitude = None, None

            self._photos[image] = {
                "name": image,
                "full_path": full_path,
                "latitude": latitude,
                "longitude": longitude,
            }
            
            # Print to see if latitude and longitude is correct
            print(f"photo {image} updated exif data")
            print(f"Your gps coordinates are: {(latitude, longitude)}")

        # recreate the photo window if it currently exists
        if( self.photo_window ):
            self.create_photo_window()

        # recreate the map window if it currently exists
        if( self.map_window ):
            self.create_map_window()


    def close_program( self ):
        self.main_window.destroy()
    
    def create_map_window( self ):
        if( self.map_window ):
            self.map_window.destroy()

        self.map_window = MapWindow( self )

    def create_photo_window( self ):
        if( self.photo_window ):
            self.photo_window.destroy()

        self.photo_window = PhotoWindow( self )

    def mainloop( self ):
        self.main_window.mainloop()

main()

