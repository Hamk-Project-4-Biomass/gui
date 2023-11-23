import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from PIL import ImageTk
from functions import *
from pyrealsense import *
from scheduling import ScheduleWindow
import os
import subprocess
import time
import multiprocessing
from croniter import croniter
import sys

class AppState:

    def __init__(self, *args, **kwargs):
        self.realsense = RealSense()

class RealSenseViewer:

    slider_color = []
    auto_btns = []
    end_date = None
    cron_interval = None
    time_until_next_execution = None

    def __init__(self, root, state):
        self.root = root
        self.state = state
        self.create_gui()

    def run(self):
        self.root.mainloop()

    def create_gui(self):
        self.root.state('zoomed')
        self.root.title("RealSense Viewer")

        self.create_top_bar()

        self.create_canvases()

        self.create_schedule_info()
        
        self.create_color_sliders()

        self.create_depth_sliders()


    
    def create_top_bar(self):
        def save_png():
        # Save the color and depth images to the current directory
            color_image = state.realsense.get_color_image()
            depth_image = state.realsense.get_depth_image()

            fulldatestring = datetime.now().strftime("%Y-%m-%d.%H.%M.%S")

            script_dir = os.path.dirname(__file__)

            export.png(color_image, depth_image, fulldatestring, script_dir)

        def save_ply():
            color_frame = state.realsense.get_color_frame()
            depth_frame = state.realsense.get_depth_frame()

            fulldatestring = datetime.now().strftime("%Y-%m-%d.%H.%M.%S")

            script_dir = os.path.dirname(__file__)

            export.ply(color_frame, depth_frame, fulldatestring + ".ply", script_dir)

        def pointcloud_viewer():
            state.realsense.pipe_stop()

            script_dir = os.path.dirname(__file__)

            process = subprocess.Popen(["python", os.path.join(script_dir, "opencv_pointcloud_viewer.py")])
            process.wait()
            state.realsense.pipe_start()

        def open_schedule_window():


            def parent_callback(cron_interval, end_date):
                self.cron_interval = cron_interval

                # Update the scheduling info
                self.planned_end_date_label.configure(text=f"Planned End Date: {end_date}")
                self.interval_label.configure(text=f"Cron interval: {self.cron_interval}")

                #------------------------Cron code------------------------
                cron = croniter(cron_interval, datetime.now())
                self.next_execution = cron.get_next(datetime)

                def check_cron():                        
                    current_time = datetime.now()

                    if self.next_execution > current_time:
                        self.time_until_next_execution = (self.next_execution - current_time).total_seconds()
                        self.time_to_next_picture_label.configure(text=f"Time to Next Picture: {round(self.time_until_next_execution,0)} seconds")
                        print(f"Waiting {self.time_until_next_execution} seconds until the next invocation")
                    else:
                        save_png()
                        save_ply()
                        self.next_execution = cron.get_next(datetime)

                def update_cron():
                    if end_date is None or datetime.now() < end_date:
                        check_cron()
                        self.root.after(1000, update_cron)
                    else:
                        return 0

                update_cron()

                #---------------------------------------------------------
                
            schedule_window = ScheduleWindow(root, parent_callback)
            root.wait_window(schedule_window)

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=0, column=0, columnspan=5, sticky="ew")

        save_button_png = ttk.Button(button_frame, text="Save PNG", command=save_png)
        save_button_png.grid(row=0, column=0, padx=2, pady=2)

        save_button_ply = ttk.Button(button_frame, text="Export Ply", command=save_ply)
        save_button_ply.grid(row=0, column=1, padx=2, pady=2)

        pointcloud_button = ttk.Button(button_frame, text="Pointcloud Viewer", command=pointcloud_viewer)
        pointcloud_button.grid(row=0, column=2, padx=2, pady=2)

        #Create a "Schedule button that will open a new window"
        schedule_button = ttk.Button(button_frame, text="Scheduling", command=open_schedule_window)
        schedule_button.grid(row=0, column=3, padx=2, pady=2)

        quit_button = ttk.Button(button_frame, text="Quit", command=self.root.destroy)
        quit_button.grid(row=0, column=4, padx=2, pady=2)

    def create_canvases(self):
        # Create canvas widgets for color and depth images
        color_canvas = tk.Canvas(self.root, width=640, height=480)
        color_canvas.grid(row=1, column=0, padx=2, pady=2)

        depth_canvas = tk.Canvas(self.root, width=640, height=480)
        depth_canvas.grid(row=1, column=1, padx=2, pady=2)

        def update_canvas():
            try:
                color_tk_image = ImageTk.PhotoImage(image=self.state.realsense.get_color_pill_image())
                depth_tk_image = ImageTk.PhotoImage(image=self.state.realsense.get_depth_pill_image())

                # Update the canvas widgets with the new images
                color_canvas.create_image(0, 0, anchor=tk.NW, image=color_tk_image)
                depth_canvas.create_image(0, 0, anchor=tk.NW, image=depth_tk_image)

                # Keep references to prevent garbage collection
                color_canvas.image = color_tk_image
                depth_canvas.image = depth_tk_image

            except:
                print("No device detected")
                pass
        
        def update():
            update_canvas()
            self.root.after(10, update)

        update()
    
    def create_schedule_info(self):

        #Creating a frame to to display scheduling info
        schedule_info_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
        schedule_info_frame.grid(row=1, column=3, columnspan=1, pady=2, padx=2, sticky="ew")

        # Add a title label to the frame
        title_label = tk.Label(schedule_info_frame, text="Scheduling info", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10)) 

        # Add labels for planned end date, interval, and time to next picture
        self.planned_end_date_label = tk.Label(schedule_info_frame, text=f"Planned End Date: {self.end_date}")
        self.planned_end_date_label.pack(anchor="w")

        self.interval_label = tk.Label(schedule_info_frame, text=f"Cron interval: {self.cron_interval}")
        self.interval_label.pack(anchor="w")

        self.time_to_next_picture_label = tk.Label(schedule_info_frame, text=f"Time to Next Picture:{self.time_until_next_execution}")
        self.time_to_next_picture_label.pack(anchor="w")

        def reset_schedule():
            end_date = None
            cron_interval = None

            #Update the scheduling info
            self.planned_end_date_label.configure(text=f"Planned End Date: {end_date}")
            self.interval_label.configure(text=f"Cron interval: {cron_interval}")
            self.schedule_job.set_stop_event()


        stop_button = ttk.Button(schedule_info_frame, text="Stop process", command=reset_schedule)
        stop_button.pack()

    def create_color_sliders(self):
        # the options for the color camera
        color_frame = tk.Frame(self.root)
        color_frame.grid(row=2, column=0, columnspan=3, pady=2, sticky="ew")

        self.sliders_color = []

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
            self.sliders_color.append(slider1)

        
        def auto_white_balance():
            state.realsense.toggle_color_auto_white_balance()
            self.update_sliders()
            self.update_auto_btns()

        btn = ttk.Button(color_frame, text="Auto Withe Balance", command=auto_white_balance)
        btn.grid(row=0, column=2, padx=2, pady=2)
        self.auto_btns.append(btn)

        def backlight_compensation():
            state.realsense.color_backlight_compensation()
            self.update_sliders()
            self.update_auto_btns()

        backlight_compensation_btn = ttk.Button(color_frame, text="Backlight Compensation", command=backlight_compensation)
        backlight_compensation_btn.grid(row=1, column=2, padx=2, pady=2)
        self.auto_btns.append(backlight_compensation_btn)

        def color_auto_exposure():
            state.realsense.color_auto_exposure()
            self.update_sliders()
            self.update_auto_btns()


        auto_exposure_btn = ttk.Button(color_frame, text="Auto Exposure", command=color_auto_exposure)
        auto_exposure_btn.grid(row=2, column=2, padx=2, pady=2)
        self.auto_btns.append(auto_exposure_btn)

    def update_auto_btns(self):
            self.auto_btns[0].configure(text="Auto White Balance" if self.state.realsense.get_color_auto_white_balance() else "Manual White Balance")
            self.auto_btns[1].configure(text="Backlight Compensation" if self.state.realsense.get_backlight_compensation() else "Manual Backlight Compensation")
            self.auto_btns[2].configure(text="Auto Exposure" if self.state.realsense.get_color_auto_exposure() else "Manual Exposure")
            self.auto_btns[3].configure(text="Auto Exposure" if self.state.realsense.get_depth_auto_exposure() else "Manual Exposure")

    def update_sliders(self):
        self.sliders_color[0].set(self.state.realsense.get_color_exposure())
        self.sliders_color[1].set(self.state.realsense.get_color_brightness())
        self.sliders_color[2].set(self.state.realsense.get_color_contrast())
        self.sliders_color[3].set(self.state.realsense.get_color_gain())
        self.sliders_color[4].set(self.state.realsense.get_color_hue())
        self.sliders_color[5].set(self.state.realsense.get_color_saturation())
        self.sliders_color[6].set(self.state.realsense.get_color_sharpness())
        self.sliders_color[7].set(self.state.realsense.get_color_gamma())
        self.sliders_color[8].set(self.state.realsense.get_color_white_balance())
        self.sliders_color[9].set(self.state.realsense.get_color_power_line_frequency())

    def create_depth_sliders(self):
        sliders_depth = []

        depth_frame = tk.Frame(self.root)
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

        btn = ttk.Button(depth_frame, text="Auto Exposure", command=depth_auto_exposure)
        btn.grid(row=0, column=0, padx=2, pady=2)
        self.auto_btns.append(btn)


if __name__ == "__main__":
    state = AppState()
    root = tk.Tk()
    app = RealSenseViewer(root, state)
    app.run()