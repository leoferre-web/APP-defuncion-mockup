import streamlit as st
import datetime
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from supabase import create_client

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Defunción Digital - Córdoba", layout="centered", page_icon="⚖️")

URL_LOGO = "https://raw.githubusercontent.com/leoferre-web/APP-defuncion-mockup/main/logo.png"

# --- CSS PARA BAJAR EL ENCABEZADO SIN QUE SE CORTE ---
st.markdown("""
<style>
    /* 1. Bajamos todo el contenedor principal para que nada se corte arriba */
    .block-container {
        padding-top: 100px !important; 
    }

    /* 2. Estilo del Header: Eliminamos márgenes negativos para que el logo y el título bajen juntos */
    .cba-header {
        background: linear-gradient(135deg, #003366 0%, #1a4f8a 100%);
        border-bottom: 4px solid #c9a227;
        padding: 25px;
        display: flex;
        align-items: center;
        gap: 20px;
        border-radius: 8px 8px 0 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .cba-logo-box {
        background: white;
        border-radius: 8px;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
    }

    .cba-logo-box img {
        width: 100%;
        height: auto;
    }

    .cba-header-text h1 {
        color: white !important;
        font-size: 24px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .cba-header-text p {
        color: rgba(255,255,255,0.8) !important;
        margin: 0 !important;
        font-size: 14px !important;
    }

    .cba-progress {
        height: 5px;
        background: #c9a227;
        margin-bottom: 30px;
        border-radius: 0 0 8px 8px;
    }

    /* Ocultar elementos innecesarios de Streamlit que ensucian el diseño */
    #MainMenu, footer, header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO (Logo y Título juntos) ---
st.markdown(f"""
<div class="cba-header">
    <div class="cba-logo-box">
        <img src="{URL_LOGO}">
    </div>
    <div class="cba-header-text">
        <h1>Ministerio de Salud</h1>
        <p>Gobierno de la Provincia de Córdoba</p>
    </div>
</div>
<div class="cba-progress"></div>
""", unsafe_allow_html=True)

# --- RESTO DEL FORMULARIO ---
with st.expander("📂 I. DATOS DEL REGISTRO", expanded=False):
    st.text_input("Departamento")

with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    st.text_input("Nombre Completo")
    st.text_input("DNI")

with st.expander("🖋️ VIII. PROFESIONAL", expanded=True):
    st.text_input("Matrícula")
    st.text_input("Nombre Médico")
    st.checkbox("Firma Digital (CiDi Córdoba)")

st.button("ENVIAR REGISTRO")
