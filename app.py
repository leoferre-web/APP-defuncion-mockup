import streamlit as st
import datetime
import time
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Defunción Digital - Córdoba", layout="wide", page_icon="⚖️")

# --- SIMULACIÓN DE BASES DE DATOS (Para que la validación "funcione" en la demo) ---
DB_RENAPER = {"123": {"nombre": "JUAN PEREZ", "domicilio": "AV. COLON 1234, CORDOBA"}}
DB_REFES = {"12345": "DR. CARLOS MEDICINA (MATRÍCULA ACTIVA)"}

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

# --- CLASE PDF PROFESIONAL ---
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

# --- FUNCIÓN DE ENVÍO ---
def enviar_correo(dest, pdf_content, nombre):
    try:
        remitente = st.secrets["email"]["remitente"]
        password = st.secrets["email"]["password"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = dest
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
        st.error(f"Error crítico de envío/Secrets: {e}")
        return False

# --- INTERFAZ ---
st.title("⚖️ Sistema de Defunción Digital Córdoba")

# BLOQUE I: REGISTRO
with st.expander("📂 I. DATOS DEL REGISTRO"):
    c1, c2, c3, c4 = st.columns(4)
    dpto_reg = c1.text_input("Dpto/Partido")
    deleg_reg = c2.text_input("Delegación")
    acta_reg = c3.text_input("Acta Nro")
    anio_reg = c4.text_input("Año")

# BLOQUE II: FALLECIDO
with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    dni_f = st.text_input("3- Nro de Documento (Pruebe con '123' para validar)")
    
    # Lógica de Validación RENAPER
    nombre_defecto = ""
    domicilio_defecto = ""
    if dni_f in DB_RENAPER:
        with st.spinner("Consultando RENAPER..."):
            time.sleep(0.8)
            st.success(f"✅ Identidad Validada: {DB_RENAPER[dni_f]['nombre']}")
            nombre_defecto = DB_RENAPER[dni_f]['nombre']
            domicilio_defecto = DB_RENAPER[dni_f]['domicilio']
    elif dni_f:
        st.warning("⚠️ DNI no encontrado en base local. Ingrese datos manualmente.")

    nombre_f = st.text_input("1- Apellido/s y Nombre/s", value=nombre_defecto)
    c_f1, c_f2 = st.columns(2)
    sexo_f = c_f1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac = c_f2.date_input("6- Fecha Nacimiento", value=datetime.date(1960,1,1))
    domicilio_f = st.text_input("10- Domicilio Real", value=domicilio_defecto)

    st.markdown("**16- Edad al fallecimiento**")
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
        e_anios = st.number_input("Años cumplidos", 1, 120)
        edad_str = f"{e_anios} años"

    id_gen = st.selectbox("17- Identidad de Género", ["Mujer trans/travesti", "Varón trans", "Mujer", "Varón", "Ninguna", "Ignorado"])
    pueblo = st.radio("18- ¿Pueblo originario?", ["No", "Si", "Se ignora"], horizontal=True)
    pueblo_nom = st.text_input("19- Cuál?") if pueblo == "Si" else "N/A"
    instruccion = st.selectbox("20- Máximo nivel instrucción", ["Nunca asistió", "Primario Comp", "Primario Incomp", "Secundario Comp", "Secundario Incomp", "Terciario/Univ Comp", "Terciario/Univ Incomp", "Posgrado", "Se ignora"])

# BLOQUE III: SOCIO-ECONÓMICO
if not es_menor and e_anios >= 14:
    with st.expander("💼 III. DATOS 14 AÑOS Y MÁS"):
        sit_lab = st.radio("21- Situación laboral", ["Trabajaba", "Buscaba trabajo", "No trabajaba/no buscaba"])
        ocupacion = st.text_input("22- Ocupación habitual")

# BLOQUE IV: CAUSAS
with st.expander("🩺 IV. CAUSAS DE LA DEFUNCIÓN"):
    forma_m = st.radio("23- Forma de morir", ["No traumática", "Traumática"], horizontal=True)
    enfer_inf = st.radio("24- ¿Enfermedad infectocontagiosa?", ["No", "Si"]) if forma_m == "No traumática" else "N/A"
    
    busc_cie = st.text_input("🔍 BUSCADOR CIE-10").upper()
    if busc_cie:
        for d, c in CIE10_DB.items():
            if busc_cie in d:
                if st.button(f"Asignar {c}"): st.session_state['causa_seleccionada'] = f"{c} - {d}"
    
    causa_a = st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
    causa_b = st.text_input("b) Debido a")
    otros_est = st.text_area("II) Otros estados patológicos")
    intervalo = st.text_input("Intervalo enfermedad-muerte")

# BLOQUE V: ESPECIALES
with st.expander("⚠️ V. SITUACIONES ESPECIALES"):
    if sexo_f == "Femenino":
        emb = st.radio("27- ¿Embarazada/12 meses previos?", ["No", "Si", "Se desconoce"])
    cirugia = st.radio("30- ¿Cirugía en 4 semanas previas?", ["No", "Si", "Se desconoce"])
    autopsia = st.radio("33- ¿Se solicitó autopsia?", ["No", "Si", "Se desconoce"])
    fuente = st.selectbox("35- Fuente", ["Historia clínica", "Laboratorio", "Interrogatorio"])
    atencion = st.radio("36- ¿Tuvo atención médica?", ["Si", "No", "Se desconoce"])

# BLOQUE VI: CAUSAS EXTERNAS
with st.expander("🏎️ VI. CAUSAS EXTERNAS"):
    manera = st.selectbox("37- Manera de morir", ["Enfermedad", "Accidente", "Suicidio", "Agresión", "Investigación", "No pudo determinarse"])
    desc_lesion = st.text_area("40- Describa cómo ocurrió")
    lugar_ext = st.selectbox("41- Lugar donde ocurrió", ["Vivienda", "Institución", "Vía pública", "Trabajo", "Otro"])

# BLOQUE VII: MENOR 1 AÑO
if es_menor:
    with st.expander("👶 VII. MENOR DE 1 AÑO"):
        peso = st.number_input("42- Peso al nacer (gramos)", 0)
        semanas = st.number_input("43- Semanas de embarazo", 0)

# BLOQUE VIII: MÉDICO (Validación REFES mejorada)
with st.expander("🖋️ VIII. PROFESIONAL", expanded=True):
    col_m1, col_m2 = st.columns(2)
    mat_m = col_m1.text_input("Matrícula Profesional (Pruebe '12345')")
    
    nom_m_defecto = ""
    if mat_m in DB_REFES:
        with st.spinner("Consultando REFES..."):
            time.sleep(0.8)
            st.success(f"✅ {DB_REFES[mat_m]}")
            nom_m_defecto = "DR. CARLOS MEDICINA"
    
    nom_m = col_m2.text_input("Nombre Médico", value=nom_m_defecto)
    email_dest = st.text_input("Email para recibir el PDF")
    firma_digital = st.checkbox("Firma Digital (CiDi Córdoba)")

# --- BOTÓN DE GENERACIÓN ---
if st.button("CONFIRMAR Y ENVIAR CERTIFICADO COMPLETO"):
    if nombre_f and causa_a and firma_digital and email_dest:
        with st.spinner("Generando PDF Oficial..."):
            pdf = CertificadoPDF()
            pdf.add_page()
            
            # Mapeo de ítems al PDF (Ejemplo de algunos campos)
            pdf.seccion("DATOS DEL REGISTRO")
            pdf.item("I", "Registro", f"{dpto_reg} - {acta_reg}")
            pdf.seccion("DATOS DEL FALLECIDO")
            pdf.item("1", "Nombre", nombre_f)
            pdf.item("3", "DNI", dni_f)
            pdf.item("16", "Edad", edad_str)
            pdf.item("17", "Género", id_gen)
            pdf.seccion("CAUSAS")
            pdf.item("26-a", "Causa", causa_a)
            pdf.seccion("FIRMA")
            pdf.item("M", "Médico", f"{nom_m} MP: {mat_m}")
            pdf.item("HASH", "Validación Digital", f"CBA-{int(time.time())}")

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            if enviar_correo(email_dest, pdf_bytes, nombre_f):
                st.info("✅ Registro exitoso. El PDF llegará a su bandeja en breve.")
    else:
        st.error("Error: Faltan datos críticos o la firma digital.")
