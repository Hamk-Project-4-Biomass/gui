import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import ImageTk
from functions import *
from pyrealsense import *
import os
import subprocess

class AppState:

    def __init__(self, *args, **kwargs):
        self.realsense = RealSense()
        

# Create a Tkinter window
root = tk.Tk()
root.state('zoomed')  # For Windows

root.title("RealSense Viewer")

# Create an instance of the AppState class
state = AppState()

# Create a frame for buttons
# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

sliders_color = []
sliders_depth = []
auto_btns = []

def update_auto_btns():

        auto_btns[0].configure(text="Auto White Balance" if state.realsense.get_color_auto_white_balance() else "Manual White Balance")
        auto_btns[1].configure(text="Backlight Compensation" if state.realsense.get_backlight_compensation() else "Manual Backlight Compensation")
        #auto_btns[2].configure(text="Low Light Compensation" if state.realsense.get_low_light_compensation() else "Manual Low Light Compensation")
        auto_btns[3].configure(text="Auto Exposure" if state.realsense.get_color_auto_exposure() else "Manual Exposure")

        auto_btns[4].configure(text="Auto Exposure" if state.realsense.get_depth_auto_exposure() else "Manual Exposure")

# Create a function to update the sliders
def update_sliders():
    # Update the sliders with the current values
    sliders_color[0].set(state.realsense.get_color_exposure())
    sliders_color[1].set(state.realsense.get_color_brightness())
    sliders_color[2].set(state.realsense.get_color_contrast())
    sliders_color[3].set(state.realsense.get_color_gain())
    sliders_color[4].set(state.realsense.get_color_hue())
    sliders_color[5].set(state.realsense.get_color_saturation())
    sliders_color[6].set(state.realsense.get_color_sharpness())
    sliders_color[7].set(state.realsense.get_color_gamma())
    sliders_color[8].set(state.realsense.get_color_white_balance())
    sliders_color[9].set(state.realsense.get_color_power_line_frequency())

    sliders_depth[0].set(state.realsense.get_depth_exposure())
    sliders_depth[1].set(state.realsense.get_depth_gain())
    sliders_depth[2].set(state.realsense.get_depth_power())

# Create a function to update the canvas
def update_canvas():
    try:
        color_tk_image = ImageTk.PhotoImage(image=state.realsense.get_color_pill_image())
        depth_tk_image = ImageTk.PhotoImage(image=state.realsense.get_depth_pill_image())

        # Update the canvas widgets with the new images
        color_canvas.create_image(0, 0, anchor=tk.NW, image=color_tk_image)
        depth_canvas.create_image(0, 0, anchor=tk.NW, image=depth_tk_image)

        # Keep references to prevent garbage collection
        color_canvas.image = color_tk_image
        depth_canvas.image = depth_tk_image

    except:
        print("No device detected")
        pass


# Create canvas widgets for color and depth images
color_canvas = tk.Canvas(root, width=640, height=480)
color_canvas.grid(row=1, column=0, padx=2, pady=2)
depth_canvas = tk.Canvas(root, width=640, height=480)
depth_canvas.grid(row=1, column=1, padx=2, pady=2)


# Create a "Save PNG" button
def save_png():
    # Save the color and depth images to the current directory
    color_image = state.realsense.get_color_pill_image()
    depth_image = state.realsense.get_depth_pill_image()

    fulldatestring = datetime.now().strftime("%Y-%m-%d.%H.%M.%S")

    script_dir = os.path.dirname(__file__)

    export.png(color_image, depth_image, fulldatestring, script_dir)


save_button_png = ttk.Button(button_frame, text="Save PNG", command=save_png)
save_button_png.grid(row=0, column=0, padx=2, pady=2)


def save_ply():
    color_frame = state.realsense.get_color_frame()
    depth_frame = state.realsense.get_depth_frame()

    fulldatestring = datetime.now().strftime("%Y-%m-%d.%H.%M.%S")

    script_dir = os.path.dirname(__file__)

    export.ply(color_frame, depth_frame, fulldatestring + ".ply", script_dir)


save_button_ply = ttk.Button(button_frame, text="Export Ply", command=save_ply)
save_button_ply.grid(row=0, column=1, padx=2, pady=2)


def viewer():
    state.realsense.pipe_stop()

    #get the file path of the current script
    script_dir = os.path.dirname(__file__)

    process = subprocess.Popen(["python", script_dir +  "\\opencv_pointcloud_viewer.py"])
    process.wait()
    state.realsense.pipe_start()


pointcloud_button = ttk.Button(button_frame, text="Pointcloud Viewer", command=viewer)
pointcloud_button.grid(row=0, column=2, padx=2, pady=2)

# Create a "Quit" button
quit_button = ttk.Button(button_frame, text="Quit", command=root.destroy)
quit_button.grid(row=0, column=3, padx=2, pady=2)


# Add an update loop to periodically update the canvas
def update():
    update_canvas()
    root.after(10, update)  # Adjust the update interval as needed


# the options for the color camera
color_frame = tk.Frame(root)
color_frame.grid(row=2, column=0, columnspan=3, pady=2, sticky="ew")


slider_data = [
    ("exposure",  {"from_": 1, "to": 10000, "orient": tk.HORIZONTAL}, state.realsense.set_color_exposure),
    ("brightness",  {"from_": -64, "to": 64, "orient": tk.HORIZONTAL}, state.realsense.set_color_brightness),
    ("contrast",  {"from_": 0, "to": 100, "orient": tk.HORIZONTAL}, state.realsense.set_color_contrast),
    ("gain",  {"from_": 0, "to": 128, "orient": tk.HORIZONTAL}, state.realsense.set_color_gain),
    ("Hue",  {"from_": -180, "to": 180, "orient": tk.HORIZONTAL}, state.realsense.set_color_hue),
    ("Saturation",  {"from_": 0, "to": 100, "orient": tk.HORIZONTAL}, state.realsense.set_color_saturation),
    ("Sharpness",  {"from_": 0, "to": 100, "orient": tk.HORIZONTAL}, state.realsense.set_color_sharpness),
    ("Gamma",  {"from_": 100, "to": 500, "orient": tk.HORIZONTAL}, state.realsense.set_color_gamma),
    ("White Balance",  {"from_": 2800, "to": 6500, "orient": tk.HORIZONTAL}, state.realsense.set_color_white_balance),
    ("power line frequency", {"from_": 1, "to": 3, "orient": tk.HORIZONTAL}, state.realsense.set_color_power_line_frequency),
]

for i, (text, slider_args, command) in enumerate(slider_data):
    label = tk.Label(color_frame, text=text)
    label.grid(row=i, column=0, padx=2, pady=2)
    slider1 = tk.Scale(color_frame, **slider_args)
    slider1.grid(row=i, column=1, padx=2, pady=2)
    slider1.bind("<ButtonRelease-1>", lambda event, slider=slider1, cmd=command: cmd(slider.get()))
    sliders_color.append(slider1)


# Create a slider with a label on top
def auto_white_balance():
    state.realsense.toggle_color_auto_white_balance()
    update_sliders()
    update_auto_btns()

btn = ttk.Button(color_frame, text="Auto Withe Balance", command=auto_white_balance)
btn.grid(row=0, column=2, padx=2, pady=2)
auto_btns.append(btn)

def backlight_compensation():
    state.realsense.color_backlight_compensation()
    update_sliders()
    update_auto_btns()

backlight_compensation_btn = ttk.Button(color_frame, text="Backlight Compensation", command=backlight_compensation)
backlight_compensation_btn.grid(row=1, column=2, padx=2, pady=2)
auto_btns.append(backlight_compensation_btn)

def low_light_compensation():
    state.realsense.color_low_light_compensation()
    update_sliders() 
    update_auto_btns() 

low_light_compensation_btn = ttk.Button(color_frame, text="Low Light Compensation", command=low_light_compensation)
low_light_compensation_btn.grid(row=2, column=2, padx=2, pady=2)
auto_btns.append(low_light_compensation_btn)

def color_auto_exposure():
    state.realsense.color_auto_exposure()
    update_sliders()
    update_auto_btns()


auto_exposure_btn = ttk.Button(color_frame, text="Auto Exposure", command=color_auto_exposure)
auto_exposure_btn.grid(row=3, column=2, padx=2, pady=2)
auto_btns.append(auto_exposure_btn)


# the options for the depth camera
depth_frame = tk.Frame(root)
depth_frame.grid(row=2, column=1, columnspan=3, pady=2, sticky="ne")


sliders_data = [
    ("exposure",  {"from_": 1, "to": 166, "orient": tk.HORIZONTAL}, state.realsense.set_depth_exposure),
    ("gain",  {"from_": 16, "to": 248, "orient": tk.HORIZONTAL}, state.realsense.set_depth_gain),
    ("laser power",  {"from_": 0, "to": 360, "orient": tk.HORIZONTAL}, state.realsense.set_depth_power),
]

for i, (text, slider_args, command) in enumerate(sliders_data):
    label = tk.Label(depth_frame, text=text)
    label.grid(row=i, column=2, padx=2, pady=2)
    slider1 = tk.Scale(depth_frame, **slider_args)
    slider1.grid(row=i, column=1, padx=2, pady=2)
    slider1.bind("<ButtonRelease-1>", lambda event, slider=slider1, cmd=command: cmd(slider.get()))
    sliders_depth.append(slider1)   

def depth_auto_exposure():
    state.realsense.depth_auto_exposure()
    update_sliders()
    update_auto_btns()

btn = ttk.Button(depth_frame, text="Auto Exposure", command=depth_auto_exposure)
btn.grid(row=0, column=0, padx=2, pady=2)
auto_btns.append(btn)

update()

root.mainloop()