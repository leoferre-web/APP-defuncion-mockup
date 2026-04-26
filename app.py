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

URL_LOGO = "https://raw.githubusercontent.com/leoferre-web/APP-defuncion-mockup/main/logo.png"

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def conectar_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = conectar_supabase()

# --- BASES DE DATOS DE VALIDACIÓN ---
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

# --- SESSION STATE ---
if 'causa_seleccionada' not in st.session_state:
    st.session_state['causa_seleccionada'] = ""
if 'proceso_exitoso' not in st.session_state:
    st.session_state['proceso_exitoso'] = False

def reiniciar_formulario():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- CLASE PDF ---
class CertificadoPDF(FPDF):
    def header(self):
        self.set_fill_color(230, 230, 230)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "INFORME ESTADISTICO DE DEFUNCION - PROVINCIA DE CORDOBA", 1, 1, 'C', True)
        self.ln(2)
    def seccion(self, titulo):
        self.set_fill_color(245, 245, 245)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 7, f" {titulo}", 1, 1, 'L', True)
        self.ln(1)
    def item(self, num, etiqueta, valor):
        self.set_font('Arial', 'B', 9)
        self.cell(40, 7, f"{num}- {etiqueta}: ", 0, 0)
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 7, str(valor), 0, 'L')

def enviar_correo(dest, pdf_content, nombre):
    try:
        remitente = st.secrets["email"]["remitente"]
        password  = st.secrets["email"]["password"]
        msg = MIMEMultipart()
        msg['From']    = remitente
        msg['To']      = dest
        msg['Subject'] = f"CERTIFICADO DIGITAL DEFUNCIÓN: {nombre}"
        msg.attach(MIMEText(f"Se adjunta certificado oficial validado de {nombre}.", 'plain'))
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename=Certificado_{nombre}.pdf")
        msg.attach(part)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(remitente, password)
        s.send_message(msg)
        s.quit()
        return True
    except Exception as e:
        st.error(f"Error en el envío de mail: {e}")
        return False

# =============================================================================
# CSS GLOBAL
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Source+Sans+3:wght@400;600;700&display=swap');

:root {
    --azul:      #003366;
    --celeste:   #0077cc;
    --cel-fondo: #e8f2fb;
    --gris-bg:   #f4f6f9;
    --gris-brd:  #d0d9e4;
}

html, body, .stApp {
    background-color: var(--gris-bg) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

#MainMenu, footer { visibility: hidden; }

.block-container { padding-top: 4rem !important; max-width: 860px !important; }

/* ── HEADER ── */
.cba-header {
    background: linear-gradient(135deg, #003366 0%, #1a4f8a 100%);
    border-bottom: 4px solid #c9a227;
    padding: 20px 28px;
    margin: 0 -1rem 0 -1rem;
    display: flex; align-items: center; gap: 20px;
    box-shadow: 0 3px 14px rgba(0,0,0,0.22);
}
.cba-logo-box {
    background: white; border-radius: 10px; padding: 8px 10px;
    min-width: 78px; min-height: 78px;
    display: flex; align-items: center; justify-content: center;
}
.cba-logo-box img { width: 62px; height: 62px; object-fit: contain; }
.cba-header-text h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 25px !important; color: white !important; margin: 0 !important;
}
.cba-badge {
    background: #c9a227; color: #003366; font-size: 10px; font-weight: 700;
    padding: 5px 14px; border-radius: 20px; margin-top: 6px; display: inline-block;
}

/* ── OPCIONES Y TEXTOS NEGROS ── */
div[data-testid="stMarkdownContainer"] p, 
.stWidget label p, 
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label p {
    color: #000000 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* ── CUADRO CIDI ── */
.cidi-box {
    background: var(--cel-fondo) !important; 
    border: 1.5px dashed var(--celeste) !important;
    border-radius: 8px; padding: 16px 20px;
    color: #000000 !important; /* Texto negro */
    font-weight: 700 !important;
    margin-bottom: 10px;
}

/* ── LABELS PRINCIPALES ── */
.stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label, .stTextArea label {
    font-weight: 700 !important;
    color: #000000 !important;
}

.badge-ok {
    display: inline-flex; align-items: center; gap: 7px;
    background: #e8f7ee; color: #155a2e; font-size: 12px; font-weight: 700;
    padding: 5px 13px; border-radius: 20px; border: 1px solid #a8dfc0;
}
.btn-confirmar .stButton > button {
    background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
    color: white !important; border-radius: 8px !important; font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================
st.markdown(f"""
<div class="cba-header">
    <div class="cba-logo-box"><img src="{URL_LOGO}"></div>
    <div class="cba-header-text">
        <h1>Ministerio de Salud</h1>
        <p style="color: white; margin:0;">Gobierno de la Provincia de Córdoba</p>
        <div class="cba-badge">Sistema Digital</div>
    </div>
</div>
<div style="height:4px; background: #c9a227; margin-bottom: 20px;"></div>
""", unsafe_allow_html=True)

if st.session_state['proceso_exitoso']:
    st.success("✅ Certificado generado con éxito")
    if st.button("CARGAR NUEVO"): reiniciar_formulario()
    st.stop()

# =============================================================================
# BLOQUES
# =============================================================================
with st.expander("📂 I. DATOS DEL REGISTRO"):
    c1, c2, c3, c4 = st.columns(4)
    dpto_reg = c1.text_input("Dpto")
    deleg_reg = c2.text_input("Delegación")
    acta_reg = c3.text_input("Acta")
    anio_reg = c4.text_input("Año")

with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    dni_f = st.text_input("3- Nro de Documento")
    nombre_defecto, domicilio_defecto = "", ""
    
    # RESTAURACIÓN DE ALERTA DNI
    if dni_f:
        if dni_f in DB_RENAPER:
            st.markdown(f'<div class="badge-ok">✅ Identidad Validada: {DB_RENAPER[dni_f]["nombre"]}</div>', unsafe_allow_html=True)
            nombre_defecto = DB_RENAPER[dni_f]['nombre']
            domicilio_defecto = DB_RENAPER[dni_f]['domicilio']
        else:
            st.warning("⚠️ DNI no encontrado en RENAPER. Complete manualmente.")
    
    nombre_f = st.text_input("1- Nombre Completo", value=nombre_defecto)
    c_f1, c_f2 = st.columns(2)
    sexo_f = c_f1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac = c_f2.date_input("6- Fecha Nacimiento")
    domicilio_f = st.text_input("10- Domicilio", value=domicilio_defecto)
    
    es_menor = st.checkbox("¿Es menor de 1 año?")
    if es_menor:
        em1, em2 = st.columns(2)
        edad_str = f"{em1.number_input('Meses',0)}m {em2.number_input('Días',0)}d"
        e_anios = 0
    else:
        e_anios = st.number_input("Años", 1, 120, 70)
        edad_str = f"{e_anios} años"

with st.expander("🩺 IV. CAUSAS"):
    forma_m = st.radio("23- Forma", ["No traumática", "Traumática"], horizontal=True)
    causa_a = st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
    intervalo = st.text_input("Intervalo")

with st.expander("🖋️ VIII. PROFESIONAL", expanded=True):
    col_m1, col_m2 = st.columns(2)
    mat_m = col_m1.text_input("Matrícula")
    nom_m_defecto = ""
    
    # RESTAURACIÓN DE ALERTA MATRÍCULA
    if mat_m:
        if mat_m in DB_REFES:
            st.markdown(f'<div class="badge-ok">✅ {DB_REFES[mat_m]}</div>', unsafe_allow_html=True)
            nom_m_defecto = "DR. CARLOS MEDICINA"
        else:
            st.error("❌ Matrícula no encontrada en REFES.")
            
    nom_m = col_m2.text_input("Nombre Médico", value=nom_m_defecto)
    email_dest = st.text_input("Email envío PDF")
    
    # AJUSTE VISUAL TEXTO CIDI
    st.markdown('<div class="cidi-box">🔐 Firma Digital — CiDi Córdoba</div>', unsafe_allow_html=True)
    firma_digital = st.checkbox("Confirmar Firma Digital (CiDi)")

st.markdown('<div class="btn-confirmar">', unsafe_allow_html=True)
confirmar = st.button("🔴 CONFIRMAR Y ENVIAR REGISTRO", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESAMIENTO ---
if confirmar:
    if nombre_f and causa_a and firma_digital and email_dest:
        try:
            # INSERCIÓN EN SUPABASE (RESTAURADA)
            res = supabase.table("certificados_defuncion").insert({
                "nombre_fallecido": nombre_f, "dni_fallecido": dni_f,
                "causa_directa": causa_a, "medico_nombre": nom_m, "email_envio": email_dest
            }).execute()
            
            # PDF Y MAIL
            pdf = CertificadoPDF()
            pdf.add_page()
            pdf.seccion("RESUMEN"); pdf.item("1", "Nombre", nombre_f); pdf.item("26", "Causa", causa_a)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            if enviar_correo(email_dest, pdf_bytes, nombre_f):
                st.session_state['proceso_exitoso'] = True
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("⚠️ Faltan datos obligatorios o firma.")
