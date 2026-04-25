import streamlit as st
import datetime
import time
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from supabase import create_client, Client

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Defunción Digital - Córdoba", layout="centered", page_icon="⚖️")

# URL RAW del logo en tu GitHub
URL_LOGO = "https://raw.githubusercontent.com/leoferre-web/APP-defuncion-mockup/main/logo.png"

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def conectar_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = conectar_supabase()

# --- DATOS DE VALIDACIÓN ---
DB_RENAPER = {"123": {"nombre": "JUAN PEREZ", "domicilio": "AV. COLON 1234, CORDOBA"}}
DB_REFES = {"12345": "DR. CARLOS MEDICINA (MATRÍCULA ACTIVA)"}

CIE10_DB = {
    "INFARTO AGUDO DE MIOCARDIO": "I21.9", "INSUFICIENCIA CARDIACA": "I50.9", 
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10",
    "SHOCK CARDIOGENICO": "R57.0", "EMBOLIA PULMONAR": "I26.9", "ARRITMIA CARDIACA": "I49.9",
    "ANEURISMA DE AORTA": "I71.9", "NEUMONIA": "J18.9", "EPOC": "J44.9", 
    "COVID-19": "U07.1", "ASMA": "J45.9", "INSUFICIENCIA RESPIRATORIA": "J96.0", 
    "EDEMA PULMONAR": "J81", "BRONQUITIS AGUDA": "J20.9", "SEPSIS": "A41.9", 
    "SHOCK SEPTICO": "A41.9", "TUBERCULOSIS": "A15.0", "HIV/SIDA": "B24", 
    "DENGUE GRAVE": "A91", "MENINGITIS": "G03.9", "INFECCION URINARIA (UROPSEPSIS)": "N39.0",
    "CANCER DE PULMON": "C34.9", "CANCER DE COLON": "C18.9", "CANCER DE MAMA": "C50.9", 
    "CANCER DE PROSTATA": "C61", "LEUCEMIA": "C91.9", "CANCER DE PANCREAS": "C25.9",
    "CANCER DE ESTOMAGO": "C16.9", "LINFOMA": "C85.9", "DIABETES TIPO 2": "E11.9", 
    "INSUFICIENCIA RENAL CRONICA": "N18.9", "CIRROSIS HEPATICA": "K74.6", 
    "CETOACIDOSIS DIABETICA": "E11.1", "INSUFICIENCIA HEPATICA": "K72.9",
    "TRAUMATISMO CRANEOENCEFALICO": "S06.9", "HERIDA POR ARMA DE FUEGO": "W34", 
    "POLITRAUMATISMO": "T07", "AHOGAMIENTO": "W74", "ASFIXIA MECANICA": "W84", 
    "INTOXICACION POR MONOXIDO DE CARBONO": "T58", "QUEMADURAS GRAVES": "T30.0", 
    "CAIDA DE ALTURA": "W19", "ACCIDENTE DE TRANSITO": "V89.2", "SUICIDIO": "X84",
    "ALZHEIMER": "G30.9", "DEMENCIA SENIL": "F03", "PARKINSON": "G20",
    "MUERTE SUBITA INFANTIL": "R95", "PARO CARDIORRESPIRATORIO NO ESPECIFICADO": "I46.9",
    "SENILIDAD / VEJEZ": "R54", "EMBARAZO ECTOPICO": "O00.9"
}

# Session States
if 'causa_seleccionada' not in st.session_state: st.session_state['causa_seleccionada'] = ""
if 'proceso_exitoso' not in st.session_state: st.session_state['proceso_exitoso'] = False

# --- CSS E INYECCIÓN DE ESTILO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Source+Sans+3:wght@300;400;500;600&display=swap');
    
    :root {
        --azul-oscuro: #003366; --azul-medio: #1a4f8a; --celeste-accion: #0077cc;
        --celeste-fondo: #e8f2fb; --dorado: #c9a227; --gris-fondo: #f4f6f9;
    }

    .stApp { background-color: var(--gris-fondo); font-family: 'Source Sans 3', sans-serif; }
    
    .header-container {
        background: linear-gradient(135deg, #003366 0%, #1a4f8a 100%);
        border-bottom: 4px solid var(--dorado); padding: 2rem;
        margin: -5rem -2rem 2rem -2rem; color: white; text-align: center;
    }

    .logo-box {
        background: white; display: inline-block; padding: 8px;
        border-radius: 10px; margin-bottom: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .badge-sistema {
        background-color: var(--dorado); color: var(--azul-oscuro);
        padding: 4px 15px; border-radius: 20px; font-weight: 700;
        font-size: 12px; text-transform: uppercase; display: inline-block; margin-top: 10px;
    }

    .stExpander {
        background-color: white !important; border: 1px solid #d0d9e4 !important;
        border-radius: 10px !important; margin-bottom: 1rem !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
        color: white !important; border-radius: 50px !important;
        padding: 14px 48px !important; font-weight: 700 !important; width: 100%;
    }

    .cidi-box {
        background-color: var(--celeste-fondo); border: 2px dashed var(--celeste-accion);
        padding: 15px; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="logo-box"><img src="{URL_LOGO}" width="100"></div>
        <h1 style="font-family: 'Playfair Display'; margin:0;">Ministerio de Salud</h1>
        <p style="opacity: 0.75; margin:0; text-transform: uppercase;">Gobierno de la Provincia de Córdoba</p>
        <div class="badge-sistema">Sistema Digital</div>
    </div>
    <div style="height: 4px; background-color: #c9a227; margin: -2rem -2rem 2rem -2rem;"></div>
""", unsafe_allow_html=True)

if st.session_state['proceso_exitoso']:
    st.success("✅ Certificado generado con éxito")
    if st.button("CARGAR NUEVO CERTIFICADO"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.stop()

# --- FORMULARIO ---
with st.expander("📂 SECCIÓN I: DATOS DEL REGISTRO", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    dpto_reg = c1.text_input("Dpto/Partido")
    deleg_reg = c2.text_input("Delegación")
    acta_reg = c3.text_input("Acta Nro")
    anio_reg = c4.text_input("Año")

with st.expander("👤 SECCIÓN II: DATOS DEL FALLECIDO", expanded=True):
    c_dni, c_v = st.columns([3, 1])
    dni_f = c_dni.text_input("Nro Documento (RENAPER)")
    btn_v = c_v.button("Validar", use_container_width=True)
    
    nombre_def, dom_def = "", ""
    if dni_f == "123" or (btn_v and dni_f == "123"):
        st.markdown('<small style="color:green;">● Validado por RENAPER</small>', unsafe_allow_html=True)
        nombre_def, dom_def = "JUAN PEREZ", "AV. COLON 1234, CORDOBA"
    
    nombre_f = st.text_input("Apellido/s y Nombre/s", value=nombre_def)
    c1, c2 = st.columns(2)
    sexo_f = c1.radio("Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac = c2.date_input("Fecha Nacimiento", value=datetime.date(1960,1,1))
    domicilio_f = st.text_input("Domicilio Real", value=dom_def)
    
    es_menor = st.checkbox("¿Es menor de 1 año?")
    if es_menor:
        em1, em2 = st.columns(2); e_meses = em1.number_input("Meses", 0, 11); e_dias = em2.number_input("Días", 0, 30)
        edad_str = f"{e_meses}m {e_dias}d"
    else:
        e_anios = st.number_input("Años cumplidos", 0, 120, value=70); edad_str = f"{e_anios} años"

with st.expander("💼 SECCIÓN III: DATOS 14 AÑOS Y MÁS"):
    st.selectbox("Estado Civil", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"])
    st.text_input("Ocupación principal")

with st.expander("🩺 SECCIÓN IV: CAUSAS DE DEFUNCIÓN"):
    busc_cie = st.text_input("🔍 BUSCADOR CIE-10").upper()
    if busc_cie:
        sugs = {d: c for d, c in CIE10_DB.items() if busc_cie in d}
        cols = st.columns(2)
        for i, (desc, cod) in enumerate(sugs.items()):
            if i < 10:
                if cols[i%2].button(f"📌 {cod} - {desc}", use_container_width=True, key=desc):
                    st.session_state['causa_seleccionada'] = f"{cod} - {desc}"; st.rerun()
    
    causa_a = st.text_area("Causa Directa (A)", value=st.session_state['causa_seleccionada'])
    causa_b = st.text_input("Causa Antecedente (B)")

with st.expander("⚠️ SECCIÓN V: SITUACIONES ESPECIALES"):
    st.radio("¿Hubo autopsia?", ["No", "Sí", "Se ignora"], horizontal=True)

with st.expander("🖋️ SECCIÓN VIII: PROFESIONAL", expanded=True):
    c1, c2 = st.columns(2)
    mat_m = c1.text_input("Matrícula Profesional")
    nom_m_def = ""
    if mat_m == "12345": st.success("Médico: DR. CARLOS MEDICINA"); nom_m_def = "DR. CARLOS MEDICINA"
    nom_m = c2.text_input("Nombre Médico", value=nom_m_def)
    email_dest = st.text_input("Email para recibir PDF")
    st.markdown('<div class="cidi-box"><strong>Firma Digital CiDi</strong><br><small>Autorizo este registro oficial.</small></div>', unsafe_allow_html=True)
    firma_digital = st.checkbox("Firmar")

# --- GUARDADO ---
if st.button("🔴 CONFIRMAR Y ENVIAR REGISTRO OFICIAL"):
    if nombre_f and causa_a and firma_digital and email_dest:
        with st.spinner("Guardando en Supabase..."):
            datos = {
                "nombre_fallecido": nombre_f, "dni_fallecido": dni_f, "sexo_f": sexo_f,
                "causa_directa": causa_a, "medico_nombre": nom_m, "email_envio": email_dest
            }
            try:
                supabase.table("certificados_defuncion").insert(datos).execute()
                st.session_state['proceso_exitoso'] = True; st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    else: st.error("Complete los campos obligatorios.")
