import streamlit as st
import svgwrite
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
import os
import tempfile

###################################
# Streamlit inputs for configuration
st.sidebar.header("Configuration")

WIDTH = st.sidebar.slider("Width", min_value=100, max_value=1000, value=600)
HEIGHT = st.sidebar.slider("Height", min_value=100, max_value=1000, value=900)
NUMBER_OF_BUBBLES = st.sidebar.slider("Number of Bubbles", min_value=1, max_value=1000, value=20)
COLOR_SCHEME = st.sidebar.selectbox("Color Scheme", plt.colormaps(), index=plt.colormaps().index('Pastel1'))
IS_ANIMATED = st.sidebar.checkbox("Animated", value=True)
IS_DISTORTED = st.sidebar.checkbox("Distorted", value=True)
HAS_NOISE = st.sidebar.checkbox("Has Noise", value=False)
SAVE_OUTPUT = st.sidebar.checkbox("Save Output", value=False)
DISPLAY_OUTPUT = st.sidebar.checkbox("Display Output", value=True)
SEED = st.sidebar.number_input("Random Seed", value=1)

###################################
# Set up the drawing environment
random.seed(SEED)
colors = [mcolors.rgb2hex(color) for color in plt.get_cmap(COLOR_SCHEME).colors]
dwg = svgwrite.Drawing(size=(WIDTH, HEIGHT))

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
    circle = dwg.circle(center=(x/100 * WIDTH, y/100 * HEIGHT), r=r/100 * WIDTH, fill=f'url(#{gradient_id})')
    if IS_DISTORTED:
        circle.attribs['filter'] = "url(#distortFilter)"
    
    if IS_ANIMATED:
        min_speed = 4
        max_speed = 20
        speed = (max_speed - min_speed) * random.random() + min_speed
        
        animate = dwg.animate(
            attributeName="cy",
            from_=y/100 * HEIGHT,
            to=y/100 * HEIGHT - speed/100 * HEIGHT,
            dur="20s",
            repeatCount="indefinite",
            values=[y/100 * HEIGHT, y/100 * HEIGHT - speed/100 * HEIGHT, y/100 * HEIGHT],
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

# Save output if required
if SAVE_OUTPUT:
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    filename = f'bubbles_no-{NUMBER_OF_BUBBLES}_colors-{COLOR_SCHEME}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.svg'
    full_path = os.path.join(output_dir, filename)
    dwg.saveas(full_path)
    st.sidebar.write(f"File saved as: {full_path}")

# Display output as an image
if DISPLAY_OUTPUT:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmpfile:
        dwg.saveas(tmpfile.name)
        st.image(tmpfile.name)
