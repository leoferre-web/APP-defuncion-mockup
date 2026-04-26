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

# --- BASES DE DATOS DE VALIDACIÓN (Simuladas) ---
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
# CSS GLOBAL — DISEÑO INSTITUCIONAL PROVINCIA DE CÓRDOBA
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Source+Sans+3:wght@400;600;700&display=swap');

:root {
    --azul:      #003366;
    --azul-m:    #1a4f8a;
    --celeste:   #0077cc;
    --cel-fondo: #e8f2fb;
    --dorado:    #c9a227;
    --gris-bg:   #f4f6f9;
    --gris-brd:  #d0d9e4;
}

html, body, .stApp {
    background-color: var(--gris-bg) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* SOLO BAJAMOS EL CONTENIDO PARA QUE EL LOGO NO SE CORTE */
.block-container { 
    padding-top: 5rem !important; 
    max-width: 860px !important; 
}

/* ── HEADER ── */
.cba-header {
    background: linear-gradient(135deg, #003366 0%, #1a4f8a 100%);
    border-bottom: 4px solid #c9a227;
    padding: 20px 28px;
    margin: -1rem -1rem 0 -1rem;
    display: flex; align-items: center; gap: 20px;
    box-shadow: 0 3px 14px rgba(0,0,0,0.22);
}
.cba-logo-box {
    background: white; border-radius: 10px; padding: 8px 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15); flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    min-width: 78px; min-height: 78px;
}
.cba-logo-box img { width: 62px; height: 62px; object-fit: contain; }
.cba-header-text h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 25px !important; font-weight: 600 !important;
    color: white !important; margin: 0 0 3px 0 !important; line-height: 1.15 !important;
}
.cba-header-text p {
    font-size: 11px !important; color: rgba(255,255,255,0.75) !important;
    margin: 0 !important; text-transform: uppercase !important; letter-spacing: 1.3px !important;
}
.cba-badge {
    background: #c9a227; color: #003366; font-size: 10px; font-weight: 700;
    padding: 5px 14px; border-radius: 20px; letter-spacing: 1px;
    text-transform: uppercase; display: inline-block; margin-top: 6px;
    font-family: 'Source Sans 3', sans-serif;
}
.cba-progress {
    height: 4px;
    background: linear-gradient(90deg, #c9a227 35%, #d0d9e4 35%);
    margin: 0 -1rem 1.6rem -1rem;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid var(--gris-brd) !important;
    border-radius: 10px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 1px 5px rgba(0,30,60,0.07) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] > details > summary {
    background: var(--cel-fondo) !important;
    border-bottom: 1px solid var(--gris-brd) !important;
    padding: 12px 18px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    color: #003366 !important;
}
[data-testid="stExpander"] > details > summary:hover { background: #cfe0f5 !important; }
[data-testid="stExpander"] > details > div { padding: 18px 20px 22px !important; }

/* ── MODIFICACIÓN: COLOR DE TEXTO PARA RADIO Y CHECKBOX (LETRAS VISIBLES) ── */
div[data-testid="stRadio"] label p, 
div[data-testid="stCheckbox"] label p {
    color: #262730 !important; /* Color oscuro para que se vea */
    font-weight: 500 !important;
}

/* ── LABELS DE LOS CAMPOS ── */
.stTextInput label, .stNumberInput label, .stDateInput label, .stTimeInput label, 
.stSelectbox label, .stTextArea label, .stRadio label, .stCheckbox label {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput input,
.stTimeInput input,
.stTextArea textarea {
    border: 1.5px solid var(--gris-brd) !important;
    border-radius: 6px !important;
    color: #111827 !important;
    background: white !important;
}

/* ── BOTONES ── */
.stButton > button {
    background: var(--celeste) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}
.stButton > button:hover { background: #005fa3 !important; }

.btn-confirmar .stButton > button {
    background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 14px rgba(192,57,43,0.35) !important;
    padding: 0.75rem 2rem !important;
}

/* ── BADGE VALIDACIÓN ── */
.badge-ok {
    display: inline-flex; align-items: center; gap: 7px;
    background: #e8f7ee; color: #155a2e;
    font-size: 12px; font-weight: 700;
    padding: 5px 13px; border-radius: 20px;
    border: 1px solid #a8dfc0;
    margin: 4px 0 8px 0;
}
.badge-dot { width: 8px; height: 8px; background: #27ae60; border-radius: 50%; display: inline-block; }

/* ── ÁREA FIRMA CiDi ── */
.cidi-box {
    background: var(--cel-fondo); border: 1.5px dashed var(--celeste);
    border-radius: 8px; padding: 16px 20px;
    display: flex; align-items: center; gap: 14px; margin-bottom: 10px;
}
.cidi-icon {
    width: 44px; height: 44px; background: var(--celeste); border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
/* MODIFICACIÓN: TEXTO CIDI OSCURO */
.cidi-text p     { margin: 0; font-weight: 700; color: #003366 !important; font-size: 14px; }
.cidi-text small { color: #1e3a5f !important; font-size: 12px; }

/* ── FOOTER ── */
.footer-legal {
    text-align: center; margin-top: 10px;
    font-size: 11px; color: #4a5568;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================
st.markdown(f"""
<div class="cba-header">
    <div class="cba-logo-box">
        <img src="{URL_LOGO}" alt="Gobierno de Córdoba">
    </div>
    <div class="cba-header-text">
        <h1>Ministerio de Salud</h1>
        <p>Gobierno de la Provincia de Córdoba</p>
        <div class="cba-badge">Sistema Digital</div>
    </div>
</div>
<div class="cba-progress"></div>
""", unsafe_allow_html=True)

# PANTALLA DE ÉXITO
if st.session_state['proceso_exitoso']:
    st.success("✅ Certificado generado con éxito")
    if st.button("CARGAR NUEVO CERTIFICADO", use_container_width=True):
        reiniciar_formulario()
    st.stop()

# BLOQUE I — DATOS DEL REGISTRO
with st.expander("📂  I. DATOS DEL REGISTRO"):
    c1, c2, c3, c4 = st.columns(4)
    dpto_reg  = c1.text_input("Dpto/Partido")
    deleg_reg = c2.text_input("Delegación")
    acta_reg  = c3.text_input("Acta Nro")
    anio_reg  = c4.text_input("Año")

# BLOQUE II — DATOS DEL FALLECIDO
with st.expander("👤  II. DATOS DEL FALLECIDO", expanded=True):
    dni_f = st.text_input("3- Nro de Documento (Validación RENAPER)")
    nombre_defecto, domicilio_defecto = "", ""

    if dni_f in DB_RENAPER:
        nombre_defecto    = DB_RENAPER[dni_f]['nombre']
        domicilio_defecto = DB_RENAPER[dni_f]['domicilio']
        st.markdown(f'<div class="badge-ok"><span class="badge-dot"></span>Identidad Validada — {nombre_defecto}</div>', unsafe_allow_html=True)

    nombre_f    = st.text_input("1- Apellido/s y Nombre/s", value=nombre_defecto)
    c_f1, c_f2 = st.columns(2)
    sexo_f      = c_f1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac       = c_f2.date_input("6- Fecha Nacimiento", value=datetime.date(1960, 1, 1))
    domicilio_f = st.text_input("10- Domicilio Real", value=domicilio_defecto)
    es_menor = st.checkbox("¿Es menor de 1 año?")
    
    if es_menor:
        em1, em2, em3, em4 = st.columns(4)
        e_meses = em1.number_input("Meses", 0, 11)
        e_dias = em2.number_input("Días", 0, 30)
        e_horas = em3.number_input("Horas", 0, 23)
        e_minutos = em4.number_input("Minutos", 0, 59)
        edad_str = f"{e_meses}m {e_dias}d {e_horas}h {e_minutos}min"
        e_anios = 0
    else:
        e_anios = st.number_input("Años cumplidos", 1, 120, value=70)
        edad_str = f"{e_anios} años"

    id_gen = st.selectbox("17- Identidad de Género", ["Mujer", "Varón", "Trans", "Ninguna", "Ignorado"])
    pueblo = st.radio("18- ¿Pueblo originario?", ["No", "Si", "Se ignora"], horizontal=True)

# BLOQUE IV — CAUSAS
with st.expander("🩺  IV. CAUSAS DE LA DEFUNCIÓN"):
    forma_m = st.radio("23- Forma de morir", ["No traumática", "Traumática"], horizontal=True)
    causa_a = st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
    intervalo = st.text_input("Intervalo enfermedad-muerte")

# BLOQUE V — SITUACIONES ESPECIALES
with st.expander("⚠️  V. SITUACIONES ESPECIALES"):
    autopsia = st.radio("33- ¿Se solicitó autopsia?", ["No", "Si", "Se desconoce"])

# BLOQUE VIII — PROFESIONAL
with st.expander("🖋️  VIII. PROFESIONAL", expanded=True):
    col_m1, col_m2 = st.columns(2)
    mat_m = col_m1.text_input("Matrícula Profesional")
    nom_m = col_m2.text_input("Nombre Médico")
    email_dest = st.text_input("Email para recibir el PDF")

    st.markdown("""
    <div class="cidi-box">
        <div class="cidi-icon">🔐</div>
        <div class="cidi-text">
            <p>Firma Digital — CiDi Córdoba</p>
            <small>Requiere autenticación con su cuenta CiDi provincial.</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    firma_digital = st.checkbox("Firma Digital (CiDi Córdoba)")

st.markdown('<div class="btn-confirmar">', unsafe_allow_html=True)
confirmar = st.button("🔴  CONFIRMAR Y ENVIAR REGISTRO OFICIAL", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if confirmar:
    if nombre_f and causa_a and firma_digital and email_dest:
        st.session_state['proceso_exitoso'] = True
        st.rerun()
