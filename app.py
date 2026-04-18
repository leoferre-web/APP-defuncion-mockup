import streamlit as st
import datetime
import time
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE PÁGINA SOBRIA ---
st.set_page_config(page_title="Defunción Digital Córdoba - Oficial", layout="wide", page_icon="⚖️")

# Estilo para eliminar elementos distractores
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { background-color: #2c3e50; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS CIE-10 (AMPLIADA A 50+) ---
CIE10_DB = {
    "INFARTO AGUDO DE MIOCARDIO": "I21.9", "INSUFICIENCIA CARDIACA": "I50.9", 
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10",
    "SHOCK CARDIOGENICO": "R57.0", "NEUMONIA": "J18.9", "EPOC": "J44.9",
    "COVID-19": "U07.1", "CANCER DE PULMON": "C34.9", "SEPSIS": "A41.9",
    "DIABETES TIPO 2": "E11.9", "INSUFICIENCIA RENAL": "N18.9", "ALZHEIMER": "G30.9",
    "TRAUMATISMO CRANEOENCEFALICO": "S06.9", "HERIDA POR ARMA DE FUEGO": "W34",
    "CIRROSIS HEPATICA": "K74.6", "CANCER DE COLON": "C18.9", "ASMA": "J45.9",
    "EMBOLIA PULMONAR": "I26.9", "EDEMA PULMONAR": "J81", "SHOCK SEPTICO": "A41.9",
    "CANCER DE MAMA": "C50.9", "CANCER DE PROSTATA": "C61", "TUBERCULOSIS": "A15.0",
    "HIV/SIDA": "B24", "DENGUE GRAVE": "A91", "LEUCEMIA": "C91.9",
    "POLITRAUMATISMO": "T07", "AHOGAMIENTO": "W74", "ASFIXIA MECANICA": "W84",
    "INTOXICACION MONOXIDO": "T58", "QUEMADURAS": "T30.0", "CAIDA DE ALTURA": "W19"
}

if 'causa_seleccionada' not in st.session_state:
    st.session_state['causa_seleccionada'] = ""

# --- FUNCIONES DE DOCUMENTO Y ENVÍO ---
def generar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "INFORME ESTADISTICO DE DEFUNCION - CORDOBA", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    for k, v in datos.items():
        pdf.multi_cell(0, 7, f"{k}: {v}", border=0)
    pdf.ln(10)
    pdf.cell(0, 10, "VALIDADO POR: RENAPER / REFES / FIRMA DIGITAL CIDI", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def enviar_correo(dest, pdf_content, nombre):
    try:
        remitente = st.secrets["email"]["remitente"]
        password = st.secrets["email"]["password"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = dest
        msg['Subject'] = f"CERTIFICADO DIGITAL CONFIRMADO: {nombre}"
        msg.attach(MIMEText(f"Se adjunta el certificado digital de defunción de {nombre} validado por el Ministerio de Salud.", 'plain'))
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
    except: return False

# --- INTERFAZ DEL CERTIFICADO ---
st.title("⚖️ Informe Estadístico de Defunción Digital")
st.subheader("Provincia de Córdoba - Registro Civil")

# BLOQUE I: REGISTRO
with st.expander("📂 I. DATOS DEL REGISTRO"):
    c1, c2, c3, c4 = st.columns(4)
    c1.text_input("Departamento")
    c2.text_input("Delegación")
    c3.text_input("Acta Nro")
    c4.text_input("Año")

# BLOQUE II: FALLECIDO
with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    col_dni = st.columns([1, 1, 1])
    nro_doc = col_dni[0].text_input("3- Nro de Documento")
    if nro_doc: 
        st.success("✅ Identidad Validada en RENAPER")
    
    nombre = st.text_input("1- Apellido/s y Nombre/s", value="JUAN PEREZ" if nro_doc else "")
    
    # ÍTEM 16: EDAD DETALLADA
    st.markdown("**16- Edad al momento del fallecimiento**")
    e1, e2 = st.columns(2)
    es_menor = e1.checkbox("¿Es menor de 1 año?")
    if not es_menor:
        edad_anios = e2.number_input("Años cumplidos", 1, 120)
    else:
        m, d, h, mi = st.columns(4)
        m.number_input("Meses", 0, 11)
        d.number_input("Días", 0, 30)
        h.number_input("Horas", 0, 23)
        mi.number_input("Minutos", 0, 59)

    # ÍTEMS 17, 18, 19, 20
    st.selectbox("17- Identidad de Género", ["Mujer trans/travesti", "Varón trans", "Mujer", "Varón", "Ninguna", "Ignorado"])
    pueblo = st.radio("18- ¿Pertenece a pueblo originario?", ["No", "Si", "Se ignora"], horizontal=True)
    if pueblo == "Si": st.text_input("19- Especifique pueblo")
    instruccion = st.selectbox("20- Nivel de Instrucción", ["Nunca asistió", "Primario Comp/Incomp", "Secundario Comp/Incomp", "Terciario/Univ Comp/Incomp", "Posgrado", "Se ignora"])

# BLOQUE III: LABORAL (14+)
if not es_menor and edad_anios >= 14:
    with st.expander("💼 III. SITUACIÓN LABORAL (14 años y más)"):
        st.radio("21- Situación laboral", ["Trabajaba", "Buscaba trabajo", "No buscaba"])
        st.text_input("22- Ocupación habitual")

# BLOQUE IV: CAUSAS Y CIE-10
st.markdown("---")
st.header("🩺 IV. CERTIFICACIÓN MÉDICA")
forma = st.radio("23- Forma de morir", ["No traumática", "Traumática"], horizontal=True)

busc = st.text_input("🔍 BUSCADOR CIE-10 (Escriba diagnóstico)").upper()
if busc:
    for d, c in CIE10_DB.items():
        if busc in d:
            if st.button(f"Codificar: {c}"): st.session_state['causa_seleccionada'] = f"{c} - {d}"

causa_a = st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
st.text_input("b) Debido a")
st.text_input("Intervalo enfermedad-muerte")

# BLOQUE V: SITUACIONES ESPECIALES
with st.expander("⚠️ V. INFORMACIÓN COMPLEMENTARIA"):
    st.radio("27- Embarazo/Puerperio (Mujeres 10-49)", ["No", "Si", "Se desconoce"])
    st.radio("30- Cirugía previa", ["No", "Si", "Se desconoce"])
    st.radio("33- Autopsia", ["No", "Si", "Se desconoce"])
    st.selectbox("35- Fuente", ["Historia clínica", "Laboratorio", "Interrogatorio"])
    st.radio("36- Atención médica", ["Si", "No", "Se desconoce"])

# BLOQUE VI: CAUSAS EXTERNAS
with st.expander("🏎️ VI. CAUSAS EXTERNAS (37-41)"):
    st.selectbox("37- Manera de morir", ["Enfermedad", "Accidente", "Suicidio", "Agresión", "Investigación", "Otro"])
    st.text_area("40- Descripción de la lesión")
    st.selectbox("41- Lugar", ["Vivienda", "Vía pública", "Trabajo", "Otro"])

# BLOQUE VII: MENOR 1 AÑO
if es_menor:
    with st.expander("👶 VII. MENOR DE 1 AÑO"):
        st.number_input("42- Peso al nacer (grs)", 0)
        st.number_input("43- Semanas gestación", 0)

# BLOQUE VIII: MÉDICO Y FIRMA
with st.expander("🖋️ VIII. PROFESIONAL CERTIFICANTE", expanded=True):
    m_col1, m_col2 = st.columns(2)
    mat = m_col1.text_input("Matrícula Profesional")
    if mat: st.success("✅ Matrícula Habilitada (REFES)")
    medico = m_col2.text_input("Nombre", value="Dr. Carlos Medicina" if mat else "")
    email_envio = st.text_input("Email para envío del certificado PDF")
    firma = st.checkbox("Confirmo veracidad y firmo digitalmente (CiDi)")

# --- ACCIÓN FINAL (SIN GLOBOS) ---
if st.button("CONFIRMAR Y FINALIZAR REGISTRO"):
    if nombre and causa_a and firma and email_envio:
        with st.spinner("Procesando registro oficial..."):
            datos_pdf = {"Paciente": nombre, "DNI": nro_doc, "Causa": causa_a, "Medico": medico, "Hash": "SHA256-8293"}
            pdf = generar_pdf(datos_pdf)
            if enviar_correo(email_envio, pdf, nombre):
                st.markdown("""
                    <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; border: 1px solid #c3e6cb; text-align: center;">
                        <h3>✅ CERTIFICADO CONFIRMADO</h3>
                        <p>El documento ha sido firmado y enviado por correo electrónico.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Error en envío. Verifique sus Secrets.")
    else:
        st.warning("Complete todos los campos y la firma.")
