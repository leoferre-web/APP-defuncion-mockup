import streamlit as st
import datetime
import time
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(page_title="Sistema Digital de Defunción - Córdoba", layout="wide")

# --- FUNCION PARA GENERAR PDF ---
def generar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "CERTIFICADO DE DEFUNCION DIGITAL - CORDOBA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for clave, valor in datos.items():
        pdf.cell(200, 10, f"{clave}: {valor}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- FUNCION PARA ENVIAR CORREO ---
def enviar_correo(destinatario, pdf_content, nombre_fallecido):
    remitente = "tu_correo@gmail.com"  # CAMBIAR POR TU CORREO
    password = "tu_password_de_aplicacion" # CAMBIAR POR TU CLAVE DE APLICACION

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"Certificado de Defunción Digital - {nombre_fallecido}"

    body = "Se adjunta el certificado de defunción validado y firmado digitalmente."
    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename=Certificado_{nombre_fallecido}.pdf")
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error de envío: {e}")
        return False

# --- INTERFAZ ---
st.title("⚖️ Registro Digital con Envío de PDF")

with st.form("form_final"):
    nombre = st.text_input("Nombre del Fallecido")
    dni = st.text_input("DNI")
    causa = st.text_input("Causa de Muerte (CIE-10)")
    email_medico = st.text_input("Tu correo electrónico (para recibir el PDF)")
    confirmar = st.checkbox("Confirmo que los datos son correctos y firmo digitalmente")
    
    boton_enviar = st.form_submit_button("CONFIRMAR Y ENVIAR PDF")

if boton_enviar:
    if nombre and email_medico and confirmar:
        datos_pdf = {
            "Fecha": str(datetime.date.today()),
            "Fallecido": nombre,
            "DNI": dni,
            "Causa": causa,
            "Estado": "VALIDADO - FIRMADO DIGITALMENTE"
        }
        
        with st.spinner("Generando documento y enviando correo..."):
            contenido_pdf = generar_pdf(datos_pdf)
            exito = enviar_correo(email_medico, contenido_pdf, nombre)
            
            if exito:
                st.success(f"✅ ¡Certificado enviado con éxito a {email_medico}!")
    else:
        st.error("Por favor, completa los datos y marca la firma.")
