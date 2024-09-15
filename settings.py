import streamlit as st
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from bubbles import bubble_settings
from filters import filter_settings
from waves import wave_settings
from splotches import splotch_settings
import pprint
import json

@st.dialog("Config Definition")
def show_config_modal(CONFIG, sp):
    # Add a radio button to choose between formats
    is_json = st.checkbox("JSON formatted", value=True)

    # Add a checkbox to control sorting
    sort_items = st.checkbox("Sort Items", value=False)
    
    # Add a checkbox to control whether a 
    name = st.text_input("Preset Name", value=sp["name"])

    # Show the config based on the selected format and sorting option
    config = CONFIG if name == "" else {"name": name} | CONFIG
    formatted_config = json.dumps(config, indent=4, sort_keys=sort_items) if is_json else pprint.pformat(config, indent=4, sort_dicts=sort_items).replace("{", "{\n ").replace("'", '"')
    st.code(formatted_config, language='json' if is_json else "python")

def settings_component(C, OTHER_CONFIG, presets):
    ##### PRESETS #####
    preset_names = [preset["name"] for preset in presets]
    PRESET = st.sidebar.selectbox("Choose Preset", preset_names, index=preset_names.index("Slow Splotches"))
    sp = next(preset for preset in presets if preset["name"] == PRESET) # selected preset

    ##### GENERAL SETTINGS #####
    st.sidebar.header("General Settings")
    C["SEED"] = st.sidebar.number_input("Random Seed", value = sp.get("SEED", 3), help="SEED")
    with st.sidebar.expander("General Settings"):
        C['W'] = st.number_input("Width", value=sp.get("W", 600), step=1, help="W")
        C['H'] = st.number_input("Height", value=sp.get("H", 600), step=1, help="H")
        valid_color_schemes = [cmap_name for cmap_name in plt.colormaps() if hasattr(plt.get_cmap(cmap_name), 'colors')]
        C["COLOR_SCHEME"] = st.selectbox("Color Scheme", valid_color_schemes, index=valid_color_schemes.index(sp.get("COLOR_SCHEME", 600)), help="COLOR_SCHEME")
        OTHER_CONFIG["COLORS"] = [mcolors.rgb2hex(color) for color in plt.get_cmap(C["COLOR_SCHEME"]).colors]
        C["HAS_BACKGROUND"] = st.checkbox("Add Background", value=sp.get("HAS_BACKGROUND", True), help="HAS_BACKGROUND")
        if C["HAS_BACKGROUND"]:
            C["BACKGROUND_COLOR"] = st.color_picker("Background Color", value=sp.get("BACKGROUND_COLOR", 600), help="BACKGROUND_COLOR")
            
    ##### GENERAL ANIMATION SETTINGS #####
    with st.sidebar.expander("General Animation Settings"):
        C["IS_ANIMATED"] = st.checkbox("Animated", value=sp.get("IS_ANIMATED", True), help="IS_ANIMATED")
        C["REPEAT_ANIMATION"] = st.checkbox("Repeat Animation", value=sp.get("REPEAT_ANIMATION", True), help="REPEAT_ANIMATION")
        C["ANIMATION_DURATION"] = st.number_input("Animation Duration in s", value=sp.get("ANIMATION_DURATION", 5.0), step=0.1, help="ANIMATION_DURATION")

    ##### TYPE SELECTION AND SETTINGS #####
    st.sidebar.header("Type Settings")
    modules = ["Bubbles", "Filters", "Waves", "Radial Waves", "Splotches"]
    C["MODULE"] = st.sidebar.selectbox("Type of Graphic", modules, index=modules.index(sp.get("MODULE", "Waves")), help="MODULE")

    if C["MODULE"] == "Bubbles": bubble_settings(C, OTHER_CONFIG, sp)
    if C["MODULE"] == "Filters": filter_settings(C, OTHER_CONFIG, sp)
    if C["MODULE"] == "Waves": wave_settings(C, OTHER_CONFIG, sp)
    if C["MODULE"] == "Splotches": splotch_settings(C, OTHER_CONFIG, sp)
        
    if st.sidebar.button("See Config Definition"):
        show_config_modal(C, sp)

    return sp