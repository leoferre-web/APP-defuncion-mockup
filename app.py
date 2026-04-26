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
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10"
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
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "INFORME ESTADISTICO DE DEFUNCION - PROVINCIA DE CORDOBA", 1, 1, 'C')
        self.ln(2)
    def seccion(self, titulo):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 7, f" {titulo}", 1, 1, 'L')
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
# CSS GLOBAL — CORRECCIÓN DE COLORES Y ENCABEZADO
# =============================================================================
st.markdown("""
<style>
/* 1. Fondo general siempre blanco y eliminar barra negra superior */
.stApp { background-color: white !important; }
header { visibility: hidden !important; }

/* 2. Forzar que todos los campos (inputs, textareas, selects) sean blancos con texto negro */
input, textarea, div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > div {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ccc !important;
}

/* 3. Forzar que todos los textos (labels, opciones de radio, parrafos) sean NEGROS */
label p, .stWidget label p, div[data-testid="stMarkdownContainer"] p, span p {
    color: black !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* 4. Estilo del Encabezado (Restaurado sin barra negra) */
.cba-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 0;
    border-bottom: 2px solid #eee;
    background-color: white !important;
}
.cba-header h1 { margin: 0; font-size: 24px; color: black !important; }
.cba-header p { margin: 0; color: #444 !important; }

/* 5. Cuadro de firma CiDi */
.cidi-box {
    border: 1px dashed black !important;
    padding: 15px;
    margin: 10px 0;
    color: black !important;
    background-color: #f9f9f9 !important;
}

/* 6. Botones */
.stButton > button { background-color: #f0f0f0; color: black; border: 1px solid #ccc; }
.btn-confirmar button { background-color: #cc0000 !important; color: white !important; font-weight: bold !important; }

</style>
""", unsafe_allow_html=True)

# =============================================================================
# HEADER
# =============================================================================
st.markdown(f"""
<div class="cba-header">
    <img src="{URL_LOGO}" width="60">
    <div>
        <h1>Ministerio de Salud</h1>
        <p>Gobierno de la Provincia de Córdoba</p>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state['proceso_exitoso']:
    st.success("✅ Certificado generado con éxito")
    if st.button("CARGAR NUEVO"): reiniciar_formulario()
    st.stop()

# =============================================================================
# FORMULARIO
# =============================================================================
with st.expander("📂 I. DATOS DEL REGISTRO"):
    c1, c2, c3, c4 = st.columns(4)
    dpto_reg = c1.text_input("Dpto")
    deleg_reg = c2.text_input("Delegación")
    acta_reg = c3.text_input("Acta")
    anio_reg = c4.text_input("Año")

with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    dni_f = st.text_input("3- Nro de Documento (DNI)")
    nombre_defecto, domicilio_defecto = "", ""
    
    if dni_f:
        if dni_f in DB_RENAPER:
            st.markdown(f"**VALIDADO: {DB_RENAPER[dni_f]['nombre']}**")
            nombre_defecto = DB_RENAPER[dni_f]['nombre']
            domicilio_defecto = DB_RENAPER[dni_f]['domicilio']
        else:
            st.warning("⚠️ DNI no encontrado en RENAPER.")
    
    nombre_f = st.text_input("1- Apellidos y Nombres", value=nombre_defecto)
    c_f1, c_f2 = st.columns(2)
    sexo_f = c_f1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac = c_f2.date_input("6- Fecha Nacimiento")
    domicilio_f = st.text_input("10- Domicilio Real", value=domicilio_defecto)
    
    es_menor = st.checkbox("¿Es menor de 1 año?")
    if es_menor:
        em1, em2 = st.columns(2)
        edad_str = f"{em1.number_input('Meses',0)}m {em2.number_input('Días',0)}d"
    else:
        e_anios = st.number_input("Años cumplidos", 1, 120, 70)
        edad_str = f"{e_anios} años"

with st.expander("🩺 IV. CAUSAS DE LA DEFUNCIÓN"):
    forma_m = st.radio("23- Forma de morir", ["No traumática", "Traumática"], horizontal=True)
    causa_a = st.text_area("26- a) Causa Directa")
    intervalo = st.text_input("Intervalo enfermedad-muerte")
    autopsia = st.radio("33- ¿Se solicitó autopsia?", ["No", "Si", "Se desconoce"])

with st.expander("🖋️ VIII. PROFESIONAL", expanded=True):
    col_m1, col_m2 = st.columns(2)
    mat_m = col_m1.text_input("Matrícula")
    nom_m_defecto = ""
    
    if mat_m:
        if mat_m in DB_REFES:
            st.markdown(f"**MÉDICO VALIDADO: {DB_REFES[mat_m]}**")
            nom_m_defecto = "DR. CARLOS MEDICINA"
        else:
            st.error("❌ Matrícula no encontrada en REFES.")
            
    nom_m = col_m2.text_input("Nombre del Médico", value=nom_m_defecto)
    email_dest = st.text_input("Email para envío del PDF")
    
    st.markdown('<div class="cidi-box">🔐 Firma Digital — CiDi Córdoba</div>', unsafe_allow_html=True)
    firma_digital = st.checkbox("Certifico la veracidad de los datos")

st.markdown('<div class="btn-confirmar">', unsafe_allow_html=True)
confirmar = st.button("CONFIRMAR Y ENVIAR REGISTRO OFICIAL", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PROCESO ---
if confirmar:
    if nombre_f and causa_a and firma_digital and email_dest:
        try:
            supabase.table("certificados_defuncion").insert({
                "nombre_fallecido": nombre_f, "dni_fallecido": dni_f,
                "causa_directa": causa_a, "medico_nombre": nom_m, "email_envio": email_dest
            }).execute()
            
            pdf = CertificadoPDF()
            pdf.add_page()
            pdf.seccion("DATOS"); pdf.item("1", "Fallecido", nombre_f); pdf.item("26", "Causa", causa_a)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            if enviar_correo(email_dest, pdf_bytes, nombre_f):
                st.session_state['proceso_exitoso'] = True
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("⚠️ Faltan datos obligatorios.")
