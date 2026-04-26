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
# CSS GLOBAL — AJUSTE DE ESPACIADO SUPERIOR
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

#MainMenu, footer { visibility: hidden; }

/* SE BAJÓ EL CONTENIDO MÁS (8rem) */
.block-container { padding-top: 8rem !important; max-width: 860px !important; }

/* ── HEADER ── */
.cba-header {
    background: linear-gradient(135deg, #003366 0%, #1a4f8a 100%);
    border-bottom: 4px solid #c9a227;
    padding: 20px 28px;
    margin: -8rem -1rem 0 -1rem; /* Ajustado para bajar con el padding */
    display: flex; align-items: center; gap: 20px;
    box-shadow: 0 3px 14px rgba(0,0,0,0.22);
}
.cba-logo-box {
    background: white; border-radius: 10px; padding: 8px 10px;
    flex-shrink: 0; display: flex; align-items: center; justify-content: center;
    min-width: 78px; min-height: 78px;
}
.cba-logo-box img { width: 62px; height: 62px; object-fit: contain; }
.cba-header-text h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 25px !important; font-weight: 600 !important;
    color: white !important; margin: 0 !important;
}
.cba-header-text p {
    font-size: 11px !important; color: rgba(255,255,255,0.75) !important;
    margin: 0 !important; text-transform: uppercase !important;
}
.cba-progress {
    height: 4px;
    background: linear-gradient(90deg, #c9a227 35%, #d0d9e4 35%);
    margin: 0 -1rem 1.6rem -1rem;
}

/* ── ESTILOS DE FORMULARIO ── */
[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid var(--gris-brd) !important;
    border-radius: 10px !important;
    margin-bottom: 14px !important;
}
[data-testid="stExpander"] > details > summary {
    background: var(--cel-fondo) !important;
    font-weight: 700 !important;
    color: #003366 !important;
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
        <p>Gobierno de la Provincia de Córdoba</p>
    </div>
</div>
<div class="cba-progress"></div>
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
    dni_f = st.text_input("3- Nro de Documento (RENAPER)")
    nombre_f = st.text_input("1- Apellido/s y Nombre/s")
    c_f1, c_f2 = st.columns(2)
    sexo_f = c_f1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac = c_f2.date_input("6- Fecha Nacimiento")

with st.expander("🩺 IV. CAUSAS DE LA DEFUNCIÓN"):
    causa_a = st.text_area("26- a) Causa Directa")
    intervalo = st.text_input("Intervalo")

with st.expander("🖋️ VIII. PROFESIONAL", expanded=True):
    mat_m = st.text_input("Matrícula Profesional")
    nom_m = st.text_input("Nombre Médico")
    email_dest = st.text_input("Email receptor PDF")
    firma_digital = st.checkbox("Firma Digital (CiDi Córdoba)")

confirmar = st.button("🔴 CONFIRMAR Y ENVIAR REGISTRO OFICIAL", use_container_width=True)

if confirmar:
    if nombre_f and causa_a and firma_digital and email_dest:
        try:
            supabase.table("certificados_defuncion").insert({
                "nombre_fallecido": nombre_f, "dni_fallecido": dni_f,
                "causa_directa": causa_a, "medico_nombre": nom_m, "email_envio": email_dest
            }).execute()
            
            pdf = CertificadoPDF()
            pdf.add_page()
            pdf.seccion("DATOS")
            pdf.item("1", "Nombre", nombre_f)
            pdf.item("26-a", "Causa", causa_a)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')

            if enviar_correo(email_dest, pdf_bytes, nombre_f):
                st.session_state['proceso_exitoso'] = True
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
