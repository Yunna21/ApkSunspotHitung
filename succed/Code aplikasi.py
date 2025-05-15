import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import math
import sys
import os

# Add the directory to sys.path to import the solar parameter module
sys.path.append(r"C:\Yuna\astro aplikasi\succed")

# Import the solar parameter calculation function
from Persamaan_Solar_Parameter import calculate_solar_coordinates

# Global variables
file_path = None
image = None
temp_image = None
display_image = None
points = []  # List to store points for distance measurement
threshold_value = 100  # Default threshold for sunspot detection
R = 696340  # Radius of the Sun in kilometers
ix, iy = -1, -1
drawing = False
measured_pixel_diameter = None  # Variable to store measured pixel diameter

# Function to calculate pixel distance
def calculate_pixel_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Browse and display the image
def browse_image():
    global file_path, image, temp_image, display_image, image_label
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        temp_image = image.copy()
        display_image = image.copy()
        
        # Save for Tkinter display without resizing
        cv2.imwrite("temp_display.png", display_image)
        img = tk.PhotoImage(file="temp_display.png")

        image_label.config(image=img)
        image_label.image = img

# Start measuring diameter
def start_measuring_diameter():
    global points
    points = []
    image_label.bind("<Button-1>", measure_diameter_callback)

def measure_diameter_callback(event):
    global points, display_image, measured_pixel_diameter
    x, y = event.x, event.y
    points.append((x, y))
    if len(points) == 2:
        measured_pixel_diameter = calculate_pixel_distance(points[0], points[1])
        measured_radius = measured_pixel_diameter / 2
        
        # Draw on the display image
        cv2.line(display_image, points[0], points[1], (255, 0, 0), 1)
        cv2.putText(display_image, f"Diameter: {measured_pixel_diameter:.2f} pixels", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(display_image, f"Radius: {measured_radius:.2f} pixels", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        diameter_result_label.config(text=f"Diameter measured: {measured_pixel_diameter:.2f} pixels")
        radius_result_label.config(text=f"Radius calculated: {measured_radius:.2f} pixels")
        points.clear()
        
        # Refresh the displayed image
        display_image_in_label()

# Start measuring sunspot area
def start_measuring_sunspot_area():
    image_label.bind("<Button-1>", measure_sunspot_area_callback)
    image_label.bind("<ButtonRelease-1>", finish_measuring_area)

def measure_sunspot_area_callback(event):
    global ix, iy, drawing
    ix, iy = event.x, event.y
    drawing = True

def finish_measuring_area(event):
    global drawing, display_image
    if drawing:
        x2, y2 = event.x, event.y
        cv2.rectangle(display_image, (ix, iy), (x2, y2), (0, 255, 0), 1)
        calculate_sunspot_area(ix, iy, x2, y2)
        drawing = False

# Calculate sunspot area based on selected rectangle
def calculate_sunspot_area(x1, y1, x2, y2):
    selected_area = temp_image[y1:y2, x1:x2]
    gray_area = cv2.cvtColor(selected_area, cv2.COLOR_BGR2GRAY)
    _, binary_area = cv2.threshold(gray_area, threshold_value, 255, cv2.THRESH_BINARY_INV)
    pixel_count = np.sum(binary_area == 255)
    
    # Display measured area and calculate real area if diameter is measured
    area_label.config(text=f"Measured sunspot area: {pixel_count} pixels")
    if measured_pixel_diameter is not None:
        measured_radius = measured_pixel_diameter / 2
        real_area = (pixel_count * 1e6) / (2 * math.pi * (measured_radius ** 2))
        real_area_label.config(text=f"Real sunspot area: {real_area:.2f} km²")
    cv2.imshow("Detected Sunspots", binary_area)

# Update threshold based on entry and slider values
def update_threshold_from_entry(*args):
    value = int(threshold_entry_var.get())
    threshold_slider.set(value)
    adjust_threshold(value)

def adjust_threshold(value):
    global threshold_value
    threshold_value = int(value)
    threshold_entry_var.set(str(value))

# Solar parameter calculation function
def calculate_solar_parameters():
    date = date_entry.get()
    hour = hour_entry.get()
    minute = minute_entry.get()
    second = second_entry.get()
    try:
        observation_datetime = datetime.strptime(f"{date} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
        julian_date = observation_datetime.toordinal() + 1721424.5 + (
            observation_datetime.hour - 12) / 24 + observation_datetime.minute / 1440 + observation_datetime.second / 86400
        
        B0, L0, P = calculate_solar_coordinates(julian_date)
        solar_param_label.config(text=f"B0: {B0:.6f}°\nL0: {L0:.6f}°\nP: {P:.6f}°")
    except ValueError:
        solar_param_label.config(text="Invalid date/time format. Ensure all fields are correct.")

# Refresh displayed image in Tkinter
def display_image_in_label():
    cv2.imwrite("temp_display.png", display_image)
    img = tk.PhotoImage(file="temp_display.png")
    image_label.config(image=img)
    image_label.image = img

# Setup Tkinter window
root = tk.Tk()
root.title("Solar Parameter and Sunspot Measurement Tool")

# Set a custom icon (make sure 'path_to_icon.png' exists in the specified location)
icon = tk.PhotoImage(file="Logo.png")  # Use a .png file
root.iconphoto(False, icon)

# Left section for controls
control_frame = tk.Frame(root, padx=20, pady=20)
control_frame.grid(row=0, column=0, sticky="n")

tk.Label(control_frame, text="Solar Parameter Calculation", font=("Arial", 14)).grid(row=0, column=0, pady=10)

tk.Label(control_frame, text="Enter Date (YYYY-MM-DD):").grid(row=1, column=0)
date_entry = tk.Entry(control_frame)
date_entry.grid(row=2, column=0, pady=5)
date_entry.insert(0, "2024-01-01")  # Set initial date value

tk.Label(control_frame, text="Hour (0-23):").grid(row=3, column=0)
hour_entry = tk.Entry(control_frame)
hour_entry.grid(row=4, column=0, pady=5)
hour_entry.insert(0, "0")  # Set initial hour value

tk.Label(control_frame, text="Minute (0-59):").grid(row=5, column=0)
minute_entry = tk.Entry(control_frame)
minute_entry.grid(row=6, column=0, pady=5)
minute_entry.insert(0, "0")  # Set initial minute value

tk.Label(control_frame, text="Second (0-59):").grid(row=7, column=0)
second_entry = tk.Entry(control_frame)
second_entry.grid(row=8, column=0, pady=5)
second_entry.insert(0, "0")  # Set initial second value

calculate_solar_button = tk.Button(control_frame, text="Calculate Solar Parameters", command=calculate_solar_parameters)
calculate_solar_button.grid(row=9, column=0, pady=10)

solar_param_label = tk.Label(control_frame, text="")
solar_param_label.grid(row=10, column=0, pady=10)

browse_button = tk.Button(control_frame, text="Browse Image", command=browse_image)
browse_button.grid(row=11, column=0, pady=10)

measure_diameter_button = tk.Button(control_frame, text="Start Measuring Diameter", command=start_measuring_diameter)
measure_diameter_button.grid(row=12, column=0, pady=10)

diameter_result_label = tk.Label(control_frame, text="")
diameter_result_label.grid(row=13, column=0, pady=10)

radius_result_label = tk.Label(control_frame, text="")
radius_result_label.grid(row=14, column=0, pady=10)

# Threshold slider and entry for sunspot detection
tk.Label(control_frame, text="Adjust Sunspot Threshold:").grid(row=15, column=0)
threshold_slider = tk.Scale(control_frame, from_=0, to=255, orient="horizontal", command=adjust_threshold)
threshold_slider.set(threshold_value)
threshold_slider.grid(row=16, column=0, pady=5)

threshold_entry_var = tk.StringVar(value=str(threshold_value))
threshold_entry = tk.Entry(control_frame, textvariable=threshold_entry_var, width=5)
threshold_entry.grid(row=16, column=1)
threshold_entry_var.trace_add("write", update_threshold_from_entry)

measure_area_button = tk.Button(control_frame, text="Start Measuring Sunspot's Area", command=start_measuring_sunspot_area)
measure_area_button.grid(row=17, column=0, pady=10)

area_label = tk.Label(control_frame, text="")
area_label.grid(row=18, column=0, pady=10)

real_area_label = tk.Label(control_frame, text="")
real_area_label.grid(row=19, column=0, pady=10)

image_frame = tk.Frame(root, width=1080 , height=1080, bg="gray")
image_frame.grid(row=0, column=1)
image_label = tk.Label(image_frame)
image_label.grid(row=0, column=0)

root.mainloop()
