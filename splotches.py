import streamlit as st
import utilities as utils
from utilities import w, h
import random

def splotch_settings(C, OTHER_CONFIG, sp):
    with st.sidebar.expander("Layout Settings"):
        C["NUMBER_OF_SPLOTCHES"] = st.number_input("Number of Splotches", min_value=1, max_value=1000, value=sp.get("NUMBER_OF_SPLOTCHES", 20), step=1, help="NUMBER_OF_SPLOTCHES")

    with st.sidebar.expander("Splotch Settings"):
        C["SPLOTCH_SIZE_MIN"] = st.number_input("Minimum Size (relative to canvas width)", min_value=0.0, value=sp.get("SPLOTCH_SIZE_MIN", 5.0), step=1.0, help="SPLOTCH_SIZE_MIN")
        C["SPLOTCH_SIZE_MAX"] = st.number_input("Maximum Size (relative to canvas width)", min_value=1.0, value=sp.get("SPLOTCH_SIZE_MAX", 30.0), step=1.0, help="SPLOTCH_SIZE_MAX")
        st.divider()
        C["NUMBER_OF_SPLOTCH_POINTS_MIN"] = st.number_input("Min number of Splotch Points", min_value=2, value=sp.get("NUMBER_OF_SPLOTCH_POINTS_MIN", 5), step=1, help="NUMBER_OF_SPLOTCH_POINTS_MIN")
        C["NUMBER_OF_SPLOTCH_POINTS_MAX"] = st.number_input("Max number of Splotch Points", min_value=2, value=sp.get("NUMBER_OF_SPLOTCH_POINTS_MAX", 10), step=1, help="NUMBER_OF_SPLOTCH_POINTS_MAX")
        st.divider()
        C["SPLOTCH_POINT_SPACING_RANDOMNESS"] = st.number_input("Splotch Point Spacing Randomness", min_value=0.0, value=sp.get("SPLOTCH_POINT_SPACING_RANDOMNESS", 1.0), step=0.5, help="SPLOTCH_POINT_SPACING_RANDOMNESS")
        C["SPLOTCH_POINT_RADIAL_RANDOMNESS"] = st.number_input("Splotch Point Radial Randomness", value=sp.get("SPLOTCH_POINT_RADIAL_RANDOMNESS", 5.0), step=0.1, help="SPLOTCH_POINT_RADIAL_RANDOMNESS")
        C["CONTROL_ARM_LENGTH"] = st.number_input("Control Arm Length (Relative)", value=sp.get("CONTROL_ARM_LENGTH", 0.2), min_value=0.0, step=0.01, help="CONTROL_ARM_LENGTH")
    
    with st.sidebar.expander("Color Settings"):
        C["SINGLE_COLOR"] = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", True), help="SINGLE_COLOR")
        if (C["SINGLE_COLOR"]):
            C["FILL_COLOR"] = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#FF4800"), help="FILL_COLOR")
        
        C["HAS_NOISE"] = st.checkbox("Has Noise", value=sp.get("HAS_NOISE", True), help="HAS_NOISE")
    
    with st.sidebar.expander("Shadow Settings"):
        C["HAS_SHADOW"] = st.checkbox("Add Splotch Shadow", value=sp.get("HAS_SHADOW", False), help="HAS_SHADOW")
        if C["HAS_SHADOW"]:
            if C["SINGLE_COLOR"]:
                C["SHADOW_COLOR_COMPLEMENTARY"] = st.checkbox("Complementary Color", value=sp.get("SHADOW_COLOR_COMPLEMENTARY", False), help="SHADOW_COLOR_COMPLEMENTARY")
            C["SHADOW_COLOR"] = st.color_picker("Shadow Color", utils.complementary_color(C["FILL_COLOR"]) if C["SINGLE_COLOR"] and C["SHADOW_COLOR_COMPLEMENTARY"] else sp.get("SHADOW_COLOR", "#000"), help="SHADOW_COLOR")
            C["SHADOW_BLURRINESS"] = st.number_input("Shadow Blurriness", value=sp.get("SHADOW_BLURRINESS", 20), min_value=0, step=1, help="SHADOW_BLURRINESS")
            C["SHADOW_OPACITY"] = st.number_input("Shadow Opacity", min_value=0.0, max_value=1.0, value=sp.get("SHADOW_OPACITY", 0.2), step=0.05, help="SHADOW_OPACITY")
            C['SHADOW_OFFSET_X'] = st.number_input("Shadow Offset X (relative to canvas width)", value=sp.get("SHADOW_OFFSET_X", 2.0), step=1.0, help="SHADOW_OFFSET_X")
            C['SHADOW_OFFSET_Y'] = st.number_input("Shadow Offset Y (relative to canvas width)", value=sp.get("SHADOW_OFFSET_Y", 2.0), step=1.0, help="SHADOW_OFFSET_Y")
    
    with st.sidebar.expander("Splotches Animation Settings"):
        C["SPLOTCH_POINTS_ANIMATED"] = st.checkbox("Animate Splotch Points", value=sp.get("SPLOTCH_POINTS_ANIMATED", True), help="SPLOTCH_POINTS_ANIMATED")
        if C["SPLOTCH_POINTS_ANIMATED"]:
            C['SPLOTCH_POINT_ANIMATION_DURATION'] = st.number_input("Splotch Point Animation Duration", value=sp.get("SPLOTCH_POINT_ANIMATION_DURATION", 5.0), min_value=0.0, step=1.0, help="SPLOTCH_POINT_ANIMATION_DURATION")
            C["SPLOTCH_POINT_ANIMATION_STRENGTH"] = st.number_input("Animation Strength", value=sp.get("SPLOTCH_POINT_ANIMATION_STRENGTH", 0.25), min_value=0.0, step=0.05, help="SPLOTCH_POINT_ANIMATION_STRENGTH")
            st.divider()
            
        C["SPLOTCHES_TRANSLATE"] = st.checkbox("Splotches Translate", value=sp.get("SPLOTCHES_TRANSLATE", True), help="SPLOTCHES_TRANSLATE")
        if C["SPLOTCHES_TRANSLATE"]:
            C['SPLOTCH_TRANSLATION_DURATION'] = st.number_input("Splotch Translation Duration", value=sp.get("SPLOTCH_TRANSLATION_DURATION", 5.0), min_value=0.0, step=1.0, help="SPLOTCH_TRANSLATION_DURATION")
            st.divider()
            C["MIN_X_DISTANCE_PERC"] = st.number_input("Min x distance (relative to canvas width)", value=sp.get("MIN_X_DISTANCE_PERC", 0.0), step=1.0, help="MIN_X_DISTANCE_PERC")
            C["MAX_X_DISTANCE_PERC"] = st.number_input("Max x distance (relative to canvas width)", value=sp.get("MAX_X_DISTANCE_PERC", 0.0), step=1.0, help="MAX_X_DISTANCE_PERC")
            st.divider()
            C["MIN_Y_DISTANCE_PERC"] = st.number_input("Min y distance (relative to canvas height)", value=sp.get("MIN_Y_DISTANCE_PERC", 4.0), step=1.0, help="MIN_Y_DISTANCE_PERC")
            C["MAX_Y_DISTANCE_PERC"] = st.number_input("Max y distance (relative to canvas height)", value=sp.get("MAX_Y_DISTANCE_PERC", 20.0), step=1.0, help="MAX_Y_DISTANCE_PERC")
            st.divider()
            
        C["SPLOTCHES_ROTATE"] = st.checkbox("Rotate Splotches", value=sp.get("SPLOTCHES_ROTATE", True), help="SPLOTCHES_ROTATE")
        if C["SPLOTCHES_ROTATE"]:
            C['MIN_SPLOTCH_ROTATION_DURATION'] = st.number_input("Min Splotch Rotation Duration", value=sp.get("MIN_SPLOTCH_ROTATION_DURATION", 5.0), min_value=0.0, step=1.0, help="MIN_SPLOTCH_ROTATION_DURATION")
            C['MAX_SPLOTCH_ROTATION_DURATION'] = st.number_input("Max Splotch Rotation Duration", value=sp.get("MAX_SPLOTCH_ROTATION_DURATION", 5.0), min_value=0.0, step=1.0, help="MAX_SPLOTCH_ROTATION_DURATION")

def generate_splotches(dwg, C, OTHER_CONFIG):
    # TODO: Animate the blotches, either their form or their position, or both?
    # TODO: Get some of the texture stuff in, make them look metallic and light reflecting...
    # Define the shadow filter using feGaussianBlur and feOffset
    if C["HAS_SHADOW"]: 
        filter_element = dwg.filter(id="shadow", x="-50%", y="-50%", width="200%", height="200%")
        filter_element.feGaussianBlur(in_="SourceAlpha", stdDeviation=C["SHADOW_BLURRINESS"], result="blur")
        filter_element.feFlood(flood_color=C["SHADOW_COLOR"], flood_opacity=C["SHADOW_OPACITY"], result="floodShadow")  # Set a less intense shadow color
        filter_element.feComposite(in_="floodShadow", in2="blur", operator="in", result="compositeShadow")
    
        dwg.defs.add(filter_element)
    
    for i in range(C["NUMBER_OF_SPLOTCHES"]):
        # Define the center & size of the circle
        c = (100 * random.random(), 100 * random.random())
        r = (C["SPLOTCH_SIZE_MAX"] - C["SPLOTCH_SIZE_MIN"]) * random.random() + C["SPLOTCH_SIZE_MIN"]
    
        number_of_splotch_points = random.choice(range(C["NUMBER_OF_SPLOTCH_POINTS_MIN"], C["NUMBER_OF_SPLOTCH_POINTS_MAX"] + 1))
        
        splotch_points_regular = utils.generate_regular_points(c, number_of_splotch_points, r)
        splotch_points_from = [utils.translate_point_radially(utils.translate_point_tangentially(p, c, C["SPLOTCH_POINT_SPACING_RANDOMNESS"] * (random.random() - 0.5)), c, C["SPLOTCH_POINT_RADIAL_RANDOMNESS"] * (random.random() - 0.5)) for p in splotch_points_regular]
        splotch_points_to = [utils.translate_point_radially(p, c, C["SPLOTCH_POINT_ANIMATION_STRENGTH"] * (random.random() - 0.5)) for p in splotch_points_from]
        
        start_point_from_x, start_point_from_y = splotch_points_from[0]
        from_path_data = f"M {w(start_point_from_x, C['W'])},{h(start_point_from_y, C['H'])}\n"
        start_point_to_x, start_point_to_y = splotch_points_to[0]
        to_path_data = f"M {w(start_point_to_x, C['W'])},{h(start_point_to_y, C['H'])}\n"
        
        for k, ((from_x, from_y), (to_x, to_y))  in enumerate(zip(splotch_points_from, splotch_points_to)):
            ### FROM
            # find the previous and next points, wrapping around
            from_prev = splotch_points_from[(k - 1) % len(splotch_points_from)]
            from_next = splotch_points_from[(k + 1) % len(splotch_points_from)]
            
            # calculate control points for p
            from_control_x, from_control_y = utils.calculate_control(from_prev, (from_x, from_y), from_next, C["CONTROL_ARM_LENGTH"])
            
            from_path_data += f"S {w(from_control_x, C['W'])},{h(from_control_y, C['H'])} {w(from_x, C['W'])},{h(from_y, C['H'])}\n"
        
            ### TO
            # find the previous and next points, wrapping around
            to_prev = splotch_points_to[(k - 1) % len(splotch_points_to)]
            to_next = splotch_points_to[(k + 1) % len(splotch_points_to)]
            
            # calculate control points for p
            to_control_x, to_control_y = utils.calculate_control(to_prev, (to_x, to_y), to_next, C["CONTROL_ARM_LENGTH"])
            
            to_path_data += f"S {w(to_control_x, C['W'])},{h(to_control_y, C['H'])} {w(to_x, C['W'])},{h(to_y, C['H'])}\n"
        
        ### FROM
        # add the first point again, to get a smooth closure
        from_x, from_y = splotch_points_from[0]
        from_prev = splotch_points_from[-1]
        from_next = splotch_points_from[1]
        control_x, control_y = utils.calculate_control(from_prev, (from_x, from_y), from_next, C["CONTROL_ARM_LENGTH"])
        from_path_data += f"S {w(control_x, C['W'])},{h(control_y, C['H'])} {w(from_x, C['W'])},{h(from_y, C['H'])}\n"
        
        ### TO
        # add the first point again, to get a smooth closure
        to_x, to_y = splotch_points_to[0]
        to_prev = splotch_points_to[-1]
        to_next = splotch_points_to[1]
        control_x, control_y = utils.calculate_control(to_prev, (to_x, to_y), to_next, C["CONTROL_ARM_LENGTH"])
        to_path_data += f"S {w(control_x, C['W'])},{h(control_y, C['H'])} {w(to_x, C['W'])},{h(to_y, C['H'])}\n"
        
        # close the path
        from_path_data += "Z"
        to_path_data +="Z"
        
        # create the stripped path
        from_path = from_path_data.replace('\n', ' ').strip()
        to_path = to_path_data.replace('\n', ' ').strip()
        fill_color = C["FILL_COLOR"] if C["SINGLE_COLOR"] else random.choice(OTHER_CONFIG["COLORS"])

        splotch = dwg.path(d=from_path, fill=fill_color)
        
        if C["HAS_SHADOW"]:
            # need to offset the shadow manually and not use the offset in the filter definition as the rotation would otherwise
            # make the shadow not look quite right...
            splotch_shadow = dwg.path(d=from_path, fill="blue", filter="url(#shadow)", transform=f"translate({w(C['SHADOW_OFFSET_X'], C['W'])} {h(C['SHADOW_OFFSET_Y'], C['H'])})")
        
        # NOTE: The animation only works if x and y coordinates in the path are comma separated, and points are space separated
        # i.e. 'S 50 50, 20 20' doesn't work, but 'S 50,50 20,20' does... 
        if C["IS_ANIMATED"]:
            if C["SPLOTCH_POINTS_ANIMATED"]:
                animate_splotch_points = dwg.animate(
                    attributeName="d",
                    dur=f"{C['SPLOTCH_POINT_ANIMATION_DURATION']}s",
                    repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
                    values=[from_path, to_path, from_path],
                    keyTimes="0;0.5;1",
                    calcMode="spline",
                    keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
                )
            
            if C["SPLOTCHES_TRANSLATE"]:
                travel_distance_x = C["MIN_X_DISTANCE_PERC"] + (C["MAX_X_DISTANCE_PERC"] - C["MIN_X_DISTANCE_PERC"]) * random.random() # reused later
                travel_distance_y = C["MIN_Y_DISTANCE_PERC"] + (C["MAX_Y_DISTANCE_PERC"] - C["MIN_Y_DISTANCE_PERC"]) * random.random() # reused later
                animate_translation = dwg.animateTransform(
                    transform="translate",
                    repeatCount="indefinite",
                    dur=f"{C['SPLOTCH_TRANSLATION_DURATION']}s",
                    values=f"0 0;{w(travel_distance_x, C['W'])} {h(travel_distance_y, C['H'])};0 0",
                    keyTimes="0;0.5;1",
                    calcMode="spline",
                    keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
                )
                
                # something is failing in the svgwrite library... need to set the attributeName manually
                animate_translation["attributeName"] = "transform"
                    
            if C["SPLOTCHES_ROTATE"]:    
                animate_rotation = dwg.animateTransform(
                    transform="rotate",
                    repeatCount="indefinite",
                    dur=f"{C['MIN_SPLOTCH_ROTATION_DURATION'] + (C['MAX_SPLOTCH_ROTATION_DURATION'] - C['MIN_SPLOTCH_ROTATION_DURATION']) * random.random()}s",
                    from_=f"0 {w(c[0], C['W'])} {h(c[1], C['H'])}",
                    to=f"360 {w(c[0], C['W'])} {h(c[1], C['H'])}",
                    additive="sum"
                )
                
                animate_rotation["attributeName"] = "transform"
            
            if C["HAS_SHADOW"] and C["SPLOTCHES_TRANSLATE"]:
                # shadow needs to be translated separately because it's offset
                animate_translation_shadow = dwg.animateTransform(
                    transform="translate",
                    repeatCount="indefinite",
                    dur=f"{C['SPLOTCH_TRANSLATION_DURATION']}s",
                    values=f"{w(C['SHADOW_OFFSET_X'], C['W'])} {h(C['SHADOW_OFFSET_Y'], C['H'])};{w(travel_distance_x, C['W'] + C['SHADOW_OFFSET_X'])} {h(travel_distance_y, C['H'] + C['SHADOW_OFFSET_Y'])};{w(C['SHADOW_OFFSET_X'], C['W'])} {h(C['SHADOW_OFFSET_Y'], C['H'])}",
                    keyTimes="0;0.5;1",
                    calcMode="spline",
                    keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
                )
                
                animate_translation_shadow["attributeName"] = "transform"
            
            if C["SPLOTCH_POINTS_ANIMATED"]: splotch.add(animate_splotch_points)
            if C["SPLOTCHES_TRANSLATE"]:splotch.add(animate_translation)
            if C["SPLOTCHES_ROTATE"]:splotch.add(animate_rotation)
            
            # add shadow animations
            if C["HAS_SHADOW"]:
                if C["SPLOTCH_POINTS_ANIMATED"]: splotch_shadow.add(animate_splotch_points)
                if C["SPLOTCHES_TRANSLATE"]:splotch_shadow.add(animate_translation_shadow)
                if C["SPLOTCHES_ROTATE"]:splotch_shadow.add(animate_rotation)
        
        if C["HAS_SHADOW"]: dwg.add(splotch_shadow)
        
        dwg.add(splotch)
        
    if C["HAS_NOISE"]:
        rect = dwg.rect(insert=(0, 0), size=(C['W'], C['H']), fill=random.choice(OTHER_CONFIG["COLORS"]), fill_opacity=0.2, filter="url(#noiseFilter)")
        dwg.add(rect)
    
    return dwg