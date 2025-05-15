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
threshold_value_center = 100  # Default threshold for sun disk center detection
threshold_value_sunspot = 100  # Default threshold for sunspot detection
R = 696340  # Radius of the Sun in kilometers
ix, iy = -1, -1
drawing = False
measured_pixel_diameter = None  # Variable to store measured pixel diameter
sun_center = None  # Center of detected sun for distance calculation

# Function to calculate pixel distance
def calculate_pixel_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Browse and display the image
def browse_image():
    global file_path, image, temp_image, display_image, image_label, sun_center
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        temp_image = image.copy()
        display_image = image.copy()
        detect_sun_center()
        
        # Save for Tkinter display without resizing
        cv2.imwrite("temp_display.png", display_image)
        img = tk.PhotoImage(file="temp_display.png")

        image_label.config(image=img)
        image_label.image = img

# Detect the sun and find its center
def detect_sun_center():
    global sun_center, display_image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray_image, threshold_value_center, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        sun_center = (int(x), int(y))
        cv2.circle(display_image, sun_center, int(radius), (0, 0, 255), 2)  # Red circle around the sun
        cv2.circle(display_image, sun_center, 5, (0, 0, 255), -1)           # Red dot at the center
        display_image_in_label()

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
        cv2.line(display_image, points[0], points[1], (255, 0, 0), 1)
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
    _, binary_area = cv2.threshold(gray_area, threshold_value_sunspot, 255, cv2.THRESH_BINARY_INV)
    pixel_count = np.sum(binary_area == 255)
    area_label.config(text=f"Measured sunspot area: {pixel_count} pixels")

# Update threshold for sun center detection
def update_threshold_center_from_entry(*args):
    value = int(threshold_entry_center_var.get())
    threshold_slider_center.set(value)
    adjust_threshold_center(value)

def adjust_threshold_center(value):
    global threshold_value_center
    threshold_value_center = int(value)
    threshold_entry_center_var.set(str(value))
    detect_sun_center()

# Update threshold for sunspot area measurement
def update_threshold_sunspot_from_entry(*args):
    value = int(threshold_entry_sunspot_var.get())
    threshold_slider_sunspot.set(value)
    adjust_threshold_sunspot(value)

def adjust_threshold_sunspot(value):
    global threshold_value_sunspot
    threshold_value_sunspot = int(value)
    threshold_entry_sunspot_var.set(str(value))

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

# Function to start finding sunspot coordinates
def start_finding_sunspot_coordinates():
    image_label.bind("<Button-1>", find_sunspot_coordinates)

def find_sunspot_coordinates(event):
    global measured_pixel_diameter, display_image
    x, y = event.x, event.y
    if sun_center and measured_pixel_diameter:
        pixel_distance = calculate_pixel_distance(sun_center, (x, y))
        distance_km = (pixel_distance / measured_pixel_diameter) * 2 * R / 2  # Convert pixel distance to km
        coord_label.config(text=f"Distance from center: {distance_km:.2f} km")
        cv2.circle(display_image, (x, y), 3, (0, 255, 0), -1)  # Mark the selected point
        display_image_in_label()

# Setup Tkinter window
root = tk.Tk()
root.title("Solar Parameter and Sunspot Measurement Tool")
icon = tk.PhotoImage(file="Logo.png")
root.iconphoto(False, icon)

control_frame = tk.Frame(root, padx=20, pady=20)
control_frame.grid(row=0, column=0, sticky="n")

# Browse Image Button
browse_button = tk.Button(control_frame, text="Browse Image", command=browse_image)
browse_button.grid(row=0, column=0, pady=10)

tk.Label(control_frame, text="Solar Parameter Calculation", font=("Arial", 14)).grid(row=1, column=0, pady=10)
tk.Label(control_frame, text="Enter Date (YYYY-MM-DD):").grid(row=2, column=0)
date_entry = tk.Entry(control_frame)
date_entry.grid(row=3, column=0, pady=5)
date_entry.insert(0, "2024-01-01")
tk.Label(control_frame, text="Hour (0-23):").grid(row=4, column=0)
hour_entry = tk.Entry(control_frame)
hour_entry.grid(row=5, column=0, pady=5)
hour_entry.insert(0, "0")
tk.Label(control_frame, text="Minute (0-59):").grid(row=6, column=0)
minute_entry = tk.Entry(control_frame)
minute_entry.grid(row=7, column=0, pady=5)
minute_entry.insert(0, "0")
tk.Label(control_frame, text="Second (0-59):").grid(row=8, column=0)
second_entry = tk.Entry(control_frame)
second_entry.grid(row=9, column=0, pady=5)
second_entry.insert(0, "0")
calculate_solar_button = tk.Button(control_frame, text="Calculate Solar Parameters", command=calculate_solar_parameters)
calculate_solar_button.grid(row=10, column=0, pady=10)

solar_param_label = tk.Label(control_frame, text="")
solar_param_label.grid(row=11, column=0, pady=10)

measure_diameter_button = tk.Button(control_frame, text="Start Measuring Diameter", command=start_measuring_diameter)
measure_diameter_button.grid(row=12, column=0, pady=10)

# Threshold for Sun Disk Center Detection
threshold_label_center = tk.Label(control_frame, text="Threshold for Sun Disk Center Detection:")
threshold_label_center.grid(row=13, column=0, pady=5)
threshold_entry_center_var = tk.StringVar()
threshold_entry_center = tk.Entry(control_frame, textvariable=threshold_entry_center_var, width=5)
threshold_entry_center.grid(row=14, column=0, pady=5)
threshold_slider_center = tk.Scale(control_frame, from_=0, to=255, orient="horizontal", command=adjust_threshold_center)
threshold_slider_center.grid(row=15, column=0, pady=5)
threshold_entry_center_var.trace_add("write", update_threshold_center_from_entry)

# Threshold for Sunspot Area Measurement
threshold_label_sunspot = tk.Label(control_frame, text="Threshold for Sunspot Area Measurement:")
threshold_label_sunspot.grid(row=16, column=0, pady=5)
threshold_entry_sunspot_var = tk.StringVar()
threshold_entry_sunspot = tk.Entry(control_frame, textvariable=threshold_entry_sunspot_var, width=5)
threshold_entry_sunspot.grid(row=17, column=0, pady=5)
threshold_slider_sunspot = tk.Scale(control_frame, from_=0, to=255, orient="horizontal", command=adjust_threshold_sunspot)
threshold_slider_sunspot.grid(row=18, column=0, pady=5)
threshold_entry_sunspot_var.trace_add("write", update_threshold_sunspot_from_entry)

measure_sunspot_button = tk.Button(control_frame, text="Start Measuring Sunspot Area", command=start_measuring_sunspot_area)
measure_sunspot_button.grid(row=19, column=0, pady=10)
area_label = tk.Label(control_frame, text="")
area_label.grid(row=20, column=0, pady=10)

find_sunspot_coord_button = tk.Button(control_frame, text="Start Find Sunspot's Coordinates", command=start_finding_sunspot_coordinates)
find_sunspot_coord_button.grid(row=21, column=0, pady=10)
coord_label = tk.Label(control_frame, text="")
coord_label.grid(row=22, column=0, pady=10)

image_label = tk.Label(root)
image_label.grid(row=0, column=1, padx=20)

root.mainloop()
