import math

def calculate_solar_coordinates(julian_date):
    # Calculate number of days since J2000.0
    n = (julian_date - 2451545.0) / 36525  # Changed to / 36525 instead of / 365250 for correct century calculation
    
    # Mean longitude of the Sun (L)
    L = (280.460 + 36000.7698 * n) % 360
    
    # Mean longitude of the Moon (L1)
    L1 = (218.3165 + 481267.8813 * n) % 360
    
    # Longitude of Ascending Node (Omega)
    Omega = (125.04 - 1934.136 * n) % 360  # Corrected sign
    
    # Lo, Bo, and P Variable
    Tetha = ((julian_date - 2398220) * (360 / 25.38)) % 360
    I = 7.25
    K = 73.6667 + (1.3958333 / 36525) * (julian_date - 2396758)
    
    # Mean anomaly of the Sun (M)
    M = (357.52910 + 35999.05030 * n - 0.0001559 * n * n - 0.00000048 * n * n * n) % 360  # Corrected the formula

    # Convert M to radians for the trigonometric functions
    M_rad = math.radians(M)
    
    # Ecliptic longitude of the Sun (λ)
    lambda_sun = (L + (1.914602 - 0.004817 * n - 0.000014 * n * n) * math.sin(M_rad) + 
                  (0.019993 - 0.000101 * n) * math.sin(2 * M_rad) + 0.000289 * math.sin(3 * M_rad)) % 360
    
    lambda_aksen = (lambda_sun + 1.397 * n - 0.00031 * n * n) % 360
    
    # Mean obliquity of the ecliptic (epsilon0)
    epsilon0 = 23.43929111 - 0.0130041667 * n - 1.636 * 1e-7 * n * n + 5.03611 * 1e-7 * n * n * n
    
    # Nutation in obliquity (deltaepsilon)
    deltaepsilon = (0.0025556 * math.cos(math.radians(Omega)) + 
                    1.58025e-4 * math.cos(math.radians(2 * L)) + 
                    2.77778e-5 * math.cos(math.radians(2 * L1)) - 
                    2.5e-5 * math.cos(math.radians(2 * Omega)))
    
    # Obliquity of the ecliptic (epsilon)
    epsilon = epsilon0 + deltaepsilon
    
    # Convert lambda_sun, lambda_aksen, and epsilon to radians for the trigonometric functions
    lambda_rad = math.radians(lambda_sun)
    lambda_rad_aksen = math.radians(lambda_aksen)
    epsilon_rad = math.radians(epsilon)
    
    # Calculate x and y for P calculation
    x = math.degrees(math.atan(-math.cos(lambda_rad_aksen) * math.tan(epsilon_rad)))
    y = math.degrees(math.atan(-math.cos(lambda_rad - math.radians(K)) * math.tan(math.radians(I))))
    
    # Heliographic latitude B0
    B0 = math.degrees(math.asin(math.sin(lambda_rad - math.radians(K)) * math.sin(math.radians(I))))
    
    # Heliographic longitude L0
    nu = math.degrees(math.atan(math.tan(lambda_rad - math.radians(K)) * math.cos(math.radians(I))))
    L0 = (nu - Tetha) % 360
    
    # Position angle P
    P = x + y
    
    return B0, L0, P
