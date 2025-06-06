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
        text += page.extract_text() + "\n"
    return text

def extract_text_word(file):
    text = docx2txt.process(file)
    return text

def extract_text_excel(file):
    df = pd.read_excel(file, sheet_name=None)
    all_text = ""
    for sheet, data in df.items():
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
        text = extract_text_word(uploaded_fi_
