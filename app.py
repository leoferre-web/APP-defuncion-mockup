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

# --- BASE DE DATOS CIE-10 ---
CIE10_DB = {
    "INFARTO AGUDO DE MIOCARDIO": "I21.9", "INSUFICIENCIA CARDIACA": "I50.9", 
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10",
    "SHOCK CARDIOGENICO": "R57.0", "NEUMONIA": "J18.9", "EPOC": "J44.9",
    "COVID-19": "U07.1", "CANCER DE PULMON": "C34.9", "SEPSIS": "A41.9",
    "DIABETES TIPO 2": "E11.9", "INSUFICIENCIA RENAL": "N18.9", "ALZHEIMER": "G30.9",
    "TRAUMATISMO CRANEOENCEFALICO": "S06.9", "HERIDA POR ARMA DE FUEGO": "W34"
}

if 'causa_seleccionada' not in st.session_state:
    st.session_state['causa_seleccionada'] = ""

# --- CLASE PDF CON MEJOR ESTÉTICA ---
class CertificadoPDF(FPDF):
    def header(self):
        self.set_fill_color(230, 230, 230)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "INFORME ESTADÍSTICO DE DEFUNCIÓN - PROVINCIA DE CÓRDOBA", 1, 1, 'C', True)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, "Documento Digital con Validez Legal - Ley 25.506", 0, 1, 'C')
        self.ln(5)

    def seccion_titulo(self, titulo):
        self.set_fill_color(240, 240, 240)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 7, titulo, 1, 1, 'L', True)
        self.set_font('Arial', '', 9)

    def dato(self, etiqueta, valor):
        self.set_font('Arial', 'B', 9)
        self.write(7, f"{etiqueta}: ")
        self.set_font('Arial', '', 9)
        self.write(7, f"{valor}\n")

# --- FUNCIONES DE SERVIDOR ---
def enviar_correo(dest, pdf_content, nombre):
    try:
        remitente = st.secrets["email"]["remitente"]
        password = st.secrets["email"]["password"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = dest
        msg['Subject'] = f"CERTIFICADO DIGITAL DEFUNCIÓN: {nombre}"
        msg.attach(MIMEText(f"Se adjunta certificado oficial de {nombre}.", 'plain'))
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
        st.error(f"Error de envío: {e}")
        return False

# --- INTERFAZ STREAMLIT ---
st.title("⚖️ Certificado de Defunción Digital")

# BLOQUES DE DATOS (Interfaz)
with st.expander("📂 I. DATOS DEL REGISTRO"):
    c1, c2, c3 = st.columns(3)
    dpto = c1.text_input("Dpto/Partido")
    deleg = c2.text_input("Delegación")
    acta = c3.text_input("Acta Nro")

with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    dni = st.text_input("3- Nro de Documento")
    nombre = st.text_input("1- Apellido/s y Nombre/s", value="JUAN PEREZ" if dni else "")
    c_f1, c_f2 = st.columns(2)
    sexo = c_f1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    id_gen = c_f2.selectbox("17- Identidad de Género", ["Mujer trans/travesti", "Varón trans", "Mujer", "Varón", "Ninguna", "Ignorado"])
    
    es_menor = st.checkbox("¿Es menor de 1 año?")
    if es_menor:
        m, d, h = st.columns(3)
        edad_val = f"{m.number_input('Meses',0)}m {d.number_input('Días',0)}d {h.number_input('Horas',0)}h"
    else:
        edad_val = f"{st.number_input('Años cumplidos', 1, 120)} años"

    pueblo = st.radio("18- ¿Pueblo originario?", ["No", "Si"], horizontal=True)
    instruc = st.selectbox("20- Nivel de Instrucción", ["Primario Completo", "Secundario Completo", "Universitario", "Sin instrucción"])

with st.expander("🩺 III. CERTIFICACIÓN MÉDICA"):
    busc = st.text_input("🔍 BUSCADOR CIE-10").upper()
    if busc:
        for d, c in CIE10_DB.items():
            if busc in d:
                if st.button(f"Seleccionar {c}"): st.session_state['causa_seleccionada'] = f"{c} - {d}"
    
    causa_a = st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
    otros_pat = st.text_input("II) Otros estados patológicos")

with st.expander("🖋️ IV. FIRMA Y ENVÍO"):
    mat = st.text_input("Matrícula Profesional")
    email_envio = st.text_input("Email para recibir el PDF")
    firma = st.checkbox("Confirmo veracidad y firmo digitalmente")

# --- GENERACIÓN FINAL ---
if st.button("GENERAR CERTIFICADO IMPRESO"):
    if nombre and causa_a and firma and email_envio:
        with st.spinner("Generando PDF con estética oficial..."):
            pdf = CertificadoPDF()
            pdf.add_page()
            
            pdf.seccion_titulo("I. DATOS DEL REGISTRO")
            pdf.dato("Departamento", dpto)
            pdf.dato("Delegación", deleg)
            pdf.dato("Acta Nro", acta)
            
            pdf.seccion_titulo("II. DATOS DEL FALLECIDO")
            pdf.dato("Nombre Completo", nombre)
            pdf.dato("DNI", dni)
            pdf.dato("Edad", edad_val)
            pdf.dato("Identidad de Género", id_gen)
            pdf.dato("Pueblo Originario", pueblo)
            pdf.dato("Instrucción", instruc)
            
            pdf.seccion_titulo("III. CAUSAS DE DEFUNCIÓN (CIE-10)")
            pdf.dato("Causa Directa (a)", causa_a)
            pdf.dato("Otros estados", otros_pat)
            
            pdf.seccion_titulo("IV. PROFESIONAL Y VALIDACIÓN")
            pdf.dato("Médico", "Dr. Certificante")
            pdf.dato("Matrícula", mat)
            pdf.dato("Firma Digital ID", "F-DIG-99283-CBA")
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            if enviar_correo(email_envio, pdf_bytes, nombre):
                st.success(f"Certificado enviado con éxito a {email_envio}")
    else:
        st.warning("Faltan datos obligatorios.")
