import streamlit as st
import svgwrite
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import os
import tempfile

################# UTILITIES #################
def w(p):
    return p/100 * WIDTH

def h(p):
    return p/100 * HEIGHT

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
        x = 100 * random.random()
        y = 100 * random.random()
        
        min_r = 5
        max_r = 30
        r = (max_r - min_r) * random.random() + min_r
        
        base_color = random.choice(colors)
        
        # Define a linear gradient
        gradient_id = f"gradient-{i}"
        linear_gradient = dwg.linearGradient((0, 0), (1, 1), id=gradient_id)
        linear_gradient.add_stop_color(0, base_color, 1)
        linear_gradient.add_stop_color(1, base_color, 0.1)
        dwg.defs.add(linear_gradient)
        
        # Define the circle itself
        circle = dwg.circle(center=(w(x), h(y)), r=w(r), fill=f'url(#{gradient_id})')
        if IS_DISTORTED:
            circle.attribs['filter'] = "url(#distortFilter)"
        
        if IS_ANIMATED:
            min_speed = 4
            max_speed = 20
            speed = (max_speed - min_speed) * random.random() + min_speed
            
            animate = dwg.animate(
                attributeName="cy",
                from_=h(y),
                to=h(y) - h(speed),
                dur="20s",
                repeatCount="indefinite" if REPEAT_ANIMATION else 1,
                values=[h(y), h(y) - h(speed), h(y)],
                keyTimes="0;0.5;1",
                calcMode="spline",
                keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
            )
            circle.add(animate)
        
        dwg.add(circle)

    # Add noise if required
    if HAS_NOISE:
        rect = dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=random.choice(colors), fill_opacity=0.2, filter="url(#noiseFilter)")
        dwg.add(rect)
        
    return dwg

def generate_filters(dwg):
    ######## filter definitions ########
    try:
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
    except TypeError:
        st.warning(f'"{LIGHTING_COLOR_INPUT.strip().lower()}" is not a valid lighting color. Try a hex code or the usual string colors that are allowed. Leave it blank if you want a transparent background')

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
    circle = dwg.circle(center=(w(50), h(50)), r=w(40), fill=random.choice(colors), filter=f"url(#filterTextured)")
    dwg.add(circle)
    
    return dwg
    
################# SIDEBAR CONFIGURATION #################
# Streamlit inputs for configuration
st.sidebar.header("Configuration")
with st.sidebar.expander("General Settings"):
    WIDTH = st.number_input("Width", value=600, step=1)
    HEIGHT = st.number_input("Height", value=900, step=1)
    COLOR_SCHEME = st.selectbox("Color Scheme", plt.colormaps(), index=plt.colormaps().index('Pastel1'))
    BACKGROUND_COLOR = st.text_input("Background Color", value="white")
    IS_ANIMATED = st.checkbox("Animated", value=True)
    REPEAT_ANIMATION = st.checkbox("Repeat Animation", value=True)
    SAVE_OUTPUT = st.checkbox("Save Output", value=False)
    # DISPLAY_OUTPUT = st.checkbox("Display Output", value=True)
    SEED = st.number_input("Random Seed", value=1)

MODULE = st.sidebar.selectbox("Type of Graphic", ["Bubbles", "Filters", "Waves"], index=1)

if MODULE == "Bubbles":
    NUMBER_OF_BUBBLES = st.sidebar.number_input("Number of Bubbles", min_value=1, max_value=1000, value=20, step=1)
    IS_DISTORTED = st.sidebar.checkbox("Distorted", value=True)
    HAS_NOISE = st.sidebar.checkbox("Has Noise", value=False)
if MODULE == "Filters":
    ANIMATION_DURATION_INPUT = st.sidebar.number_input("Animation Duration in s", value=5.0, step=0.1)
    ANIMATION_DURATION = f"{ANIMATION_DURATION_INPUT}s"
    with st.sidebar.expander("Texture Settings"):
        TEXTURE_TYPE = st.selectbox("Color Scheme", ["fractalNoise", "turbulence"], index=0)
        BASE_FREQUENCY = st.number_input("Base Frequency", value=0.05, step=0.1)
        NUM_OCTAVES = st.number_input("Number of Octaves", value=20, step=1)
    
    with st.sidebar.expander("Lighting Settings"):
        SURFACE_SCALE = st.number_input("Surface Scale", value=20.0, step=1.0)
        DIFFUSE_CONSTANT = st.number_input("Diffuse Constant", value=1.0, step=1.0)
        LIGHTING_COLOR_INPUT = st.text_input("Lighting Color", value="white")
        
    with st.sidebar.expander("Animation Settings"):        
        MIN_X_PERC = st.number_input("min x (relative to canvas width)", value=10.0, step=1.0)
        MAX_X_PERC = st.number_input("max x (relative to canvas width)", value=90.0, step=1.0)
        st.divider()
        MIN_Y_PERC = st.number_input("min y (relative to canvas width)", value=10.0, step=1.0)
        MAX_Y_PERC = st.number_input("max y (relative to canvas width)", value=10.0, step=1.0)
        st.divider()
        MIN_Z = st.number_input("min z", value=5.0, step=1.0)
        MAX_Z = st.number_input("max z", value=500.0, step=1.0)
        
################# MAIN BODY #################
# set up the drawing environment
random.seed(SEED)
colors = [mcolors.rgb2hex(color) for color in plt.get_cmap(COLOR_SCHEME).colors]
dwg = svgwrite.Drawing(size=(WIDTH, HEIGHT))

# add the default background 
if BACKGROUND_COLOR.strip().lower() != "" and BACKGROUND_COLOR.strip().lower() != "transparent":
    try:
        bg_rect = dwg.rect(insert=(0, 0), size=(WIDTH, HEIGHT), fill=BACKGROUND_COLOR.strip().lower())
        dwg.add(bg_rect)
    except TypeError:
        st.warning(f'"{BACKGROUND_COLOR.strip().lower()}" is not a valid background color. Try a hex code or the usual string colors that are allowed. Leave it blank if you want a transparent background')

if MODULE == "Bubbles": dwg = generate_bubbles(dwg)
if MODULE == "Filters": dwg = generate_filters(dwg)
if MODULE == "Waves": st.info("Waves coming soon!")

# Save output if required
if SAVE_OUTPUT:
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    filename = f'bubbles_no-{NUMBER_OF_BUBBLES}_colors-{COLOR_SCHEME}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.svg'
    full_path = os.path.join(output_dir, filename)
    dwg.saveas(full_path)
    st.sidebar.write(f"File saved as: {full_path}")

# Display output as an image
with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmpfile:
    dwg.saveas(tmpfile.name)
    st.image(tmpfile.name)
    
    
