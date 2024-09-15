import streamlit as st
import utilities as utils
from utilities import w, h
import random

def wave_settings(C, OTHER_CONFIG, sp):
    with st.sidebar.expander("Layout Settings"):
        C["NUMBER_OF_WAVES"] = st.number_input("Number of Waves", min_value=1, max_value=1000, value=sp.get("NUMBER_OF_WAVES", 30), step=1, help="NUMBER_OF_WAVES")
        C["HORIZON_Y"] = st.number_input("Horizon Position", value=sp.get("HORIZON_Y", 15.0), step=1.0, help="HORIZON_Y")
        C["LAST_WAVE_Y"] = st.number_input("Last Wave", value=sp.get("LAST_WAVE_Y", 80.0), step=1.0, help="LAST_WAVE_Y")
        spacing_types = ["Linear", "Logarithmic"]
        C["SPACING_TYPE"] = st.selectbox("Spacing Type", spacing_types, index=spacing_types.index(sp.get("SPACING_TYPE", "Logarithmic")), help="SPACING_TYPE")
        C["WAVE_SPACING_RANDOMNESS"] = st.number_input("Wave Spacing Randomness", value=sp.get("WAVE_SPACING_RANDOMNESS", 0.0), min_value=0.0, max_value=1.0, step=0.05, help="WAVE_SPACING_RANDOMNESS")
    
    with st.sidebar.expander("Wave Settings"):
        C["NUMBER_OF_WAVE_POINTS_MIN"] = st.number_input("Min number of Wave Points", min_value=1, value=sp.get("NUMBER_OF_WAVE_POINTS_MIN", 2), step=1, help="NUMBER_OF_WAVE_POINTS_MIN")
        C["NUMBER_OF_WAVE_POINTS_MAX"] = st.number_input("Max number of Wave Points", min_value=1, value=sp.get("NUMBER_OF_WAVE_POINTS_MAX", 6), step=1, help="NUMBER_OF_WAVE_POINTS_MAX")
        C["WAVE_HEIGHT_FACTOR"] = st.number_input("Wave Height Indicator", value=sp.get("WAVE_HEIGHT_FACTOR", 15.0), step=1.0, help="WAVE_HEIGHT_FACTOR")
        C["FIRST_POINT_START_MAX"] = st.number_input("Max First Point Start", value=sp.get("FIRST_POINT_START_MAX", 0.0), step=1.0, help="FIRST_POINT_START_MAX")
        C["WAVE_POINT_SPACING_RANDOMNESS"] = st.number_input("Point Spacing Randomness", value=sp.get("WAVE_POINT_SPACING_RANDOMNESS", 0.0), min_value=0.0, max_value=1.0, step=0.05, help="WAVE_POINT_SPACING_RANDOMNESS")
        C["CONTROL_ARM_LENGTH"] = st.number_input("Control Arm Length (Relative)", value=sp.get("CONTROL_ARM_LENGTH", 0.2), min_value=0.0, step=0.01, help="CONTROL_ARM_LENGTH")
        
    with st.sidebar.expander("Color Settings"):
        C["SINGLE_COLOR"] = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", True), help="SINGLE_COLOR")
        if (C["SINGLE_COLOR"]):
            C["FILL_COLOR"] = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#FF4800"), help="FILL_COLOR")
        
        C["HAS_NOISE"] = st.checkbox("Has Noise", value=sp.get("HAS_NOISE", True), help="HAS_NOISE")
        C["ADD_FADING_EFFECT"] = st.checkbox("Add Fade", value=sp.get("ADD_FADING_EFFECT", True), help="ADD_FADING_EFFECT")
        if C["ADD_FADING_EFFECT"]:
            C["INVERT_FADE"] = st.checkbox("Invert Fade", value=sp.get("INVERT_FADE", False), help="INVERT_FADE")
            C["MIN_LUMINOSITY"] = st.number_input("Minimum Luminosity", min_value=0.0, max_value=1.0, value=sp.get("MIN_LUMINOSITY", 1.0), step=0.1, help="MIN_LUMINOSITY")
            C["MAX_LUMINOSITY"] = st.number_input("Maximum Luminosity", min_value=0.0, max_value=1.0, value=sp.get("MAX_LUMINOSITY", 0.2), step=0.1, help="MAX_LUMINOSITY")

    with st.sidebar.expander("Shadow Settings"):
        C["HAS_SHADOW"] = st.checkbox("Add Wave Shadow", value=sp.get("HAS_SHADOW", False), help="HAS_SHADOW")
        if C["HAS_SHADOW"]:
            if C["SINGLE_COLOR"]:
                C["SHADOW_COLOR_COMPLEMENTARY"] = st.checkbox("Complementary Color", value=sp.get("SHADOW_COLOR_COMPLEMENTARY", False), help="SHADOW_COLOR_COMPLEMENTARY")
            C["SHADOW_COLOR"] = st.color_picker("Shadow Color", utils.complementary_color(C["FILL_COLOR"]) if C["SINGLE_COLOR"] and C["SHADOW_COLOR_COMPLEMENTARY"] else sp.get("SHADOW_COLOR", "#000"), help="SHADOW_COLOR")
            C["SHADOW_BLURRINESS"] = st.number_input("Shadow Blurriness", value=sp.get("SHADOW_BLURRINESS", 20), min_value=0, step=1, help="SHADOW_BLURRINESS")
            C["SHADOW_OPACITY"] = st.number_input("Shadow Opacity", min_value=0.0, max_value=1.0, value=sp.get("SHADOW_OPACITY", 0.2), step=0.05, help="SHADOW_OPACITY")
            C["SHADOW_OFFSET_Y"] = st.number_input("Shadow Offset (relative, negative)", value=sp.get("SHADOW_OFFSET_Y", 2.0), step=1.0, help="SHADOW_OFFSET_Y")
    
    with st.sidebar.expander("Wave Animation Settings"):
        C["ANIMATION_STRENGTH"] = st.number_input("Animation Strength", value=sp.get("SPLOTCH_ANIMATION_STRENGTH", 0.15), min_value=0.0, step=0.05, help="SPLOTCH_ANIMATION_STRENGTH")

def generate_waves(dwg, C, OTHER_CONFIG):
    regular_wave_horizons = utils.linear_interpolation(C["HORIZON_Y"], C["LAST_WAVE_Y"], C["NUMBER_OF_WAVES"]) if C["SPACING_TYPE"] == "Linear" else utils.log_interpolation(C["HORIZON_Y"], C["LAST_WAVE_Y"], C["NUMBER_OF_WAVES"])
    
    # Define the shadow filter using feGaussianBlur and feOffset
    if C["HAS_SHADOW"]: 
        filter_element = dwg.filter(id="shadow", x="-50%", y="-50%", width="200%", height="200%")
        filter_element.feGaussianBlur(in_="SourceAlpha", stdDeviation=C["SHADOW_BLURRINESS"], result="blur")
        filter_element.feOffset(in_="blur", dx=0, dy=-h(C["SHADOW_OFFSET_Y"], C["H"]), result="offsetBlur")
        filter_element.feFlood(flood_color=C["SHADOW_COLOR"], flood_opacity=C["SHADOW_OPACITY"], result="floodShadow")  # Set a less intense shadow color
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
        horizon = regular_horizon + C["WAVE_SPACING_RANDOMNESS"] * min_horizon_dist * (random.random() - 0.5)
        start_point = (0, 100)
        wave_points = []
        number_of_wave_points = random.choice(range(C["NUMBER_OF_WAVE_POINTS_MIN"], C["NUMBER_OF_WAVE_POINTS_MAX"] + 1))
        
        first_wave_point_x = C["FIRST_POINT_START_MAX"] * random.random()
        # TODO: To do the animation properly, I'd likely want to generate a separate set of points.
        # That would then also change the calculation of the control points for the to_path below...
        for j in range(number_of_wave_points):
            regular_x = first_wave_point_x + (j + 1) * (100 - first_wave_point_x)/(number_of_wave_points + 1)
            regular_y = horizon
            x = regular_x + (100/number_of_wave_points) * C["WAVE_POINT_SPACING_RANDOMNESS"] * (random.random() - 0.5)
            y = regular_y + C["WAVE_HEIGHT_FACTOR"] * (random.random() - 0.5)
            
            wave_points.append((x, y))
            
        end_point = (100, 100)
        
        # generate the path TODO: Make into a standalone function
        from_path_data = f"M {w(start_point[0], C['W'])},{h(start_point[1], C["H"])}\n"
        from_path_data += f"L {w(start_point[0], C['W'])},{h(horizon, C["H"])}\n"
        to_path_data = from_path_data # start off with the same to_path
        
        for k, (p_x, p_y) in enumerate(wave_points):
            p_prev = (start_point[0], horizon) if k == 0 else wave_points[k-1]
            p_next = (end_point[0], horizon) if k == len(wave_points) - 1 else wave_points[k+1]
            control_x, control_y = utils.calculate_control(p_prev, (p_x, p_y), p_next, C["CONTROL_ARM_LENGTH"])
            from_path_data += f"S {w(control_x, C['W'])},{h(control_y, C["H"])} {w(p_x, C['W'])},{h(p_y, C["H"])}\n"
            to_path_data += f"S {w(control_x, C['W'])},{h(control_y, C["H"])} {w(p_x, C['W'])},{h((1 + C["ANIMATION_STRENGTH"] * (random.random() - 0.5)) * p_y, C["H"])}\n"
        
        # construct the the final leg
        control_x = wave_points[-1][0] + 0.5 * (end_point[0] - wave_points[-1][0])
        control_y = wave_points[-1][1] + 0.5 * (horizon - wave_points[-1][1])
        
        from_path_data += f"S {w(control_x, C['W'])},{h(control_y, C["H"])} {w(end_point[0], C['W'])},{h(horizon, C["H"])}\n"
        from_path_data += f"L {w(end_point[0], C['W'])},{h(end_point[1], C["H"])}\n"
        from_path_data += f"Z"
        
        # add the same endpoint logic to the to_path
        to_path_data += f"S {w(control_x, C['W'])},{h(control_y, C["H"])} {w(end_point[0], C['W'])},{h(horizon, C["H"])}\n"
        to_path_data += f"L {w(end_point[0], C['W'])},{h(end_point[1], C["H"])}\n"
        to_path_data += f"Z"
        
        from_path = from_path_data.replace('\n', ' ').strip()
        to_path = to_path_data.replace('\n', ' ').strip()
        
        # color stuffs...
        fill_color = C["FILL_COLOR"] if C["SINGLE_COLOR"] else random.choice(OTHER_CONFIG["COLORS"])
        if C["ADD_FADING_EFFECT"]:
            luminosity = C["MAX_LUMINOSITY"] - i * (C["MAX_LUMINOSITY"] - C["MIN_LUMINOSITY"])/C["NUMBER_OF_WAVES"]
            fill_color = utils.hex_to_rgb_with_luminosity(fill_color, luminosity if C["INVERT_FADE"] else 1 - luminosity) 
        
        wave = dwg.path(d=from_path, fill=fill_color)
        if C["HAS_SHADOW"]: wave_shadow = dwg.path(d=from_path, fill="blue", filter="url(#shadow)")
        
        # NOTE: The animation only works if x and y coordinates in the path are comma separated, and points are space separated
        # i.e. 'S 50 50, 20 20' doesn't work, but 'S 50,50 20,20' does... 
        if C["IS_ANIMATED"]:
            animation = dwg.animate(
                attributeName="d",
                dur=f"{C['ANIMATION_DURATION']}s",
                repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
                values=[from_path, to_path, from_path],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            
            wave.add(animation)
            if C["HAS_SHADOW"]: wave_shadow.add(animation)
        
        if C["HAS_SHADOW"]: dwg.add(wave_shadow)
        dwg.add(wave)
        
    if C["HAS_NOISE"]:
        rect = dwg.rect(insert=(0, 0), size=(C['W'], C["H"]), fill=random.choice(OTHER_CONFIG["COLORS"]), fill_opacity=0.2, filter="url(#noiseFilter)")
        dwg.add(rect)
    
    return dwg
