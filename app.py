import streamlit as st
from datetime import datetime
from dateutil import parser
import pytz

# Configuración de página con estética limpia
st.set_page_config(page_title="ChronoShift | UTC Converter", page_icon="🕒", layout="centered")

# CSS personalizado para minimalismo
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    .stTextInput>div>div>input { background-color: #ffffff; border-radius: 8px; }
    .stButton>button { 
        width: 100%; 
        background-color: #1e3a8a; 
        color: white; 
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #3b82f6; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕒 ChronoShift")
st.caption("Minimalist Timezone to UTC Standardizer")
st.write("---")

# Input de fecha
date_input = st.text_input("Paste your local date", placeholder="e.g. 2026-01-30 22:00 or 30/01/26 10PM")

# Selector de Timezone con buscador
col1, col2 = st.columns([2, 1])
with col1:
    source_tz = st.selectbox(
        "Source Timezone", 
        pytz.common_timezones, 
        index=pytz.common_timezones.index('America/Argentina/Tucuman')
    )

if date_input:
    try:
        # El parser de dateutil es "mágico" y detecta casi cualquier formato
        parsed_dt = parser.parse(date_input)
        
        # Asignar zona origen
        local_tz = pytz.timezone(source_tz)
        local_dt = local_tz.localize(parsed_dt)
        
        # Convertir a UTC
        utc_dt = local_dt.astimezone(pytz.utc)
        
        st.markdown("### Result (UTC)")
        utc_result = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
        st.code(utc_result, language="text")
        
        st.success(f"Successfully converted from {source_tz}")
        
    except Exception:
        st.error("Invalid format. Please try: YYYY-MM-DD HH:MM")

st.write("---")
st.markdown("Created by **Ulises Chustek** | Data Processing Specialist")