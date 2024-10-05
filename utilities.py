import numpy as np
import math
import matplotlib.colors as mcolors
import colorsys

def w(p, abs):
    return p/100 * abs

def h(p, abs):
    return p/100 * abs

# Function to convert hex to HSL with a custom lightness value
def hex_to_rgb_with_luminosity(hex_color, luminosity):
    # Convert hex to RGB (0-1 range) using mcolors
    rgb = mcolors.to_rgb(hex_color)
    
    # Convert RGB to HLS using colorsys
    h, l, s = colorsys.rgb_to_hls(*rgb)
    
    # Use the provided luminosity value (0-1 range) and clamp between 0 and 1
    l = max(0, min(1, luminosity))
    
    # Convert back to RGB from HLS
    adjusted_rgb = colorsys.hls_to_rgb(h, l, s)
    
    # Return the adjusted RGB value as a hex string
    return mcolors.to_hex(adjusted_rgb)

def complementary_color(hex_color):
    # Convert the hex color to an RGB tuple
    rgb = mcolors.to_rgb(hex_color)
    
    # Find the complementary color by subtracting each channel from 1 (since mcolors uses values between 0 and 1)
    comp_rgb = [(1.0 - channel) for channel in rgb]
    
    # Convert the complementary RGB back to hex
    return mcolors.to_hex(comp_rgb)

def calculate_control(prev, p, next, z=0.5):
    # Unpack the points
    x_prev, y_prev = prev
    x_p, y_p = p
    x_next, y_next = next
    
    # Step 1: Find the direction vector from the previous to the next point
    direction_x = x_next - x_prev
    direction_y = y_next - y_prev
    
    # Step 2: Normalize the direction vector and scale it by z times the distance ab
    scaled_vector_x = z * direction_x
    scaled_vector_y = z * direction_y
    
    # Step 3: Translate the vector to the point b to get the final point c
    x_c = x_p - scaled_vector_x
    y_c = y_p - scaled_vector_y
    
    return (x_c, y_c)

def linear_interpolation(start, end, n_steps):
    try:
        step_size = (end - start) / (n_steps - 1)  # Calculate the step size
        return [start + i * step_size for i in range(n_steps)]
    except ZeroDivisionError:
        return [start]

def log_interpolation(start, end, n_steps):
    # Ensure the minimum and maximum are positive (since log doesn't work with non-positive numbers)
    if start <= 0 or end <= 0:
        raise ValueError("Both start and end must be greater than 0.")
    
    # Generate n logarithmically spaced points between log(start) and log(end)
    log_min = np.log(start)
    log_max = np.log(end)
    
    # Linearly interpolate between the logarithms
    log_steps = np.linspace(log_min, log_max, n_steps)
    
    # Exponentiate to get the original values back
    steps = np.exp(log_steps)
    
    return steps

def generate_regular_points(center, number_of_points, radius=1):
    """
    Generate points evenly spaced around a center point.

    Args:
        center (tuple): A tuple (c_x, c_y) representing the center point.
        number_of_points (int): The number of points to generate.
        radius (float): The radius of the circle around the center. Default is 1.

    Returns:
        list: A list of tuples representing the coordinates of the points.
    """
    c_x, c_y = center
    points = []
    
    for i in range(number_of_points):
        angle = 2 * math.pi * i / number_of_points
        x = c_x + radius * math.cos(angle)
        y = c_y + radius * math.sin(angle)
        points.append((x, y))
    
    return points

def translate_point_radially(p, center, strength):
    """
    Translates point p radially outward from center by a factor of strength.

    Args:
        p (tuple): A tuple (p_x, p_y) representing the point to translate.
        center (tuple): A tuple (center_x, center_y) representing the center point.
        strength (float): The factor by which to scale the distance between p and center.

    Returns:
        tuple: A tuple (new_x, new_y) representing the new coordinates of the translated point.
    """
    p_x, p_y = p
    center_x, center_y = center
    
    # Calculate the vector from the center to the point
    delta_x = p_x - center_x
    delta_y = p_y - center_y
    
    # Calculate the distance between the point and the center
    distance = math.sqrt(delta_x**2 + delta_y**2)
    
    # Calculate the new distance based on the strength factor
    new_distance = distance * (1 + strength)
    
    # Calculate the angle of the vector
    angle = math.atan2(delta_y, delta_x)
    
    # Calculate new point coordinates by moving along the angle with the new distance
    new_x = center_x + new_distance * math.cos(angle)
    new_y = center_y + new_distance * math.sin(angle)
    
    return new_x, new_y

def translate_point_tangentially(p, center, distance):
    """
    Translates point p tangentially around center by a given distance.

    Args:
        p (tuple): A tuple (p_x, p_y) representing the point to translate.
        center (tuple): A tuple (center_x, center_y) representing the center point.
        distance (float): The distance to move the point tangentially (positive for counter-clockwise, negative for clockwise).

    Returns:
        tuple: A tuple (new_x, new_y) representing the new coordinates of the translated point.
    """
    p_x, p_y = p
    center_x, center_y = center
    
    # Calculate the vector from the center to the point
    delta_x = p_x - center_x
    delta_y = p_y - center_y
    
    # Calculate the current distance from the center (radius)
    radius = math.sqrt(delta_x**2 + delta_y**2)
    
    # Calculate the current angle of the point relative to the center
    current_angle = math.atan2(delta_y, delta_x)
    
    # Calculate the angular distance to move tangentially (arc length / radius)
    angular_distance = distance / radius
    
    # Calculate the new angle
    new_angle = current_angle + angular_distance
    
    # Calculate new point coordinates by moving along the circular path
    new_x = center_x + radius * math.cos(new_angle)
    new_y = center_y + radius * math.sin(new_angle)
    
    return new_x, new_y
