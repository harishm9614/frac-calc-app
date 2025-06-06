import streamlit as st
import math

# --- Unit System Toggle ---
st.set_page_config(page_title="Hydraulic Frac Calculator", layout="centered")
st.title("Hydraulic Fracturing Calculator")

unit_system = st.radio("Select Unit System", ["SI", "Imperial"], horizontal=True)

# --- Conversion Factors ---
if unit_system == "SI":
    length_unit = "m"
    diameter_unit = "m"
    flow_rate_unit = "m³/s"
    pressure_unit = "Pa"
    density_unit = "kg/m³"
    viscosity_unit = "Pa·s"
    slurry_conc_unit = "kg/m³"
else:
    length_unit = "ft"
    diameter_unit = "in"
    flow_rate_unit = "bbl/min"
    pressure_unit = "psi"
    density_unit = "lb/ft³"
    viscosity_unit = "cp"
    slurry_conc_unit = "lb/gal"

# --- Pressure Drop Calculator ---
st.header("🔻 Pressure Drop Calculator")

with st.form("pressure_drop_form"):
    st.subheader("Input Parameters")
    length = st.number_input(f"Pipe Length ({length_unit})", min_value=0.0, step=1.0)
    diameter = st.number_input(f"Pipe Diameter ({diameter_unit})", min_value=0.0, step=0.1)
    flow_rate = st.number_input(f"Flow Rate ({flow_rate_unit})", min_value=0.0, step=0.1)
    density = st.number_input(f"Fluid Density ({density_unit})", min_value=0.0, step=1.0)
    viscosity = st.number_input(f"Fluid Viscosity ({viscosity_unit})", min_value=0.0, step=0.1)
    roughness = st.number_input("Pipe Roughness (absolute, same units as diameter)", min_value=0.0, step=0.0001)
    method = st.selectbox("Friction Loss Method", ["Darcy-Weisbach"])
    submitted1 = st.form_submit_button("Calculate Pressure Drop")

    if submitted1:
        if unit_system == "Imperial":
            # Convert flow rate from bbl/min to ft³/s (1 bbl = 5.615 ft³)
            flow_rate = flow_rate * 5.615 / 60
            diameter = diameter / 12  # in to ft
            viscosity = viscosity / 1000  # cp to lb/ft·s approx
        
        area = math.pi * (diameter / 2) ** 2
        velocity = flow_rate / area
        reynolds = density * velocity * diameter / viscosity

        if reynolds == 0:
            friction_factor = 0
        elif reynolds < 2300:
            friction_factor = 64 / reynolds
        else:
            friction_factor = 0.079 / reynolds ** 0.25  # Blasius approx

        dp = friction_factor * (length / diameter) * 0.5 * density * velocity ** 2

        if unit_system == "Imperial":
            dp = dp / 144  # lb/ft² to psi approx

        st.success(f"Pressure Drop: {dp:.2f} {pressure_unit}")
        st.info(f"Reynolds Number: {reynolds:.0f}")

# --- Sand Fill Calculator ---
st.header("🏜 Sand Fill Calculator")

with st.form("sand_fill_form"):
    st.subheader("Input Parameters")
    casing_id = st.number_input(f"Casing ID ({diameter_unit})", min_value=0.0, step=0.1)
    tubing_od = st.number_input(f"Tubing OD ({diameter_unit})", min_value=0.0, step=0.1)
    fill_depth = st.number_input(f"Sand Fill Depth ({length_unit})", min_value=0.0, step=0.1)
    slurry_conc = st.number_input(f"Slurry Concentration ({slurry_conc_unit})", min_value=0.0, step=1.0)
    submitted2 = st.form_submit_button("Calculate Sand Volume")

    if submitted2:
        if unit_system == "Imperial":
            casing_id = casing_id / 12  # in to ft
            tubing_od = tubing_od / 12  # in to ft

        area = math.pi * (casing_id ** 2 - tubing_od ** 2) / 4
        sand_volume = area * fill_depth

        if unit_system == "Imperial":
            # convert ft³ to bbl and lb
            volume_bbl = sand_volume / 5.615
            sand_mass = volume_bbl * slurry_conc  # lb
            st.success(f"Sand Volume: {volume_bbl:.2f} bbl")
            st.info(f"Sand Mass: {sand_mass:.0f} lb")
        else:
            sand_mass = sand_volume * slurry_conc  # kg
            st.success(f"Sand Volume: {sand_volume:.2f} m³")
            st.info(f"Sand Mass: {sand_mass:.0f} kg")

# --- Sand Plug Calculator ---
st.header("🧱 Sand Plug Calculator")

with st.form("sand_plug_form"):
    st.subheader("Input Parameters")
    hole_diameter = st.number_input(f"Hole Diameter ({diameter_unit})", min_value=0.0, step=0.1)
    plug_length = st.number_input(f"Plug Length ({length_unit})", min_value=0.0, step=0.1)
    slurry_conc = st.number_input(f"Slurry Concentration ({slurry_conc_unit})", min_value=0.0, step=1.0, key="plug_slurry_conc")
    pump_rate = st.number_input(f"Pump Rate ({flow_rate_unit})", min_value=0.0, step=0.1)
    submitted3 = st.form_submit_button("Calculate Sand Plug")

    if submitted3:
        if unit_system == "Imperial":
            hole_diameter = hole_diameter / 12  # in to ft
            pump_rate = pump_rate * 5.615 / 60  # bbl/min to ft³/s

        area = math.pi * (hole_diameter / 2) ** 2
        volume = area * plug_length  # m³ or ft³

        if unit_system == "Imperial":
            volume_bbl = volume / 5.615
            sand_mass = volume_bbl * slurry_conc
            time_min = volume_bbl / (pump_rate * 60) if pump_rate > 0 else 0
            st.success(f"Slurry Volume: {volume_bbl:.2f} bbl")
            st.info(f"Sand Mass: {sand_mass:.0f} lb")
            st.info(f"Pumping Time: {time_min:.2f} min")
        else:
            sand_mass = volume * slurry_conc
            time_min = volume / pump_rate / 60 if pump_rate > 0 else 0
            st.success(f"Slurry Volume: {volume:.2f} m³")
            st.info(f"Sand Mass: {sand_mass:.0f} kg")
            st.info(f"Pumping Time: {time_min:.2f} min")
