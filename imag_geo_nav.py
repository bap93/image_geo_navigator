
# final project: Image Geo Navigator
# author: Brooke Perez
# IDE: Visual Stuido Code
# created: 2024-09-14
# purpose: 

# psuedo code
#
#
#
#
#
#


import folium 
import tkinter as tk
from tkinter import messagebox
from tkintermapview import TkinterMapView

program_name = "Image Geo Navigator"

#
def main():

    # main menu creation 
    root = tk.Tk()
    create_main_window(root)
    #create_map_window(root)
    root.mainloop()

def create_main_window(root):
    root.title("Start Menu")
    
    # window size
    root.geometry("1024x768")

    # background color as lemon chiffon
    root.config(bg="lemonchiffon")

    menu_bar = tk.Menu(root)
    root.config(menu = menu_bar)

    action_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Actions", menu=action_menu)
    
    # create a frame for header/program name at top of window
    header_frame =tk.Frame(root, height=30, bg = "navajowhite")
    header_frame.pack(fill = "x", pady = (0,10))
    header_label =tk.Label(header_frame, text = program_name, bg = "navajowhite", font = ("Helvetica", 28))
    header_label.pack(pady = 10)



    # create frame and buttons, choose font, width, height
    frame = tk.Frame(root)
    frame.pack(anchor = "center", expand=True)

    photo_button = tk.Button(root, text = "Edit Photos", bg = "paleturquoise", font=("Helvetica", 18), width = 30, height = 3)
    photo_button.pack(anchor ="center", expand = True, ipady = 5)
    
    map_button = tk.Button(root, text = "View Map", bg = "paleturquoise", font=("Helvetica", 18), width=30, height = 3)
    map_button.pack(anchor = "center", expand=True, ipady = 5,)

    exit_button = tk.Button(root, text = "Exit", bg = "paleturquoise", font = ("Helvetica", 18), width = 30, height = 3)
    exit_button.pack(anchor = "center", expand = True, ipady = 5)



#def create_map_window(root):

    #Creating a map widget
    #map_widget = TkinterMapView(root, width=800, height=600)
    #map_widget.pack(fill="both", expand =True)


main()






