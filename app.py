import streamlit as st
import svgwrite
import random
import tempfile
import json
from settings import settings_component
from bubbles import generate_bubbles
from splotches import generate_splotches
from filters import generate_filters
from waves import generate_waves

################# PRESET DEFINITION #################
with open('presets.json', 'r') as file:
   presets = json.load(file)

################# SIDEBAR CONFIGURATION #################
st.set_page_config(layout="wide")
C = {} # config is used EVERYWHERE, thus the shorthand...
OTHER_CONFIG = {}
sp = settings_component(C, OTHER_CONFIG, presets)

################# MAIN BODY #################
# set up the drawing environment
random.seed(C["SEED"])
dwg = svgwrite.Drawing(size=(C['W'], C["H"]))

# add the default background 
if C["HAS_BACKGROUND"]:
    bg_rect = dwg.rect(insert=(0, 0), size=(C['W'], C["H"]), fill=C["BACKGROUND_COLOR"].strip().lower())
    dwg.add(bg_rect)

if C["MODULE"] == "Bubbles": dwg = generate_bubbles(dwg, C, OTHER_CONFIG)
if C["MODULE"] == "Filters": dwg = generate_filters(dwg, C, OTHER_CONFIG)
if C["MODULE"] == "Waves": dwg = generate_waves(dwg, C, OTHER_CONFIG)
if C["MODULE"] == "Splotches": dwg = generate_splotches(dwg, C, OTHER_CONFIG)
if C["MODULE"] == "Radial Waves": st.info("Radial waves coming soon!") # TODO

# Display output as an image
with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmpfile:
    dwg.saveas(tmpfile.name)
    st.image(tmpfile.name)
    
    
