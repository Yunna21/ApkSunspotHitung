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
threshold_value_center = 100  # Default threshold for sun center detection
threshold_value_sunspot = 100  # Default threshold for sunspot area detection
initial_threshold_value = 0
ix, iy = -1, -1
drawing = False
measured_pixel_radius = None  # Variable to store measured pixel diameter
B, L = 0, 0 # Global variables for B and L values
B0, L0, P = None, None, None  # Define B0, L0, and P as global variables
pixel_count = None
sun_center = None  # Placeholder for sun's center coordinates
measured_pixel_coordinates = []  # List to store coordinates if needed

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

# Function to start finding sunspot coordinates
def start_finding_sunspot_coordinates():
    image_label.bind("<Button-1>", find_sunspot_coordinates)

def find_sunspot_coordinates(event):
    global measured_pixel_coordinates, display_image, B, L
    x, y = event.x, event.y
    if sun_center:
        # Calculate coordinates relative to the sun's center
        B = y - sun_center[1]  # Latitude as y offset from center
        L = x - sun_center[0]  # Longitude as x offset from center

        # Display the relative coordinates
        coord_label.config(text=f"Coordinates relative to center: B = {B:.2f}, L = {L:.2f}")
        
        # Mark the selected point on the image and update the display
        cv2.circle(display_image, (x, y), 3, (0, 255, 0), -1)
        display_image_in_label()  # Refresh the displayed image

# Start measuring diameter
def start_measuring_radius():
    global points
    points = []
    image_label.bind("<Button-1>", measure_radius_callback)

def measure_radius_callback(event):
    global points, display_image, measured_pixel_radius
    x, y = event.x, event.y
    points.append((x, y))
    if len(points) == 2:
        measured_pixel_radius = calculate_pixel_distance(points[0], points[1])
                
        # Draw on the display image
        cv2.line(display_image, points[0], points[1], (255, 0, 0), 1)
        cv2.putText(display_image, f"Diameter: {measured_pixel_radius:.2f} pixels", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        radius_result_label.config(text=f"Radius calculated: {measured_pixel_radius:.2f} pixels")
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

# Solar parameter calculation function
def calculate_solar_parameters():
    global B0, L0, P  # Declare them as global
    date = date_entry.get()
    time_input = hour_entry.get()
    try:
        hour, minute, second = map(int, time_input.split(':'))
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

# Calculate sunspot area based on selected rectangle
def calculate_sunspot_area(x1, y1, x2, y2):
    global pixel_count
    selected_area = temp_image[y1:y2, x1:x2]
    gray_area = cv2.cvtColor(selected_area, cv2.COLOR_BGR2GRAY)
    _, binary_area = cv2.threshold(gray_area, threshold_value_sunspot, 255, cv2.THRESH_BINARY_INV)
    pixel_count = np.sum(binary_area == 255)
    area_label.config(text=f"Measured sunspot area: {pixel_count} pixels")

# Display measured area and calculate real area if diameter is measured
def calculate_real_sunspot_area():
    global B, L, pixel_count, measured_pixel_radius
    if B is None or L is None:
        real_area_label.config(text="B and L values not set.")
        return
    
    if measured_pixel_radius is None:
        real_area_label.config(text="Please measure the sunspot's diameter first.")
        return
    
    # Calculate cosine of p using the solar parameters B and L
    cos_p = (
        math.sin(math.radians(B0)) * math.sin(math.radians(B)) +
        math.cos(math.radians(B0)) * math.cos(math.radians(B)) * math.cos(math.radians(L0 - L)))

    real_area = (pixel_count * 1e6) / (2 * math.pi * (measured_pixel_radius ** 2) * cos_p)
    
    real_area_label.config(text=f"Real sunspot area: {real_area:.2f} /10^6 of Sun's Visible Hemisphere")

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

browse_button = tk.Button(control_frame, text="Browse Image", command=browse_image)
browse_button.grid(row=1, column=0, pady=10)

# Threshold slider and entry for sun disk center detection
threshold_label_center = tk.Label(control_frame, text="Threshold for Sun Disk Center Detection:")
threshold_label_center.grid(row=2, column=0, pady=5)
threshold_slider_center = tk.Scale(control_frame, from_=0, to=255, orient="horizontal", command=adjust_threshold_center)
threshold_slider_center.set(initial_threshold_value)
threshold_slider_center.grid(row=3, column=0, pady=5)

threshold_entry_center_var = tk.StringVar(value=str(initial_threshold_value))
threshold_entry_center = tk.Entry(control_frame, textvariable=threshold_entry_center_var, width=5)
threshold_entry_center.grid(row=3, column=1)
threshold_entry_center_var.trace_add("write", update_threshold_center_from_entry)

measure_radius_button = tk.Button(control_frame, text="Start Measuring Radius", command=start_measuring_radius)
measure_radius_button.grid(row=4, column=0, pady=10)

radius_result_label = tk.Label(control_frame, text="")
radius_result_label.grid(row=5, column=0, pady=10)

# Threshold slider and entry for sunspot detection
tk.Label(control_frame, text="Adjust Sunspot Threshold:").grid(row=7, column=0)
threshold_slider_sunspot = tk.Scale(control_frame, from_=0, to=255, orient="horizontal", command=adjust_threshold_sunspot)
threshold_slider_sunspot.set(threshold_value)
threshold_slider_sunspot.grid(row=8, column=0, pady=5)

threshold_entry_sunspot_var = tk.StringVar(value=str(threshold_value))
threshold_entry_sunspot = tk.Entry(control_frame, textvariable=threshold_entry_sunspot_var, width=5)
threshold_entry_sunspot.grid(row=8, column=1)
threshold_entry_sunspot_var.trace_add("write", update_threshold_sunspot_from_entry)

measure_area_button = tk.Button(control_frame, text="Start Measuring Sunspot's Area", command=start_measuring_sunspot_area)
measure_area_button.grid(row=10, column=0, pady=10)

area_label = tk.Label(control_frame, text="")
area_label.grid(row=11, column=0, pady=10)

find_sunspot_coord_button = tk.Button(control_frame, text="Start Find Sunspot's Coordinates", command=start_finding_sunspot_coordinates)
find_sunspot_coord_button.grid(row=12, column=0, pady=10)
coord_label = tk.Label(control_frame, text="")
coord_label.grid(row=13, column=0, pady=10)

tk.Label(control_frame, text="Enter Date (YYYY-MM-DD):").grid(row=14, column=0)
date_entry = tk.Entry(control_frame)
date_entry.grid(row=15, column=0, pady=5)
date_entry.insert(0, "2024-01-01")  # Set initial date value

tk.Label(control_frame, text="Time (HH:MM:SS):").grid(row=16, column=0)
hour_entry = tk.Entry(control_frame)
hour_entry.grid(row=17, column=0, pady=5)
hour_entry.insert(0, "00:00:00")  # Set initial hour value

calculate_solar_button = tk.Button(control_frame, text="Calculate Solar Parameters", command=calculate_solar_parameters)
calculate_solar_button.grid(row=18, column=0, pady=10)

solar_param_label = tk.Label(control_frame, text="")
solar_param_label.grid(row=19, column=0, pady=10)

calculate_solar_button = tk.Button(control_frame, text="Calculate Real Area of Sunspot", command=calculate_real_sunspot_area)
calculate_solar_button.grid(row=20, column=0, pady=10)

real_area_label = tk.Label(control_frame, text="")
real_area_label.grid(row=21, column=0, pady=10)

image_frame = tk.Frame(root, width=1080 , height=1080, bg="gray")
image_frame.grid(row=0, column=1)
image_label = tk.Label(image_frame)
image_label.grid(row=0, column=0)

root.mainloop()
