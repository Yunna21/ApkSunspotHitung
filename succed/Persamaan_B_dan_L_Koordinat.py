import numpy as np
import math

def heliographic_coordinates(x, y, B0, L0, P, DiskDiam):
    # Convert B0, L0, and P from degrees to radians
    B0_rad = math.radians(B0)
    L0_rad = math.radians(L0)
    P_rad = math.radians(P)
    AppDiam = (32/60) + (35/3600)  # Apparent solar diameter in arcminutes converted to degrees (32' 35" ≈ 32.5833 degrees)

    # Calculate rho_1 (the angular distance from the disk center in degrees)
    rho_1 = (AppDiam / DiskDiam) * np.sqrt(x**2 + y**2)
    
    # Calculate rho (the angular distance on the Sun's surface from the disk center)
    rho = math.degrees(math.asin((2 * math.radians(rho_1)) / AppDiam) - math.radians(rho_1))

    # Calculate theta (the position angle)
    theta = math.degrees(math.atan2(x, y))  # atan2 handles quadrant correctly

    # Calculate heliographic latitude (B) in degrees
    B = math.degrees(math.asin(math.sin(B0_rad) * math.cos(math.radians(rho)) + 
                               math.cos(B0_rad) * math.sin(math.radians(rho)) * math.cos(P_rad - math.radians(theta))))

    # Calculate heliographic longitude (L) in degrees
    L = L0 + math.degrees(math.asin(math.sin(math.radians(rho)) * math.sin(P_rad - math.radians(theta)) / math.cos(math.radians(B))))
    B = math.degrees(B)
    L = math.degrees(L)

    return B, L, rho_1, rho, theta, B0, L0, P

# Example usage:
x, y = -27, -22           # Coordinates of the sunspot (in pixels)
DiskDiam = 150            # Diameter of the solar disk (in pixels)
B0 = -3.0                 # Heliographic latitude of solar disk center (degrees)
L0 = 139.5                # Heliographic longitude of solar disk center (degrees)
P = 2.1                   # Position angle of solar north pole (degrees)

B, L, rho_1, rho, theta, B0, L0, P = heliographic_coordinates(x, y, B0, L0, P, DiskDiam)
print(f"rho_1: {rho_1:.2f} degrees")
print(f"rho: {rho:.2f} degrees")
print(f"theta: {theta:.2f} degrees")
print(f"Heliographic Latitude: {B:.2f} degrees")
print(f"Heliographic Longitude: {L:.2f} degrees")
print(f"B0: {B0:.2f} degrees")
print(f"L0: {L0:.2f} degrees")
print(f"P: {P:.2f} degrees")
