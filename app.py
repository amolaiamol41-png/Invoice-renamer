import streamlit as st
import pdfplumber
import pandas as pd
import easyocr
import re
import os
import io
import zipfile
import pytesseract
from PIL import Image

# Initialize OCR (Cache it so it doesn't reload every time)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def extract_text(file, extension):
    # ... (rest of code)
    elif extension in ['jpg', 'png', 'jpeg']:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    return text

def parse_metadata(text):
    # Search for Invoice Number
    inv_match = re.search(r'(?:Invoice|Inv|No|#)[:\s]*(\w+)', text, re.I)
    # Search for Date (Formats like 01/01/2023 or 01-01-2023)
    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
    
    vendor = text.split('\n')[0][:15].strip() # Takes first line as Vendor
    inv_no = inv_match.group(1) if inv_match else "UnknownInv"
    date = date_match.group(1).replace("/", "-") if date_match else "UnknownDate"
    
    return f"{vendor}_{date}_{inv_no}"

# --- UI Layout ---
st.set_page_config(page_title="AI File Renamer")
st.title("📂 Batch Invoice Renamer")
st.write("Upload PDF, Images (Handwritten/Digital), or Excel files.")

uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

if uploaded_files:
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file in uploaded_files:
            ext = file.name.split('.')[-1].lower()
            
            with st.spinner(f'Processing {file.name}...'):
                content = extract_text(file, ext)
                new_base_name = parse_metadata(content)
                new_filename = f"{new_base_name}.{ext}"
                
                # Show results in UI
                st.write(f"✅ **{file.name}** → `{new_filename}`")
                
                # Add to ZIP
                file.seek(0)
                zip_file.writestr(new_filename, file.read())

    st.divider()
    st.download_button(
        label="Download All Renamed Files (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="renamed_files.zip",
        mime="application/zip"
    )
