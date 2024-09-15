import streamlit as st
import random
from utilities import w, h

def filter_settings(C, OTHER_CONFIG, sp):
    with st.sidebar.expander("Shape Settings"):
        shapes = ["Square", "Circle"]
        C["SHAPE"] = st.selectbox("Shape", shapes, index=shapes.index(sp.get("SHAPE", "Circle")), help="SHAPE")
        C["SHAPE_DIMENSIONS"] = st.number_input("Shape Dimensions (relative to canvas width)", value=sp.get("SHAPE_DIMENSIONS", 80.0), step=1.0, help="SHAPE_DIMENSIONS")
        
    with st.sidebar.expander("Texture Settings"):
        texture_types = ["fractalNoise", "turbulence"]
        C["TEXTURE_TYPE"] = st.selectbox("Color Scheme", texture_types, index=texture_types.index(sp.get("TEXTURE_TYPE", "fractalNoise")), help="TEXTURE_TYPE")
        C["BASE_FREQUENCY"] = st.number_input("Base Frequency", value=sp.get("BASE_FREQUENCY", 0.05), step=0.1, help="BASE_FREQUENCY")
        C["NUM_OCTAVES"] = st.number_input("Number of Octaves", value=sp.get("NUM_OCTAVES", 20), step=1, help="NUM_OCTAVES")
    
    with st.sidebar.expander("Color Settings"):
        C["SINGLE_COLOR"] = st.checkbox("Use Single Color", value=sp.get("SINGLE_COLOR", True), help="SINGLE_COLOR")
        if (C["SINGLE_COLOR"]):
            C["FILL_COLOR"] = st.color_picker("Choose Color", value=sp.get("FILL_COLOR", "#D412BC"), help="FILL_COLOR")
    
    with st.sidebar.expander("Lighting Settings"):
        C["SURFACE_SCALE"] = st.number_input("Surface Scale", value=sp.get("SURFACE_SCALE", 20.0), step=1.0, help="SURFACE_SCALE")
        C["DIFFUSE_CONSTANT"] = st.number_input("Diffuse Constant", value=sp.get("DIFFUSE_CONSTANT", 1.0), step=1.0, help="DIFFUSE_CONSTANT")
        C["LIGHTING_COLOR_INPUT"] = st.color_picker("Lighting Color", value=sp.get("LIGHTING_COLOR_INPUT", "#fff"), help="LIGHTING_COLOR_INPUT")
        
    with st.sidebar.expander("Filter Animation Settings"):        
        C["MIN_X_PERC"] = st.number_input("min x (relative to canvas width)", value=sp.get("MIN_X_PERC", 10.0), step=1.0, help="MIN_X_PERC")
        C["MAX_X_PERC"] = st.number_input("max x (relative to canvas width)", value=sp.get("MAX_X_PERC", 90.0), step=1.0, help="MAX_X_PERC")
        st.divider()
        C["MIN_Y_PERC"] = st.number_input("min y (relative to canvas width)", value=sp.get("MIN_Y_PERC", 10.0), step=1.0, help="MIN_Y_PERC")
        C["MAX_Y_PERC"] = st.number_input("max y (relative to canvas width)", value=sp.get("MAX_Y_PERC", 10.0), step=1.0, help="MAX_Y_PERC")
        st.divider()
        C["MIN_Z"] = st.number_input("min z", value=sp.get("MIN_Z", 5.0), step=1.0, help="MIN_Z")
        C["MAX_Z"] = st.number_input("max z", value=sp.get("MAX_Z", 500.0), step=1.0, help="MAX_Z")
        
def generate_filters(dwg, C, OTHER_CONFIG):
    ######## filter definitions ########
    ### textured filter ###
    filter_textured = dwg.defs.add(dwg.filter(id='filterTextured'))
    filter_textured.feTurbulence(type=C["TEXTURE_TYPE"], baseFrequency=C["BASE_FREQUENCY"], numOctaves=C["NUM_OCTAVES"], result="turbulence")
    point_light = filter_textured.feDiffuseLighting(
        in_="turbulence",
        surfaceScale=C["SURFACE_SCALE"], 
        diffuseConstant=C["DIFFUSE_CONSTANT"],
        lighting_color=C["LIGHTING_COLOR_INPUT"].strip().lower(),
        result="highlight"
    ).fePointLight(source=(w(C["MIN_X_PERC"], C["W"]), h(C["MIN_Y_PERC"], C["H"]), C["MIN_Z"]))
    filter_textured.feComposite(operator="in", in_="highlight", in2="SourceAlpha", result="highlightApplied")
    filter_textured.feBlend(in_="SourceGraphic", in2="highlightApplied", mode="multiply")

    if C["IS_ANIMATED"]:
        animation_x = dwg.animate(
            attributeName="x",
            dur=f"{C["ANIMATION_DURATION"]}s",
            repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
            values=[w(C["MIN_X_PERC"], C["W"]), w(C["MAX_X_PERC"], C["W"]), w(C["MIN_X_PERC"], C["W"])],  # cy values at keyframes as a list of strings
            keyTimes="0;0.5;1",  # Keyframe times as a space-separated string
            calcMode="spline",  # Use spline mode for smooth easing
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1"  # Control points for easing                
        )
        
        animation_y = dwg.animate(
            attributeName="y",
            dur=f"{C["ANIMATION_DURATION"]}s",
            repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
            values=[h(C["MIN_Y_PERC"], C["H"]), h(C["MAX_Y_PERC"], C["H"]), h(C["MIN_Y_PERC"], C["H"])],  # cy values at keyframes as a list of strings
            keyTimes="0;0.5;1",  # Keyframe times as a space-separated string
            calcMode="spline",  # Use spline mode for smooth easing
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1"  # Control points for easing
                
        )

        animation_z = dwg.animate(
            attributeName="z",
            dur=f"{C["ANIMATION_DURATION"]}s",
            repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1,
            values=[C["MIN_Z"], C["MAX_Z"], C["MIN_Z"], C["MAX_Z"], C["MIN_Z"]],  # cy values at keyframes as a list of strings
            keyTimes="0;0.25;0.5;0.75;1",  # Keyframe times as a space-separated string
            calcMode="spline",  # Use spline mode for smooth easing
            keySplines="0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1"  # Control points for easing 
        )

        point_light.add(animation_x)
        point_light.add(animation_y)
        point_light.add(animation_z)
        
        # it looks like the light animation doesn't properly work unless there is an actual shape that's also being animated.
        # thus, just adding a random shape and animation...
        animation_enabler = dwg.animate(attributeName="cx", from_=w(40, C["W"]), to=w(60, C["W"]), dur=f"{C["ANIMATION_DURATION"]}s", repeatCount="indefinite" if C["REPEAT_ANIMATION"] else 1)
        circle_enabler = dwg.circle(center=(w(50, C["W"]), h(50, C["H"])), r=0, fill="black")
        circle_enabler.add(animation_enabler)
        dwg.add(circle_enabler)

    ######## draw shapes ########
    fill_color = C["FILL_COLOR"] if C["SINGLE_COLOR"] else random.choice(OTHER_CONFIG["COLORS"])
    shape = None
    if C["SHAPE"] == "Circle": 
        shape = dwg.circle(center=(w(50, C["W"]), h(50, C["H"])), r=w(C["SHAPE_DIMENSIONS"]/2, C["W"]), fill=fill_color, filter=f"url(#filterTextured)")
    elif C["SHAPE"] == "Square":
        shape = dwg.rect(insert=(w((100-C["SHAPE_DIMENSIONS"])/2, C["W"]), h((100-C["SHAPE_DIMENSIONS"])/2, C["H"])), size=(w(C["SHAPE_DIMENSIONS"], C["W"]), w(C["SHAPE_DIMENSIONS"], C["W"])), fill=fill_color, filter=f"url(#filterTextured)")
        
    dwg.add(shape)
    
    return dwg
   