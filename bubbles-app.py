import streamlit as st
import svgwrite
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import colorsys
import tempfile
import numpy as np

################# UTILITIES #################
def w(p):
    return p/100 * WIDTH

def h(p):
    return p/100 * HEIGHT

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
    step_size = (end - start) / (n_steps - 1)  # Calculate the step size
    return [start + i * step_size for i in range(n_steps)]

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

################# GENERATION FUNCTIONS #################
# NOTE: scope of variables in here is pretty horribly done...
def generate_bubbles(dwg):
    # Define some filters
    distort_filter = dwg.defs.add(dwg.filter(id='distortFilter'))
    distort_filter.feTurbulence(type="fractalNoise", baseFrequency=0.05, numOctaves=10, result="turbulence")
    distort_filter.feDisplacementMap(in2="turbulence", in_="SourceGraphic", scale=100)

    noise_filter = dwg.defs.add(dwg.filter(id='noiseFilter'))
    noise_filter.feTurbulence(type="fractalNoise", baseFrequency=0.8, numOctaves=10, result="turbulence")
    noise_filter.feComposite(operator="in", in_="turbulence", in2="SourceAlpha", result="composite")
    noise_filter.feColorMatrix(in_="composite", type="luminanceToAlpha")
    noise_filter.feBlend(in_="SourceGraphic", in2="composite", mode="multiply")

    # Generate the bubbles
    for i in range(NUMBER_OF_BUBBLES):
        # Define the center & size of the circle
        x = 120 * random.random() - 10
        y = 120 * random.random() - 10
        r = (MAX_RADIUS - MIN_RADIUS) * random.random() + MIN_RADIUS
        base_color = FILL_COLOR if SINGLE_COLOR else random.choice(COLORS)
        
        # Define a linear gradient
        gradient_id = f"gradient-{i}"
        linear_gradient = dwg.linearGradient((0, 0), (1, 1), id=gradient_id)
        linear_gradient.add_stop_color(0, base_color, 1)
        linear_gradient.add_stop_color(1, base_color, 0.1)
        dwg.defs.add(linear_gradient)
        
        fill_color = f'url(#{gradient_id})' if HAS_GRADIENT else base_color
        
        # Define the circle itself
        circle = dwg.circle(center=(w(x), h(y)), r=w(r), fill=fill_color)
        if IS_DISTORTED:
            circle.attribs['filter'] = "url(#distortFilter)"
        
        if IS_ANIMATED:
            distance_x = (MAX_X_DISTANCE_PERC - MIN_X_DISTANCE_PERC) * random.random() + MIN_X_DISTANCE_PERC
            animate_x = dwg.animate(
                attributeName="cx",
                dur=ANIMATION_DURATION,
                repeatCount="indefinite" if REPEAT_ANIMATION else 1,
                values=[w(x), w(x) + w(distance_x), w(x)],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            
            distance_y = (MAX_Y_DISTANCE_PERC - MIN_Y_DISTANCE_PERC) * random.random() + MIN_X_DISTANCE_PERC
            animate_y = dwg.animate(
                attributeName="cy",
                dur=ANIMATION_DURATION,
                repeatCount="indefinite" if REPEAT_ANIMATION else 1,
                values=[h(y), h(y) - h(distance_y), h(y)],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            
            circle.add(animate_x)
            circle.add(animate_y)
        
        dwg.add(circle)

    # Add noise if required
    if HAS_NOISE:
        rect = dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=random.choice(COLORS), fill_opacity=0.2, filter="url(#noiseFilter)")
        dwg.add(rect)
        
    return dwg

def generate_filters(dwg):
    ######## filter definitions ########
    ### textured filter ###
    filter_textured = dwg.defs.add(dwg.filter(id='filterTextured'))
    filter_textured.feTurbulence(type=TEXTURE_TYPE, baseFrequency=BASE_FREQUENCY, numOctaves=NUM_OCTAVES, result="turbulence")
    point_light = filter_textured.feDiffuseLighting(
        in_="turbulence",
        surfaceScale=SURFACE_SCALE, 
        diffuseConstant=DIFFUSE_CONSTANT,
        lighting_color=LIGHTING_COLOR_INPUT.strip().lower(),
        result="highlight"
    ).fePointLight(source=(w(MIN_X_PERC), h(MIN_Y_PERC), MIN_Z))
    filter_textured.feComposite(operator="in", in_="highlight", in2="SourceAlpha", result="highlightApplied")
    filter_textured.feBlend(in_="SourceGraphic", in2="highlightApplied", mode="multiply")

    if IS_ANIMATED:
        animation_x = dwg.animate(
            attributeName="x",
            dur=ANIMATION_DURATION,
            repeatCount="indefinite" if REPEAT_ANIMATION else 1,
            values=[w(MIN_X_PERC), w(MAX_X_PERC), w(MIN_X_PERC)],  # cy values at keyframes as a list of strings
            keyTimes="0;0.5;1",  # Keyframe times as a space-separated string
            calcMode="spline",  # Use spline mode for smooth easing
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1"  # Control points for easing                
        )
        
        animation_y = dwg.animate(
            attributeName="y",
            dur=ANIMATION_DURATION,
            repeatCount="indefinite" if REPEAT_ANIMATION else 1,
            values=[h(MIN_Y_PERC), h(MAX_Y_PERC), h(MIN_Y_PERC)],  # cy values at keyframes as a list of strings
            keyTimes="0;0.5;1",  # Keyframe times as a space-separated string
            calcMode="spline",  # Use spline mode for smooth easing
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1"  # Control points for easing
                
        )

        animation_z = dwg.animate(
            attributeName="z",
            dur=ANIMATION_DURATION,
            repeatCount="indefinite" if REPEAT_ANIMATION else 1,
            values=[MIN_Z, MAX_Z, MIN_Z, MAX_Z, MIN_Z],  # cy values at keyframes as a list of strings
            keyTimes="0;0.25;0.5;0.75;1",  # Keyframe times as a space-separated string
            calcMode="spline",  # Use spline mode for smooth easing
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1"  # Control points for easing 
        )

        point_light.add(animation_x)
        point_light.add(animation_y)
        point_light.add(animation_z)
        
        # it looks like the light animation doesn't properly work unless there is an actual shape that's also being animated.
        # thus, just adding a random shape and animation...
        animation_enabler = dwg.animate(attributeName="cx", from_=w(40), to=w(60), dur=ANIMATION_DURATION, repeatCount="indefinite" if REPEAT_ANIMATION else 1)
        circle_enabler = dwg.circle(center=(w(50), h(50)), r=0, fill="black")
        circle_enabler.add(animation_enabler)
        dwg.add(circle_enabler)

    ######## draw shapes ########
    fill_color = FILL_COLOR if SINGLE_COLOR else random.choice(COLORS)
    shape = None
    if SHAPE == "Circle": 
        shape = dwg.circle(center=(w(50), h(50)), r=w(SHAPE_DIMENSIONS/2), fill=fill_color, filter=f"url(#filterTextured)")
    elif SHAPE == "Square":
        shape = dwg.rect(insert=(w((100-SHAPE_DIMENSIONS)/2), h((100-SHAPE_DIMENSIONS)/2)), size=(w(SHAPE_DIMENSIONS), w(SHAPE_DIMENSIONS)), fill=fill_color, filter=f"url(#filterTextured)")
        
    dwg.add(shape)
    
    return dwg
 
def generate_waves(dwg):
    regular_wave_horizons = linear_interpolation(HORIZON_Y, LAST_WAVE_Y, NUMBER_OF_WAVES) if SPACING_TYPE == "Linear" else log_interpolation(HORIZON_Y, LAST_WAVE_Y, NUMBER_OF_WAVES)
    
    # Define the shadow filter using feGaussianBlur and feOffset
    if HAS_SHADOW: 
        filter_element = dwg.filter(id="shadow")
        filter_element.feGaussianBlur(in_="SourceAlpha", stdDeviation=SHADOW_BLURRINESS, result="blur")
        filter_element.feOffset(in_="blur", dx=0, dy=-h(SHADOW_OFFSET_Y), result="offsetBlur")
        filter_element.feFlood(flood_color=SHADOW_COLOR, flood_opacity=SHADOW_OPACITY, result="floodShadow")  # Set a less intense shadow color
        filter_element.feComposite(in_="floodShadow", in2="offsetBlur", operator="in", result="compositeShadow")
    
        dwg.defs.add(filter_element)

    # create points
    for i, regular_horizon in enumerate(regular_wave_horizons):
        # calculate the minimum distance between the current horizon and the previous and next ones...
        # only this complicated because of non-linear steps...
        min_horizon_dist = 0
        if i == 0 and len(regular_wave_horizons) > 1: min_horizon_dist = abs(regular_wave_horizons[i+1] - regular_horizon) 
        elif i == len(regular_wave_horizons) - 1: min_horizon_dist = abs(regular_horizon - regular_wave_horizons[i-1])
        else: min_horizon_dist = min(abs(regular_wave_horizons[i+1] - regular_horizon), abs(regular_horizon - regular_wave_horizons[i-1]))
        
        # define the currrent horizon
        horizon = regular_horizon + WAVE_SPACING_RANDOMNESS * min_horizon_dist * (random.random() - 0.5)
        start_point = (0, 100)
        wave_points = []
        number_of_wave_points = random.choice(range(NUMBER_OF_WAVE_POINTS_MIN, NUMBER_OF_WAVE_POINTS_MAX + 1))
        
        first_wave_point_x = FIRST_POINT_START_MAX * random.random()
        # TODO: To do the animation properly, I'd likely want to generate a separate set of points.
        # That would then also change the calculation of the control points for the to_path below...
        for j in range(number_of_wave_points):
            regular_x = first_wave_point_x + (j + 1) * (100 - first_wave_point_x)/(number_of_wave_points + 1)
            regular_y = horizon
            x = regular_x + (100/number_of_wave_points) * WAVE_POINT_SPACING_RANDOMNESS * (random.random() - 0.5)
            y = regular_y + WAVE_HEIGHT_FACTOR * (random.random() - 0.5)
            
            wave_points.append((x, y))
            
        end_point = (100, 100)
        
        # generate the path TODO: Make into a standalone function
        from_path_data = f"M {w(start_point[0])},{h((start_point[1]))}\n"
        from_path_data += f"L {w(start_point[0])},{h(horizon)}\n"
        to_path_data = from_path_data # start off with the same to_path
        
        for k, (p_x, p_y) in enumerate(wave_points):
            p_prev = (start_point[0], horizon) if k == 0 else wave_points[k-1]
            p_next = (end_point[0], horizon) if k == len(wave_points) - 1 else wave_points[k+1]
            control_x, control_y = calculate_control(p_prev, (p_x, p_y), p_next, CONTROL_ARM_LENGTH)
            from_path_data += f"S {w(control_x)},{h(control_y)} {w(p_x)},{h(p_y)}\n"
            to_path_data += f"S {w(control_x)},{h(control_y)} {w(p_x)},{h((1 + ANIMATION_STRENGTH * (random.random() - 0.5)) * p_y)}\n"
        
        # construct the the final leg
        control_x = wave_points[-1][0] + 0.5 * (end_point[0] - wave_points[-1][0])
        control_y = wave_points[-1][1] + 0.5 * (horizon - wave_points[-1][1])
        
        from_path_data += f"S {w(control_x)},{h(control_y)} {w(end_point[0])},{h(horizon)}\n"
        from_path_data += f"L {w(end_point[0])},{h(end_point[1])}\n"
        from_path_data += f"Z"
        
        # add the same endpoint logic to the to_path
        to_path_data += f"S {w(control_x)},{h(control_y)} {w(end_point[0])},{h(horizon)}\n"
        to_path_data += f"L {w(end_point[0])},{h(end_point[1])}\n"
        to_path_data += f"Z"
        
        from_path = from_path_data.replace('\n', ' ').strip()
        to_path = to_path_data.replace('\n', ' ').strip()
        
        # color stuffs...
        fill_color = FILL_COLOR if SINGLE_COLOR else random.choice(COLORS)
        if ADD_FADING_EFFECT:
            luminosity = MAX_LUMINOSITY - i * (MAX_LUMINOSITY - MIN_LUMINOSITY)/NUMBER_OF_WAVES
            fill_color = hex_to_rgb_with_luminosity(fill_color, luminosity if INVERT_FADE else 1 - luminosity) 
        
        wave = dwg.path(d=from_path, fill=fill_color)
        if HAS_SHADOW: wave_shadow = dwg.path(d=from_path, fill="blue", filter="url(#shadow)")
        
        # NOTE: The animation only works if x and y coordinates in the path are comma separated, and points are space separated
        # i.e. 'S 50 50, 20 20' doesn't work, but 'S 50,50 20,20' does... 
        if IS_ANIMATED:
            animation = dwg.animate(
                attributeName="d",
                dur=ANIMATION_DURATION,
                repeatCount="indefinite" if REPEAT_ANIMATION else 1,
                values=[from_path, to_path, from_path],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            
            wave.add(animation)
            if HAS_SHADOW: wave_shadow.add(animation)
        
        if HAS_SHADOW: dwg.add(wave_shadow)
        dwg.add(wave)
        
    if HAS_NOISE:
        rect = dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=random.choice(COLORS), fill_opacity=0.2, filter="url(#noiseFilter)")
        dwg.add(rect)
    
    return dwg

################# PRESET DEFINITION #################
# define some re-usable modular preset parts
preset_general_standard = {
    "WIDTH": 600,
    "HEIGHT": 900,
    "COLOR_SCHEME": "viridis",
    "HAS_BACKGROUND": True,
    "BACKGROUND_COLOR": "#fff",
}

preset_animation_standard = {
    "IS_ANIMATED": True,
    "REPEAT_ANIMATION": True,
    "ANIMATION_DURATION_INPUT": 5.0
}

preset_filters_standard = {
    "TEXTURE_TYPE": "fractalNoise",
    "BASE_FREQUENCY": 0.05,
    "NUM_OCTAVES": 20,
    "SINGLE_COLOR": True,
    "FILL_COLOR": "#D412BC",
    "SURFACE_SCALE": 20.0,
    "DIFFUSE_CONSTANT": 1.0,
    "LIGHTING_COLOR_INPUT": "#fff",
    "MIN_X_PERC": 10.0,
    "MAX_X_PERC": 90.0,
    "MIN_Y_PERC": 10.0,
    "MAX_Y_PERC": 10.0,
    "MIN_Z": 5.0,
    "MAX_Z": 500.0,
}

preset_bubbles_standard = {
    "NUMBER_OF_BUBBLES": 20,
    "IS_DISTORTED": True,
    "HAS_NOISE": True,
    "MIN_RADIUS": 5.0,
    "MAX_RADIUS": 30.0,
    "HAS_GRADIENT": True,
    "SINGLE_COLOR": False,
    "MIN_X_DISTANCE_PERC": 0.0,
    "MAX_X_DISTANCE_PERC": 0.0,
    "MIN_Y_DISTANCE_PERC": 4.0,
    "MAX_Y_DISTANCE_PERC": 20.0,
}

preset_waves_standard = {
    "NUMBER_OF_WAVES": 30,
    "HORIZON_Y": 15.0,
    "LAST_WAVE_Y": 80.0,
    "SPACING_TYPE": "Logarithmic",
    "WAVE_SPACING_RANDOMNESS": 0.0,
    "NUMBER_OF_WAVE_POINTS_MIN": 2,
    "NUMBER_OF_WAVE_POINTS_MAX": 6,
    "WAVE_HEIGHT_FACTOR": 15.0,
    "FIRST_POINT_START_MAX": 0.0,
    "WAVE_POINT_SPACING_RANDOMNESS": 0.0,
    "CONTROL_ARM_LENGTH": 0.2,
    "SINGLE_COLOR": True,
    "FILL_COLOR": "#FF4800",
    "HAS_NOISE": True,
    "ADD_FADING_EFFECT": True,
    "INVERT_FADE": False,
    "MIN_LUMINOSITY": 1.0,
    "MAX_LUMINOSITY": 0.2,
    "HAS_SHADOW": False,
    "SHADOW_COLOR_COMPLEMENTARY": False,
    "SHADOW_COLOR": "#000",
    "SHADOW_BLURRINESS": 20,
    "SHADOW_OPACITY": 0.2,
    "SHADOW_OFFSET_Y": 2.0,
    "ANIMATION_STRENGTH": 0.15,
}

# define presets
presets_bubbles = [
    { 
        "name": "Distorted Bubbles",
        "MODULE": "Bubbles"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_bubbles_standard |
    {
        "ANIMATION_DURATION_INPUT": 15.0
    },
    
    ###
    { 
        "name": "Many Large Bubbles",
        "MODULE": "Bubbles"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_bubbles_standard |
    { 
        "ANIMATION_DURATION_INPUT": 15.0,
        "NUMBER_OF_BUBBLES": 200,
        "IS_DISTORTED": False
    },
    
    ###
    { 
        "name": "Many Small Bubbles",
        "MODULE": "Bubbles"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_bubbles_standard |
    { 
        "ANIMATION_DURATION_INPUT": 20.0,
        "NUMBER_OF_BUBBLES": 1000,
        "IS_DISTORTED": False,
        "MIN_RADIUS": 0.2,
        "MAX_RADIUS": 2.0,
        "MIN_X_DISTANCE_PERC": 10.0,
        "MAX_X_DISTANCE_PERC": 20.0,
        "MIN_Y_DISTANCE_PERC": 10.0,
        "MAX_Y_DISTANCE_PERC": 20.0,
    },
    
    ###
    { 
        "name": "Agressive Bubbles",
        "MODULE": "Bubbles"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_bubbles_standard |
    {
        "BACKGROUND_COLOR": "#A41919",
        "ANIMATION_DURATION_INPUT": 20.0,
        "NUMBER_OF_BUBBLES": 1000,
        "IS_DISTORTED": False,
        "SINGLE_COLOR": True,
        "FILL_COLOR": "#3EFF00",
        "MIN_RADIUS": 0.2,
        "MAX_RADIUS": 2.0,
        "MIN_X_DISTANCE_PERC": 10.0,
        "MAX_X_DISTANCE_PERC": 20.0,
        "MIN_Y_DISTANCE_PERC": 10.0,
        "MAX_Y_DISTANCE_PERC": 20.0,
    },
]
        
presets_filters = [
    { 
        "name": "Standard Filters Piece",
        "MODULE": "Filters"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_filters_standard |
    { "HEIGHT": 600 },
    
    ###
    { 
        "name": "Turbulent Filter",
        "MODULE": "Filters"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_filters_standard |
    {
        "HEIGHT": 600,
        "TEXTURE_TYPE": "turbulence"
    },
    
    ###
    { 
        "name": "Square Filter",
        "MODULE": "Filters"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_filters_standard |
    {
        "HEIGHT": 600,
        "ANIMATION_DURATION_INPUT": 10.0,
        "SHAPE": "Square",
        "FILL_COLOR": "#83CAD0",
        "MIN_X_PERC": 10.0,
        "MAX_X_PERC": 90.0,
        "MIN_Y_PERC": 10.0,
        "MAX_Y_PERC": 90.0,
    }
]

presets_waves = [
    { 
        "name": "Monochrome Waves",
        "MODULE": "Waves"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_waves_standard,
    
    ###
    { 
        "name": "Many-Colored Waves",
        "MODULE": "Waves"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_waves_standard |
    {
        "SEED": 5,
        "HORIZON_Y": 15.0,
        "SINGLE_COLOR": False,
        "ADD_FADING_EFFECT": False,
        "ANIMATION_STRENGTH": 0.05,
        "HAS_SHADOW": True,
        "SHADOW_OPACITY": 0.1,        
    },
    
    ###
    { 
        "name": "Crazy Waves",
        "MODULE": "Waves"
    } | 
    preset_general_standard | 
    preset_animation_standard | 
    preset_waves_standard |
    {
        "HORIZON_Y": -15.0,
        "LAST_WAVE_Y": 120.0,
        "SINGLE_COLOR": False,
        "SPACING_TYPE": "Linear",
        "ADD_FADING_EFFECT": False,
        "ANIMATION_STRENGTH": 0.2,
        "HAS_SHADOW": True,
        "SHADOW_OPACITY": 0.1,
        "NUMBER_OF_WAVE_POINTS_MIN": 30,
        "NUMBER_OF_WAVE_POINTS_MAX": 50        
    }
]

presets = presets_bubbles + presets_filters + presets_waves

################# SIDEBAR CONFIGURATION #################
# Streamlit inputs for configuration
st.set_page_config(layout="wide")
preset_names = [preset["name"] for preset in presets]
PRESET = st.sidebar.selectbox("Choose Preset", preset_names)
sp = next(preset for preset in presets if preset["name"] == PRESET) # selected preset

st.sidebar.header("General Settings")
SEED = st.sidebar.number_input("Random Seed", value = sp.get("SEED", 3), help="SEED")
with st.sidebar.expander("General Settings"):
    WIDTH = st.number_input("Width", value=sp.get("WIDTH", 600), step=1, help="WIDTH")
    HEIGHT = st.number_input("Height", value=sp.get("HEIGHT", 600), step=1, help="HEIGHT")
    valid_color_schemes = [cmap_name for cmap_name in plt.colormaps() if hasattr(plt.get_cmap(cmap_name), 'colors')]
    COLOR_SCHEME = st.selectbox("Color Scheme", valid_color_schemes, index=valid_color_schemes.index(sp.get("COLOR_SCHEME", 600)), help="COLOR_SCHEME")
    COLORS = [mcolors.rgb2hex(color) for color in plt.get_cmap(COLOR_SCHEME).colors]
    HAS_BACKGROUND = st.checkbox("Add Background", value=sp.get("HAS_BACKGROUND", True), help="HAS_BACKGROUND")
    if HAS_BACKGROUND:
        BACKGROUND_COLOR = st.color_picker("Background Color", value=sp.get("BACKGROUND_COLOR", 600), help="BACKGROUND_COLOR")

with st.sidebar.expander("General Animation Settings"):
    IS_ANIMATED = st.checkbox("Animated", value=sp.get("IS_ANIMATED", True), help="IS_ANIMATED")
    REPEAT_ANIMATION = st.checkbox("Repeat Animation", value=sp.get("REPEAT_ANIMATION", True), help="REPEAT_ANIMATION")
    ANIMATION_DURATION_INPUT = st.number_input("Animation Duration in s", value=sp.get("ANIMATION_DURATION_INPUT", 5.0), step=0.1, help="ANIMATION_DURATION_INPUT")
    ANIMATION_DURATION = f"{ANIMATION_DURATION_INPUT}s"

st.sidebar.header("Type Settings")
modules = ["Bubbles", "Filters", "Waves", "Radial Waves", "Splotches"]
MODULE = st.sidebar.selectbox("Type of Graphic", modules, index=modules.index(sp.get("MODULE", "Waves")), help="MODULE")
if MODULE == "Bubbles":
    with st.sidebar.expander("General Bubble Settings"):
        NUMBER_OF_BUBBLES = st.number_input("Number of Bubbles", min_value=1, max_value=1000, value=sp.get("NUMBER_OF_BUBBLES", 20), step=1, help="NUMBER_OF_BUBBLES")
        IS_DISTORTED = st.checkbox("Distorted", value=sp.get("IS_DISTORTED", True), help="IS_DISTORTED")
        HAS_NOISE = st.checkbox("Has Noise", value=sp.get("HAS_NOISE", False), help="HAS_NOISE")
        
    with st.sidebar.expander("Bubble Settings"):
        MIN_RADIUS = st.number_input("Minimum Radius (relative to canvas width)", min_value=0.0, value=sp.get("MIN_RADIUS", 5.0), step=1.0, help="MIN_RADIUS")
        MAX_RADIUS = st.number_input("Maximum Radius (relative to canvas width)", min_value=1.0, value=sp.get("MAX_RADIUS", 30.0), step=1.0, help="MAX_RADIUS")
    
    with st.sidebar.expander("Color Settings"):
        HAS_GRADIENT = st.checkbox("Add Gradient", value=sp.get("HAS_GRADIENT", True), help="HAS_GRADIENT")
        SINGLE_COLOR = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", False), help="SINGLE_COLOR")
        if (SINGLE_COLOR):
            FILL_COLOR = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#D412BC"), help="FILL_COLOR")

    with st.sidebar.expander("Bubble Animation Settings"):        
        MIN_X_DISTANCE_PERC = st.number_input("Min x distance (relative to canvas width)", value=sp.get("MIN_X_DISTANCE_PERC", 0.0), step=1.0, help="MIN_X_DISTANCE_PERC")
        MAX_X_DISTANCE_PERC = st.number_input("Max x distance (relative to canvas width)", value=sp.get("MAX_X_DISTANCE_PERC", 0.0), step=1.0, help="MAX_X_DISTANCE_PERC")
        st.divider()
        MIN_Y_DISTANCE_PERC = st.number_input("Min y distance (relative to canvas height)", value=sp.get("MIN_Y_DISTANCE_PERC", 4.0), step=1.0, help="MIN_Y_DISTANCE_PERC")
        MAX_Y_DISTANCE_PERC = st.number_input("Max y distance (relative to canvas height)", value=sp.get("MAX_Y_DISTANCE_PERC", 20.0), step=1.0, help="MAX_Y_DISTANCE_PERC")

if MODULE == "Filters":
    with st.sidebar.expander("Shape Settings"):
        shapes = ["Square", "Circle"]
        SHAPE = st.selectbox("Shape", shapes, index=shapes.index(sp.get("SHAPE", "Circle")), help="SHAPE")
        SHAPE_DIMENSIONS = st.number_input("Shape Dimensions (relative to canvas width)", value=sp.get("SHAPE_DIMENSIONS", 80.0), step=1.0, help="SHAPE_DIMENSIONS")
        
    with st.sidebar.expander("Texture Settings"):
        texture_types = ["fractalNoise", "turbulence"]
        TEXTURE_TYPE = st.selectbox("Color Scheme", texture_types, index=texture_types.index(sp.get("TEXTURE_TYPE", "fractalNoise")), help="TEXTURE_TYPE")
        BASE_FREQUENCY = st.number_input("Base Frequency", value=sp.get("BASE_FREQUENCY", 0.05), step=0.1, help="BASE_FREQUENCY")
        NUM_OCTAVES = st.number_input("Number of Octaves", value=sp.get("NUM_OCTAVES", 20), step=1, help="NUM_OCTAVES")
    
    with st.sidebar.expander("Color Settings"):
        SINGLE_COLOR = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", True), help="SINGLE_COLOR")
        if (SINGLE_COLOR):
            FILL_COLOR = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#D412BC"), help="FILL_COLOR")
    
    with st.sidebar.expander("Lighting Settings"):
        SURFACE_SCALE = st.number_input("Surface Scale", value=sp.get("SURFACE_SCALE", 20.0), step=1.0, help="SURFACE_SCALE")
        DIFFUSE_CONSTANT = st.number_input("Diffuse Constant", value=sp.get("DIFFUSE_CONSTANT", 1.0), step=1.0, help="DIFFUSE_CONSTANT")
        LIGHTING_COLOR_INPUT = st.color_picker("Lighting Color", value=sp.get("LIGHTING_COLOR_INPUT", "#fff"), help="LIGHTING_COLOR_INPUT")
        
    with st.sidebar.expander("Filter Animation Settings"):        
        MIN_X_PERC = st.number_input("min x (relative to canvas width)", value=sp.get("MIN_X_PERC", 10.0), step=1.0, help="MIN_X_PERC")
        MAX_X_PERC = st.number_input("max x (relative to canvas width)", value=sp.get("MAX_X_PERC", 90.0), step=1.0, help="MAX_X_PERC")
        st.divider()
        MIN_Y_PERC = st.number_input("min y (relative to canvas width)", value=sp.get("MIN_Y_PERC", 10.0), step=1.0, help="MIN_Y_PERC")
        MAX_Y_PERC = st.number_input("max y (relative to canvas width)", value=sp.get("MAX_Y_PERC", 10.0), step=1.0, help="MAX_Y_PERC")
        st.divider()
        MIN_Z = st.number_input("min z", value=sp.get("MIN_Z", 5.0), step=1.0, help="MIN_Z")
        MAX_Z = st.number_input("max z", value=sp.get("MAX_Z", 500.0), step=1.0, help="MAX_Z")    

if MODULE == "Waves":
    with st.sidebar.expander("Layout Settings"):
        NUMBER_OF_WAVES = st.number_input("Number of Waves", min_value=1, max_value=1000, value=sp.get("NUMBER_OF_WAVES", 30), step=1, help="NUMBER_OF_WAVES")
        HORIZON_Y = st.number_input("Horizon Position", value=sp.get("HORIZON_Y", 15.0), step=1.0, help="HORIZON_Y")
        LAST_WAVE_Y = st.number_input("Last Wave", value=sp.get("LAST_WAVE_Y", 80.0), step=1.0, help="LAST_WAVE_Y")
        spacing_types = ["Linear", "Logarithmic"]
        SPACING_TYPE = st.selectbox("Spacing Type", spacing_types, index=spacing_types.index(sp.get("SPACING_TYPE", "Logarithmic")), help="SPACING_TYPE")
        WAVE_SPACING_RANDOMNESS = st.number_input("Wave Spacing Randomness", value=sp.get("WAVE_SPACING_RANDOMNESS", 0.0), min_value=0.0, max_value=1.0, step=0.05, help="WAVE_SPACING_RANDOMNESS")
    
    with st.sidebar.expander("Wave Settings"):
        NUMBER_OF_WAVE_POINTS_MIN = st.number_input("Min number of Wave Points", min_value=1, value=sp.get("NUMBER_OF_WAVE_POINTS_MIN", 2), step=1, help="NUMBER_OF_WAVE_POINTS_MIN")
        NUMBER_OF_WAVE_POINTS_MAX = st.number_input("Max number of Wave Points", min_value=1, value=sp.get("NUMBER_OF_WAVE_POINTS_MAX", 6), step=1, help="NUMBER_OF_WAVE_POINTS_MAX")
        WAVE_HEIGHT_FACTOR = st.number_input("Wave Height Indicator", value=sp.get("WAVE_HEIGHT_FACTOR", 15.0), step=1.0, help="WAVE_HEIGHT_FACTOR")
        FIRST_POINT_START_MAX = st.number_input("Max First Point Start", value=sp.get("FIRST_POINT_START_MAX", 0.0), step=1.0, help="FIRST_POINT_START_MAX")
        WAVE_POINT_SPACING_RANDOMNESS = st.number_input("Point Spacing Randomness", value=sp.get("WAVE_POINT_SPACING_RANDOMNESS", 0.0), min_value=0.0, max_value=1.0, step=0.05, help="WAVE_POINT_SPACING_RANDOMNESS")
        CONTROL_ARM_LENGTH = st.number_input("Control Arm Length (Relative)", value=sp.get("CONTROL_ARM_LENGTH", 0.2), min_value=0.0, step=0.01, help="CONTROL_ARM_LENGTH")
        
    with st.sidebar.expander("Color Settings"):
        SINGLE_COLOR = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", True), help="SINGLE_COLOR")
        if (SINGLE_COLOR):
            FILL_COLOR = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#FF4800"), help="FILL_COLOR")
        
        HAS_NOISE = st.checkbox("Has Noise", value=sp.get("HAS_NOISE", True), help="HAS_NOISE")
        ADD_FADING_EFFECT = st.checkbox("Add Fade", value=sp.get("ADD_FADING_EFFECT", True), help="ADD_FADING_EFFECT")
        if ADD_FADING_EFFECT:
            INVERT_FADE = st.checkbox("Invert Fade", value=sp.get("INVERT_FADE", False), help="INVERT_FADE")
            MIN_LUMINOSITY = st.number_input("Minimum Luminosity", min_value=0.0, max_value=1.0, value=sp.get("MIN_LUMINOSITY", 1.0), step=0.1, help="MIN_LUMINOSITY")
            MAX_LUMINOSITY = st.number_input("Maximum Luminosity", min_value=0.0, max_value=1.0, value=sp.get("MAX_LUMINOSITY", 0.2), step=0.1, help="MAX_LUMINOSITY")
            st.divider()
            
    with st.sidebar.expander("Shadow Settings"):
        HAS_SHADOW = st.checkbox("Add Wave Shadow", value=sp.get("HAS_SHADOW", False), help="HAS_SHADOW")
        if HAS_SHADOW:
            if SINGLE_COLOR:
                SHADOW_COLOR_COMPLEMENTARY = st.checkbox("Complementary Color", value=sp.get("SHADOW_COLOR_COMPLEMENTARY", False), help="SHADOW_COLOR_COMPLEMENTARY")
            SHADOW_COLOR = st.color_picker("Shadow Color", complementary_color(FILL_COLOR) if SINGLE_COLOR and SHADOW_COLOR_COMPLEMENTARY else sp.get("SHADOW_COLOR", "#000"), help="SHADOW_COLOR")
            SHADOW_BLURRINESS = st.number_input("Shadow Blurriness", value=sp.get("SHADOW_BLURRINESS", 20), min_value=0, step=1, help="SHADOW_BLURRINESS")
            SHADOW_OPACITY = st.number_input("Shadow Opacity", min_value=0.0, max_value=1.0, value=sp.get("SHADOW_OPACITY", 0.2), step=0.05, help="SHADOW_OPACITY")
            SHADOW_OFFSET_Y = st.number_input("Shadow Offset (relative, negative)", value=sp.get("SHADOW_OFFSET_Y", 2.0), step=1.0, help="SHADOW_OFFSET_Y")
    
    with st.sidebar.expander("Wave Animation Settings"):
        ANIMATION_STRENGTH = st.number_input("Animation Strength", value=sp.get("ANIMATION_STRENGTH", 0.15), min_value=0.0, step=0.05, help="ANIMATION_STRENGTH")

################# MAIN BODY #################
# set up the drawing environment
random.seed(SEED)
dwg = svgwrite.Drawing(size=(WIDTH, HEIGHT))

# add the default background 
if HAS_BACKGROUND:
    bg_rect = dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=BACKGROUND_COLOR.strip().lower())
    dwg.add(bg_rect)

if MODULE == "Bubbles": dwg = generate_bubbles(dwg)
if MODULE == "Filters": dwg = generate_filters(dwg)
if MODULE == "Waves": dwg = generate_waves(dwg)
if MODULE == "Radial Waves": st.info("Radial waves coming soon!") # TODO
if MODULE == "Splotches": st.info("Splotches coming soon!") # TODO

# Display output as an image
with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmpfile:
    dwg.saveas(tmpfile.name)
    st.image(tmpfile.name)
    
    
