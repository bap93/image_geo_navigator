
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

def main():

    # main menu creation 
    root = tk.Tk()
    create_main_window(root)
    create_map_window(root)
    root.mainloop()

def create_main_window(root):
    root.title("Start Menu")
    root.geometry("800x600")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    action_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Actions", menu=action_menu)


def create_map_window(root):

    # Creating a map widget
    map_widget = TkinterMapView(root, width=800, height=600)
    map_widget.pack(fill="both", expand =True)


main()






