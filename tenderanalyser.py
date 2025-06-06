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
        all_text += data.astype(str).apply(lambda x: ' '.join(x), axis=1).st_
