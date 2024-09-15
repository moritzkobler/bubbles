import streamlit as st
import random
from utilities import w, h

def bubble_settings(C, OTHER_CONFIG, sp):
    with st.sidebar.expander("General Bubble Settings"):
            C["NUMBER_OF_BUBBLES"] = st.number_input("Number of Bubbles", min_value=1, max_value=1000, value=sp.get("NUMBER_OF_BUBBLES", 20), step=1, help="NUMBER_OF_BUBBLES")
            C["IS_DISTORTED"] = st.checkbox("Distorted", value=sp.get("IS_DISTORTED", True), help="IS_DISTORTED")
            C["HAS_NOISE"] = st.checkbox("Has Noise", value=sp.get("HAS_NOISE", False), help="HAS_NOISE")
            
    with st.sidebar.expander("Bubble Settings"):
        C["MIN_RADIUS"] = st.number_input("Minimum Radius (relative to canvas width)", min_value=0.0, value=sp.get("MIN_RADIUS", 5.0), step=1.0, help="MIN_RADIUS")
        C["MAX_RADIUS"] = st.number_input("Maximum Radius (relative to canvas width)", min_value=1.0, value=sp.get("MAX_RADIUS", 30.0), step=1.0, help="MAX_RADIUS")

    with st.sidebar.expander("Color Settings"):
        C["HAS_GRADIENT"] = st.checkbox("Add Gradient", value=sp.get("HAS_GRADIENT", True), help="HAS_GRADIENT")
        C["SINGLE_COLOR"] = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", False), help="SINGLE_COLOR")
        if (C["SINGLE_COLOR"]):
            C["FILL_COLOR"] = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#D412BC"), help="FILL_COLOR")

    with st.sidebar.expander("Bubble Animation Settings"):        
        C["MIN_X_DISTANCE_PERC"] = st.number_input("Min x distance (relative to canvas width)", value=sp.get("MIN_X_DISTANCE_PERC", 0.0), step=1.0, help="MIN_X_DISTANCE_PERC")
        C["MAX_X_DISTANCE_PERC"] = st.number_input("Max x distance (relative to canvas width)", value=sp.get("MAX_X_DISTANCE_PERC", 0.0), step=1.0, help="MAX_X_DISTANCE_PERC")
        st.divider()
        C["MIN_Y_DISTANCE_PERC"] = st.number_input("Min y distance (relative to canvas height)", value=sp.get("MIN_Y_DISTANCE_PERC", 4.0), step=1.0, help="MIN_Y_DISTANCE_PERC")
        C["MAX_Y_DISTANCE_PERC"] = st.number_input("Max y distance (relative to canvas height)", value=sp.get("MAX_Y_DISTANCE_PERC", 20.0), step=1.0, help="MAX_Y_DISTANCE_PERC")

def generate_bubbles(dwg, C, OTHER_CONFIG):
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
    for i in range(C["NUMBER_OF_BUBBLES"]):
        # Define the center & size of the circle
        x = 120 * random.random() - 10
        y = 120 * random.random() - 10
        r = (C["MAX_RADIUS"] - C["MIN_RADIUS"]) * random.random() + C["MIN_RADIUS"]
        base_color = C["FILL_COLOR"] if C["SINGLE_COLOR"] else random.choice(OTHER_CONFIG["COLORS"])
        
        # Define a linear gradient
        gradient_id = f"gradient-{i}"
        linear_gradient = dwg.linearGradient((0, 0), (1, 1), id=gradient_id)
        linear_gradient.add_stop_color(0, base_color, 1)
        linear_gradient.add_stop_color(1, base_color, 0.1)
        dwg.defs.add(linear_gradient)
        
        fill_color = f'url(#{gradient_id})' if C["HAS_GRADIENT"] else base_color
        
        # Define the circle itself
        circle = dwg.circle(center=(w(x, C["W"]), h(y, C["H"])), r=w(r, C["W"]), fill=fill_color)
        if C["IS_DISTORTED"]:
            circle.attribs['filter'] = "url(#distortFilter)"
        
        if C["IS_ANIMATED"]:
            distance_x = (C["MAX_X_DISTANCE_PERC"] - C["MIN_X_DISTANCE_PERC"]) * random.random() + C["MIN_X_DISTANCE_PERC"]
            animate_x = dwg.animate(
                attributeName="cx",
                dur=f"{C['ANIMATION_DURATION']}s",
                repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
                values=[w(x, C["W"]), w(x, C["W"]) + w(distance_x, C["W"]), w(x, C["W"])],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            
            distance_y = (C["MAX_Y_DISTANCE_PERC"] - C["MIN_Y_DISTANCE_PERC"]) * random.random() + C["MIN_X_DISTANCE_PERC"]
            animate_y = dwg.animate(
                attributeName="cy",
                dur=f"{C['ANIMATION_DURATION']}s",
                repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
                values=[h(y, C["H"]), h(y, C["H"]) - h(distance_y, C["H"]), h(y, C["H"])],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            
            circle.add(animate_x)
            circle.add(animate_y)
        
        dwg.add(circle)

    # Add noise if required
    if C["HAS_NOISE"]:
        rect = dwg.rect(insert=(0, 0), size=(C["W"], C["H"]), fill=random.choice(OTHER_CONFIG["COLORS"]), fill_opacity=0.2, filter="url(#noiseFilter)")
        dwg.add(rect)
        
    return dwg
