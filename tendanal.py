import streamlit as st
import pandas as pd
import docx2txt
import PyPDF2
import math
import re

st.set_page_config(page_title="Tender Analyser & Hydraulic Frac Calculator", layout="wide")

st.title("Tender Analyser & Hydraulic Fracturing Calculator")

# --- File Upload & Text Extraction ---

uploaded_file = st.file_uploader(
    "Upload a tender document (PDF, Word, Excel)",
    type=['pdf', 'docx', 'xlsx', 'xls']
)

def extract_text_pdf(file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_word(file):
    text = docx2txt.process(file)
    return text

def extract_text_excel(file):
    df_dict = pd.read_excel(file, sheet_name=None)
    all_text = ""
    for sheet, data in df_dict.items():
        all_text += f"Sheet: {sheet}\n"
        all_text += data.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep='\n')
        all_text += "\n\n"
    return all_text

text = ""
if uploaded_file is not None:
    file_type = uploaded_file.type
    st.write(f"Uploaded file type: {file_type}")

    if file_type == "application/pdf":
        text = extract_text_pdf(uploaded_file)
    elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        text = extract_text_word(uploaded_file)
    elif file_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        text = extract_text_excel(uploaded_file)
    else:
        st.warning("Unsupported file type. Please upload PDF, Word or Excel files.")

if text:
    # --- Tender Document Viewer with Search ---
    st.header("Tender Document Viewer with Search")
    search_term = st.text_input("Search within the tender document:")

    if search_term:
        escaped_search = re.escape(search_term)
        highlighted_text = re.sub(
            f"({escaped_search})",
            r"<mark>\1</mark>",
            text,
            flags=re.IGNORECASE
        )
        st.markdown(
            f'<div style="height:400px; overflow:auto; border:1px solid #ddd; padding:10px; white-space: pre-wrap;">{highlighted_text}</div>',
            unsafe_allow_html=True
        )
    else:
        st.text_area("Tender Document Content", text, height=400)

    # --- Query & Scoring Module ---
    st.header("Tender Query & Scoring")

    query = st.text_input("Enter your query about the tender (e.g., payment terms, penalties):")

    if query:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        matches = pattern.findall(text)

        if matches:
            st.success(f"Found {len(matches)} matches for '{query}':")
            excerpts = []
            for m in pattern.finditer(text):
                start = max(m.start() - 100, 0)
                end = min(m.end() + 100, len(text))
                excerpt = text[start:end].replace('\n', ' ')
                excerpts.append(excerpt)

            for i, excerpt in enumerate(excerpts[:5]):
                st.write(f"**Match {i+1}:** ...{excerpt}...")
        else:
            st.warning(f"No matches found for '{query}'.")

    st.subheader("Tender Scoring Summary")

    ease_keywords = ['clear', 'simple', 'straightforward', 'standard']
    cost_keywords = ['cost', 'price', 'budget', 'expense', 'rate']
    risk_keywords = ['penalty', 'risk', 'delay', 'liability', 'breach']

    def score_keywords(text, keywords):
        score = 0
        for kw in keywords:
            score += len(re.findall(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE))
        return score

    ease_score = score_keywords(text, ease_keywords)
    cost_score = score_keywords(text, cost_keywords)
    risk_score = score_keywords(text, risk_keywords)

    total_score = ease_score + cost_score - risk_score

    st.markdown(f"""
    | Metric             | Score  |
    |--------------------|--------|
    | Ease of Compliance  | {ease_score}      |
    | Cost Competitiveness| {cost_score}      |
    | Risk Level (negative)| {risk_score}     |
    | **Overall Score**   | **{total_score}**  |
    """)

    if total_score > 10:
        st.success("Tender looks favorable overall.")
    elif total_score > 0:
        st.info("Tender has some pros and cons.")
    else:
        st.error("Tender appears risky or costly.")


# --- Hydraulic Fracturing Calculators ---
st.header("Hydraulic Fracturing Calculators")

unit_system = st.radio("Select Unit System", ["SI", "Imperial"], horizontal=True)

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

# Pressure Drop Calculator
st.subheader("Pressure Drop Calculator")
with st.form("pressure_drop_form"):
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
            # Convert imperial units to SI for calculation
            flow_rate = flow_rate * 5.615 / 60  # bbl/min to m³/s approx
            diameter = diameter / 39.37  # inch to meters
            viscosity = viscosity / 1000  # cp to Pa.s approx

        area = math.pi * (diameter / 2) ** 2
        velocity = flow_rate / area if area != 0 else 0
        reynolds = (density * velocity * diameter) / viscosity if viscosity != 0 else 0

        if reynolds == 0:
            friction_factor = 0
        elif reynolds < 2300:
            friction_factor = 64 / reynolds
        else:
            friction_factor = 0.079 / reynolds ** 0.25

        dp = friction_factor * (length / diameter) * 0.5 * density * velocity ** 2 if diameter != 0 else 0

        if unit_system == "Imperial":
            dp = dp / 6894.76  # Pascal to psi

        st.success(f"Pressure Drop: {dp:.2f} {pressure_unit}")
        st.info(f"Reynolds Number: {reynolds:.0f}")

# Sand Fill Calculator
st.subheader("Sand Fill Calculator")
with st.form("sand_fill_form"):
    casing_id = st.number_input(f"Casing ID ({diameter_unit})", min_value=0.0, step=0.1)
    tubing_od = st.number_input(f"Tubing OD ({diameter_unit})", min_value=0.0, step=0.1)
    fill_depth = st.number_input(f"Sand Fill Depth ({length_unit})", min_value=0.0, step=0.1)
    slurry_conc = st.number_input(f"Slurry Concentration ({slurry_conc_unit})", min_value=0.0, step=1.0)
    submitted2 = st.form_submit_button("Calculate Sand Volume")

    if submitted2:
        if unit_system == "Imperial":
            casing_id = casing_id / 39.37
            tubing_od = tubing_od / 39.37

        area = math.pi * (casing_id ** 2 - tubing_od ** 2) / 4
        sand_volume = area * fill_depth

        if unit_system == "Imperial":
            volume_bbl = sand_volume * 6.28981  # m³ to bbl
            sand_mass = volume_bbl * slurry_conc
            st.success(f"Sand Volume: {volume_bbl:.2f} bbl")
            st.info(f"Sand Mass: {sand_mass:.0f} lb")
        else:
            sand_mass = sand_volume * slurry_conc
            st.success(f"Sand Volume: {sand_volume:.2f} m³")
            st.info(f"Sand Mass: {sand_mass:.0f} kg")

# Sand Plug Calculator
st.subheader("Sand Plug Calculator")
with st.form("sand_plug_form"):
    hole_diameter = st.number_input(f"Hole Diameter ({diameter_unit})", min_value=0.0, step=0.1)
    plug_length = st.number_input(f"Plug Length ({length_unit})", min_value=0.0, step=0.1)
    slurry_conc_plug = st.number_input(f"Slurry Concentration ({slurry_conc_unit})", min_value=0.0, step=1.0, key="plug_slurry_conc")
    pump_rate = st.number_input(f"Pump Rate ({flow_rate_unit})", min_value=0.0, step=0.1)
    submitted3 = st.form_submit_button("Calculate Sand Plug")

    if submitted3:
        if unit_system == "Imperial":
            hole_diameter = hole_diameter / 39.37
            pump_rate = pump_rate * 5.615 / 60

        area = math.pi * (hole_diameter / 2) ** 2
        volume = area * plug_length

        if unit_system == "Imperial":
            volume_bbl = volume * 6.28981
            sand_mass = volume_bbl * slurry_conc_plug
            time_min = (volume_bbl / pump_rate) if pump_rate > 0 else 0
            st.success(f"Slurry Volume: {volume_bbl:.2f} bbl")
            st.info(f"Sand Mass: {sand_mass:.0f} lb")
            st.info(f"Pumping Time: {time_min:.2f} min")
        else:
            sand_mass = volume * slurry_conc_plug
            time_min = (volume / pump_rate) if pump_rate > 0 else 0
            st.success(f"Slurry Volume: {volume:.2f} m³")
            st.info(f"Sand Mass: {sand_mass:.0f} kg")
            st.info(f"Pumping Time: {time_min:.2f} min")
