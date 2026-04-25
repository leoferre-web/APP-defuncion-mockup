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
st.set_page_config(
    page_title="Sistema de Defunción Digital - Córdoba",
    layout="centered",
    page_icon="⚖️"
)

URL_LOGO = "https://raw.githubusercontent.com/leoferre-web/APP-defuncion-mockup/main/logo.png"

# --- CONEXIÓN A SUPABASE ---
@st.cache_resource
def conectar_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = conectar_supabase()

# --- DATOS DE VALIDACIÓN ---
DB_RENAPER = {
    "123": {"nombre": "JUAN PEREZ", "domicilio": "AV. COLON 1234, CORDOBA"}
}
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
if 'renaper_validado' not in st.session_state:
    st.session_state['renaper_validado'] = False
if 'nombre_renaper' not in st.session_state:
    st.session_state['nombre_renaper'] = ""
if 'dom_renaper' not in st.session_state:
    st.session_state['dom_renaper'] = ""

# =============================================================================
# CSS GLOBAL - DISEÑO INSTITUCIONAL PROVINCIA DE CÓRDOBA
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Source+Sans+3:wght@300;400;500;600&display=swap');

/* ── Variables ── */
:root {
    --azul:      #003366;
    --azul-m:    #1a4f8a;
    --celeste:   #0077cc;
    --cel-fondo: #e8f2fb;
    --dorado:    #c9a227;
    --dor-fondo: #f5e9c0;
    --gris-bg:   #f4f6f9;
    --gris-brd:  #d0d9e4;
    --txt:       #1a2b3c;
    --txt-sec:   #4a6080;
    --radio:     6px;
}

/* ── Base ── */
html, body, .stApp {
    background-color: var(--gris-bg) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    color: var(--txt) !important;
}

/* ── Ocultar elementos Streamlit por defecto ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 860px !important; }

/* ── HEADER ── */
.cba-header {
    background: linear-gradient(135deg, #003366 0%, #1a4f8a 100%);
    border-bottom: 4px solid #c9a227;
    padding: 22px 32px;
    margin: -1rem -1rem 0 -1rem;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 3px 14px rgba(0,0,0,0.2);
}

.cba-logo-box {
    background: white;
    border-radius: 10px;
    padding: 8px 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 80px;
    min-height: 80px;
}

.cba-logo-box img { width: 64px; height: 64px; object-fit: contain; }

.cba-header-text { flex: 1; }

.cba-header-text h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 26px !important;
    font-weight: 600 !important;
    color: white !important;
    margin: 0 0 4px 0 !important;
    line-height: 1.15 !important;
    letter-spacing: 0.3px !important;
}

.cba-header-text p {
    font-size: 12px !important;
    color: rgba(255,255,255,0.72) !important;
    margin: 0 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    font-weight: 300 !important;
}

.cba-badge {
    background: #c9a227;
    color: #003366;
    font-size: 10px;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    align-self: flex-start;
    margin-top: 4px;
    white-space: nowrap;
    font-family: 'Source Sans 3', sans-serif;
}

/* ── Barra dorada de progreso debajo del header ── */
.cba-progress {
    height: 4px;
    background: linear-gradient(90deg, #c9a227 35%, #d0d9e4 35%);
    margin: 0 -1rem 1.8rem -1rem;
}

/* ── SECCIÓN CARDS (reemplaza los expanders de Streamlit) ── */
.sec-card {
    background: white;
    border: 1px solid var(--gris-brd);
    border-radius: 10px;
    margin-bottom: 16px;
    overflow: hidden;
    box-shadow: 0 1px 5px rgba(0,30,60,0.07);
}

.sec-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 13px 18px;
    background: var(--cel-fondo);
    border-bottom: 1px solid var(--gris-brd);
}

.sec-icon {
    width: 34px; height: 34px;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 16px;
}

.sec-num {
    font-size: 10px; font-weight: 700; color: var(--celeste);
    letter-spacing: 1.2px; text-transform: uppercase;
    font-family: 'Source Sans 3', sans-serif;
    line-height: 1;
}

.sec-title {
    font-size: 14px; font-weight: 600; color: var(--azul);
    font-family: 'Source Sans 3', sans-serif;
}

.sec-body { padding: 20px 22px 24px; }

/* ── Expanders nativos de Streamlit - override ── */
[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid var(--gris-brd) !important;
    border-radius: 10px !important;
    margin-bottom: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 5px rgba(0,30,60,0.07) !important;
}

[data-testid="stExpander"] > details > summary {
    background: var(--cel-fondo) !important;
    border-bottom: 1px solid var(--gris-brd) !important;
    padding: 12px 18px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--azul) !important;
}

[data-testid="stExpander"] > details > summary:hover {
    background: #d4e8f8 !important;
}

[data-testid="stExpander"] > details {
    padding: 0 !important;
}

[data-testid="stExpander"] > details > div {
    padding: 18px 20px 22px !important;
}

/* ── Inputs, selects ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    border: 1.5px solid var(--gris-brd) !important;
    border-radius: var(--radio) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 14px !important;
    color: var(--txt) !important;
    background: white !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--celeste) !important;
    box-shadow: 0 0 0 3px rgba(0,119,204,0.12) !important;
}

/* Labels de campos */
.stTextInput label, .stNumberInput label, .stDateInput label,
.stSelectbox label, .stTextArea label, .stRadio label,
.stCheckbox label {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--txt-sec) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ── Botones ── */
/* Botón principal (confirmar) */
div[data-testid="stButton"]:has(button[kind="primary"]) button,
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px 48px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(192,57,43,0.35) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    transition: box-shadow 0.15s !important;
}

/* Botones secundarios (Validar, Verificar, CIE-10) */
.stButton > button {
    background: var(--celeste) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radio) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: background 0.15s !important;
}

.stButton > button:hover {
    background: var(--azul-m) !important;
}

/* ── Badge RENAPER ── */
.renaper-ok {
    display: inline-flex; align-items: center; gap: 6px;
    background: #e8f7ee; color: #1a7a40;
    font-size: 12px; font-weight: 700;
    padding: 5px 12px; border-radius: 20px;
    border: 1px solid #a8dfc0;
    font-family: 'Source Sans 3', sans-serif;
    margin-top: 4px;
}

.renaper-dot {
    width: 8px; height: 8px; background: #27ae60;
    border-radius: 50%; display: inline-block;
}

/* ── Área Firma CiDi ── */
.cidi-box {
    background: var(--cel-fondo);
    border: 1.5px dashed var(--celeste);
    border-radius: var(--radio);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 8px;
}

.cidi-icon {
    width: 44px; height: 44px;
    background: var(--celeste);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}

.cidi-text p { margin: 0; font-weight: 600; color: var(--azul); font-size: 14px; }
.cidi-text small { color: var(--txt-sec); font-size: 12px; }

/* ── Success/Error ── */
.stSuccess, .stAlert {
    border-radius: var(--radio) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── Footer legal ── */
.footer-legal {
    text-align: center;
    margin-top: 10px;
    font-size: 11px;
    color: var(--txt-sec);
    font-family: 'Source Sans 3', sans-serif;
}

/* ── Divider ── */
.cba-divider {
    border: none;
    border-top: 1px solid var(--gris-brd);
    margin: 16px 0;
}

/* ── Subtítulos de subsección ── */
.subsec-label {
    font-size: 11px; font-weight: 700; color: var(--txt-sec);
    text-transform: uppercase; letter-spacing: 1px;
    font-family: 'Source Sans 3', sans-serif;
    margin: 14px 0 8px 0;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--celeste) !important; }

/* ── Radio buttons ── */
.stRadio > div { gap: 12px !important; }

/* ── Número de campo CIE10 tag ── */
.cie-tag {
    display: inline-block;
    background: var(--cel-fondo);
    color: var(--celeste);
    border: 1px solid #b5d4f4;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    font-family: 'Source Sans 3', monospace;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER INSTITUCIONAL
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

# =============================================================================
# PANTALLA DE ÉXITO
# =============================================================================
if st.session_state['proceso_exitoso']:
    st.success("✅ Certificado de defunción generado y enviado con éxito.")
    if st.button("CARGAR NUEVO CERTIFICADO"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# =============================================================================
# SECCIÓN I — DATOS DEL REGISTRO
# =============================================================================
st.markdown("""
<div class="sec-card">
  <div class="sec-header">
    <div class="sec-icon" style="background:#003366;">📁</div>
    <div>
      <div class="sec-num">Sección I</div>
      <div class="sec-title">Datos del Registro</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("▸ Ver / ocultar campos del registro", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    dpto_reg  = c1.text_input("Dpto / Partido")
    deleg_reg = c2.text_input("Delegación")
    acta_reg  = c3.text_input("Acta Nro")
    anio_reg  = c4.text_input("Año", value=str(datetime.date.today().year))

# =============================================================================
# SECCIÓN II — DATOS DEL FALLECIDO
# =============================================================================
st.markdown("""
<div class="sec-card">
  <div class="sec-header">
    <div class="sec-icon" style="background:#003366;">👤</div>
    <div>
      <div class="sec-num">Sección II</div>
      <div class="sec-title">Datos del Fallecido</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("▸ Ver / ocultar datos del fallecido", expanded=True):

    # — DNI + Validación RENAPER
    c_dni, c_btn = st.columns([3, 1])
    dni_f   = c_dni.text_input("3 — Nro de Documento  ★", placeholder="Ingrese DNI / CUIL")
    validar = c_btn.button("Validar RENAPER", use_container_width=True)

    if validar and dni_f:
        if dni_f in DB_RENAPER:
            st.session_state['renaper_validado'] = True
            st.session_state['nombre_renaper']   = DB_RENAPER[dni_f]["nombre"]
            st.session_state['dom_renaper']      = DB_RENAPER[dni_f]["domicilio"]
        else:
            st.session_state['renaper_validado'] = False
            st.warning("DNI no encontrado en RENAPER.")

    if st.session_state['renaper_validado']:
        st.markdown(
            '<div class="renaper-ok"><span class="renaper-dot"></span> Validado por RENAPER</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr class="cba-divider">', unsafe_allow_html=True)

    # — Nombre
    nombre_f = st.text_input(
        "1 — Apellido/s y Nombre/s  ★",
        value=st.session_state['nombre_renaper'],
        placeholder="Según documento de identidad"
    )

    # — Sexo + Fecha
    c1, c2 = st.columns(2)
    sexo_f = c1.radio("5 — Sexo registral", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac  = c2.date_input("6 — Fecha de Nacimiento  ★", value=datetime.date(1960, 1, 1))

    # — Domicilio
    domicilio_f = st.text_input(
        "10 — Domicilio Real",
        value=st.session_state['dom_renaper'],
        placeholder="Calle, N.°, localidad, provincia"
    )

    st.markdown('<hr class="cba-divider">', unsafe_allow_html=True)

    # — Edad
    es_menor = st.checkbox("¿Es menor de 1 año?")
    if es_menor:
        em1, em2 = st.columns(2)
        e_meses  = em1.number_input("Meses cumplidos", 0, 11, step=1)
        e_dias   = em2.number_input("Días cumplidos",  0, 30, step=1)
        edad_str = f"{e_meses}m {e_dias}d"
    else:
        e_anios  = st.number_input("Años cumplidos", 1, 120, value=70, step=1)
        edad_str = f"{e_anios} años"

    st.markdown('<hr class="cba-divider">', unsafe_allow_html=True)

    # — Identidad, pueblo originario, instrucción
    c1, c2 = st.columns(2)
    id_genero = c1.selectbox("17 — Identidad de Género", [
        "Mujer", "Varón", "No binarie", "Travesti",
        "Trans femenino", "Trans masculino", "Otro", "Se ignora"
    ])
    pueblo_orig = c2.radio(
        "18 — ¿Pueblo Originario?",
        ["No", "Sí", "Se ignora"],
        horizontal=True
    )

    instruccion = st.selectbox("20 — Máximo nivel de instrucción", [
        "Sin instrucción", "Primario Incomp.", "Primario Comp.",
        "Secundario Incomp.", "Secundario Comp.",
        "Terciario/Universitario Incomp.", "Terciario/Universitario Comp.", "Se ignora"
    ], index=4)

# =============================================================================
# SECCIÓN III — DATOS 14 AÑOS Y MÁS
# =============================================================================
st.markdown("""
<div class="sec-card">
  <div class="sec-header">
    <div class="sec-icon" style="background:#1a7a40;">💼</div>
    <div>
      <div class="sec-num">Sección III</div>
      <div class="sec-title">Datos 14 Años y Más</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("▸ Ver / ocultar datos laborales"):
    c1, c2 = st.columns(2)
    estado_civil = c1.selectbox("Estado Civil", [
        "Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a",
        "Unión convivencial", "Se ignora"
    ])
    actividad = c2.selectbox("Actividad Laboral", [
        "Activo/a", "Desocupado/a", "Jubilado/a",
        "Ama de casa", "Estudiante", "Otro", "Se ignora"
    ])
    c3, c4 = st.columns(2)
    ocupacion = c3.text_input("Ocupación principal", placeholder="Ej: Docente, Comerciante...")
    rama      = c4.text_input("Rama de actividad",   placeholder="Ej: Educación, Salud...")

# =============================================================================
# SECCIÓN IV — CAUSAS DE DEFUNCIÓN
# =============================================================================
st.markdown("""
<div class="sec-card">
  <div class="sec-header">
    <div class="sec-icon" style="background:#7b2c8a;">🩺</div>
    <div>
      <div class="sec-num">Sección IV</div>
      <div class="sec-title">Causas de la Defunción</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("▸ Ver / ocultar causas"):

    busc_cie = st.text_input(
        "Buscador CIE-10",
        placeholder="Escriba el diagnóstico (Ej: INFARTO, SEPSIS...)"
    ).upper()

    if busc_cie:
        sugs = {d: c for d, c in CIE10_DB.items() if busc_cie in d}
        if sugs:
            st.markdown('<div class="subsec-label">Resultados encontrados — seleccione para cargar:</div>',
                        unsafe_allow_html=True)
            cols = st.columns(2)
            for i, (desc, cod) in enumerate(list(sugs.items())[:10]):
                if cols[i % 2].button(
                    f"{cod}  ·  {desc}",
                    use_container_width=True,
                    key=f"cie_{desc}"
                ):
                    st.session_state['causa_seleccionada'] = f"{cod} - {desc}"
                    st.rerun()
        else:
            st.info("No se encontraron diagnósticos para ese término.")

    causa_a = st.text_area(
        "a — Causa Directa  ★",
        value=st.session_state['causa_seleccionada'],
        placeholder="Enfermedad o estado que causó directamente la muerte",
        height=80
    )
    causa_b = st.text_input(
        "b — Causa Antecedente",
        placeholder="Enfermedad o estado que dio origen a la causa anterior"
    )
    causa_c = st.text_input(
        "c — Causa Básica",
        placeholder="Estado patológico de fondo (inicio de la cadena causal)"
    )

    st.markdown('<hr class="cba-divider">', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    fecha_def = c1.date_input("Fecha de fallecimiento  ★", value=datetime.date.today())
    hora_def  = c1.time_input("Hora de fallecimiento", value=datetime.time(0, 0))
    lugar_def = c2.selectbox("Lugar de defunción", [
        "Establecimiento hospitalario público",
        "Establecimiento hospitalario privado",
        "Domicilio particular",
        "Vía pública",
        "Otro",
        "Se ignora"
    ])

# =============================================================================
# SECCIÓN V — SITUACIONES ESPECIALES
# =============================================================================
st.markdown("""
<div class="sec-card">
  <div class="sec-header">
    <div class="sec-icon" style="background:#c0392b;">⚠️</div>
    <div>
      <div class="sec-num">Sección V</div>
      <div class="sec-title">Situaciones Especiales</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("▸ Ver / ocultar situaciones especiales"):
    c1, c2 = st.columns(2)
    tipo_muerte = c1.radio(
        "Tipo de muerte",
        ["Natural", "Violenta", "Se ignora"],
        horizontal=True
    )
    autopsia = c2.radio(
        "¿Hubo autopsia?",
        ["No", "Sí", "Se ignora"],
        horizontal=True
    )
    embarazo = st.selectbox("¿Estaba embarazada? (mujeres 10–54 años)", [
        "No aplica", "No",
        "Sí, al momento del fallecimiento",
        "Sí, dentro de los 42 días anteriores",
        "Entre 43 días y 1 año antes",
        "Se ignora"
    ])

# =============================================================================
# SECCIÓN VIII — PROFESIONAL
# =============================================================================
st.markdown("""
<div class="sec-card">
  <div class="sec-header">
    <div class="sec-icon" style="background:#c9a227;">🖋️</div>
    <div>
      <div class="sec-num">Sección VIII</div>
      <div class="sec-title">Datos del Profesional</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("▸ Ver / ocultar datos del profesional", expanded=True):

    # — Matrícula
    c_mat, c_btn2 = st.columns([2, 1])
    mat_m    = c_mat.text_input("Matrícula Profesional  ★", placeholder="Número de matrícula")
    verificar = c_btn2.button("Verificar matrícula", use_container_width=True)

    nom_m_def = ""
    if mat_m == "12345" or (verificar and mat_m == "12345"):
        st.markdown(
            '<div class="renaper-ok"><span class="renaper-dot"></span> DR. CARLOS MEDICINA — Matrícula activa</div>',
            unsafe_allow_html=True
        )
        nom_m_def = "DR. CARLOS MEDICINA"
    elif verificar and mat_m:
        st.warning("Matrícula no encontrada en el registro provincial.")

    nom_m = st.text_input(
        "Nombre del Médico  ★",
        value=nom_m_def,
        placeholder="Se completa automáticamente al verificar"
    )

    email_dest = st.text_input(
        "Email para recibir el PDF  ★",
        placeholder="medico@hospital.gob.ar"
    )

    # — Firma CiDi
    st.markdown("""
    <div class="cidi-box">
        <div class="cidi-icon">🔐</div>
        <div class="cidi-text">
            <p>Firma Digital — CiDi Córdoba</p>
            <small>Requiere autenticación con su cuenta CiDi provincial. 
            Al firmar, el profesional certifica la veracidad de los datos consignados.</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    firma_digital = st.checkbox("✔ Autorizo y firmo digitalmente este registro oficial")

# =============================================================================
# BOTÓN DE ENVÍO
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)

confirmar = st.button("🔴  CONFIRMAR Y ENVIAR REGISTRO OFICIAL", use_container_width=True)

st.markdown(
    '<div class="footer-legal">Este registro tiene validez oficial según Ley Provincial N.° 10.208 — '
    'Sistema de Estadísticas Vitales de la Provincia de Córdoba</div>',
    unsafe_allow_html=True
)

if confirmar:
    errores = []
    if not nombre_f:   errores.append("Apellido/s y Nombre/s del fallecido")
    if not causa_a:    errores.append("Causa Directa de defunción")
    if not firma_digital: errores.append("Firma Digital CiDi")
    if not email_dest: errores.append("Email del profesional")
    if not nom_m:      errores.append("Nombre del Médico")

    if errores:
        st.error("⚠️ Faltan completar los siguientes campos obligatorios:\n\n" +
                 "\n".join(f"• {e}" for e in errores))
    else:
        with st.spinner("Guardando el registro en el sistema..."):
            datos = {
                "dpto_partido":      dpto_reg,
                "delegacion":        deleg_reg,
                "acta_nro":          acta_reg,
                "anio":              anio_reg,
                "dni_fallecido":     dni_f,
                "nombre_fallecido":  nombre_f,
                "sexo":              sexo_f,
                "fecha_nacimiento":  str(f_nac),
                "domicilio":         domicilio_f,
                "edad":              edad_str,
                "identidad_genero":  id_genero,
                "pueblo_originario": pueblo_orig,
                "instruccion":       instruccion,
                "causa_directa":     causa_a,
                "causa_antecedente": causa_b,
                "lugar_defuncion":   lugar_def,
                "medico_nombre":     nom_m,
                "matricula":         mat_m,
                "email_envio":       email_dest,
                "firma_digital":     firma_digital,
            }
            try:
                supabase.table("certificados_defuncion").insert(datos).execute()
                st.session_state['proceso_exitoso'] = True
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar en Supabase: {e}")
