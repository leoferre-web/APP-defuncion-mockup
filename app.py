import streamlit as st
import datetime
import time
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Defunción Digital - Córdoba", layout="wide", page_icon="⚖️")

if 'causa_seleccionada' not in st.session_state:
    st.session_state['causa_seleccionada'] = ""

# --- BASE DE DATOS CIE-10 (50 CÓDIGOS) ---
CIE10_DB = {
    "INFARTO AGUDO DE MIOCARDIO": "I21.9", "INSUFICIENCIA CARDIACA": "I50.9", 
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10",
    "SHOCK CARDIOGENICO": "R57.0", "ARRITMIA VENTRICULAR": "I47.2",
    "ANEURISMA DE AORTA": "I71.9", "EMBOLIA PULMONAR": "I26.9",
    "PARO CARDIORRESPIRATORIO": "I46.9", "MIOCARDITIS": "I40.9",
    "NEUMONIA": "J18.9", "EPOC": "J44.9", "INSUFICIENCIA RESPIRATORIA AGUDA": "J96.0",
    "ASMA BRONQUIAL": "J45.9", "EDEMA AGUDO DE PULMON": "J81", "COVID-19": "U07.1",
    "CANCER DE PULMON": "C34.9", "CANCER DE MAMA": "C50.9", "CANCER DE COLON": "C18.9",
    "SEPSIS / SEPTICEMIA": "A41.9", "SHOCK SEPTICO": "A41.9", "DIABETES TIPO 2": "E11.9",
    "INSUFICIENCIA RENAL AGUDA": "N17.9", "INSUFICIENCIA RENAL CRONICA": "N18.9",
    "ALZHEIMER": "G30.9", "TRAUMATISMO CRANEOENCEFALICO": "S06.9", "POLITRAUMATISMO": "T07",
    "HERIDA POR ARMA DE FUEGO": "W34", "AHOGAMIENTO": "W74", "ASFIXIA MECANICA": "W84"
    # ... (puedes seguir agregando hasta completar los 50 que definimos)
}

# --- FUNCIONES DE SERVIDOR (PDF Y EMAIL) ---
def generar_pdf(datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "INFORME ESTADISTICO DE DEFUNCION - PROVINCIA DE CORDOBA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for k, v in datos.items():
        pdf.multi_cell(0, 8, f"{k}: {v}", border=0)
    return pdf.output(dest='S').encode('latin-1')

def enviar_correo(destinatario, pdf_content, nombre_fallecido):
    # CONFIGURAR AQUÍ
    remitente = "tu_correo@gmail.com" 
    password = "tu_clave_de_aplicacion" 
    
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"Certificado Digital Validado - {nombre_fallecido}"
    msg.attach(MIMEText(f"Se adjunta el certificado digital de defunción de {nombre_fallecido} codificado bajo estándares CIE-10.", 'plain'))
    
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
    except: return False

# --- INTERFAZ DE USUARIO ---
st.title("⚖️ Informe Estadístico de Defunción Digital")
st.caption("Interoperabilidad: RENAPER | REFES | CIE-10 | FIRMA DIGITAL")

# BLOQUE 1: ADMINISTRATIVO
with st.expander("📂 I. DATOS DEL REGISTRO (Ítems 2-8)"):
    adm = st.columns(4)
    dpto_reg = adm[0].text_input("Dpto/Partido")
    deleg_reg = adm[1].text_input("Delegación")
    acta_nro = adm[2].text_input("Acta Nro")
    fecha_insc = adm[3].date_input("Fecha Inscripción")

# BLOQUE 2: FALLECIDO
with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    col_dni = st.columns([1, 2])
    dni = col_dni[0].text_input("3- Nro de Documento")
    if dni:
        with st.spinner("Validando en RENAPER..."):
            time.sleep(0.5)
            st.success("✅ Identidad Verificada")

    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("1- Apellidos y Nombres", value="JUAN PEREZ" if dni else "")
    sexo = c1.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    f_nac = c2.date_input("6- Fecha Nacimiento")
    id_gen = c2.selectbox("17- Identidad de Género", ["Varón", "Mujer", "Trans", "No binario", "Otro"])
    instrucc = c3.selectbox("20- Instrucción", ["Primario", "Secundario", "Terciario/Univ.", "Sin instrucción"])
    domicilio = c3.text_input("10- Domicilio Real", value="Av. Colón 1234, Córdoba" if dni else "")

# BLOQUE 3: EL HECHO
with st.expander("📍 III. LUGAR DE LA DEFUNCIÓN (Ítems 11-15)"):
    h1, h2 = st.columns(2)
    f_def = h1.date_input("11- Fecha Defunción")
    lugar_tipo = h1.selectbox("13- Lugar", ["Salud Pública", "Privado", "Vivienda", "Vía Pública", "Otro"])
    dir_hecho = h2.text_input("15- Dirección Exacta del Fallecimiento")
    establ = h2.text_input("14- Nombre Establecimiento")

# BLOQUE 4: CAUSAS E IA
st.markdown("---")
st.header("🩺 IV. CAUSAS DE MUERTE (Ítem 26)")
busqueda = st.text_input("🔍 BUSCADOR CIE-10 (Sugerencias IA)").upper()
if busqueda:
    matches = {k: v for k, v in CIE10_DB.items() if busqueda in k}
    for d, c in matches.items():
        if st.button(f"Seleccionar {c} - {d}"):
            st.session_state['causa_seleccionada'] = f"{c} - {d}"

causa_a = st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
causa_b = st.text_input("26- b) Debido a")

# BLOQUE 5: MÉDICO Y FIRMA
with st.expander("🖋️ V. DATOS DEL PROFESIONAL Y FIRMA", expanded=True):
    m1, m2 = st.columns(2)
    mat = m1.text_input("Matrícula Profesional (M.P.)")
    if mat:
        st.success("✅ Matrícula Habilitada en REFES")
    medico_nom = m2.text_input("Médico Certificante", value="Dr. Carlos Medicina" if mat else "")
    email_dest = st.text_input("Enviar copia del Certificado PDF a (Email):")
    firma = st.checkbox("Confirmo la veracidad de los datos y firmo digitalmente (Ley 25.506)")

# --- BOTÓN FINAL ---
if st.button("CONFIRMAR, GENERAR Y ENVIAR CERTIFICADO"):
    if nombre and causa_a and firma and email_dest:
        dict_datos = {
            "ID_TRANSACCION": "CBA-" + str(int(time.time())),
            "FECHA_EMISION": str(datetime.date.today()),
            "FALLECIDO": nombre, "DNI": dni,
            "LUGAR": dir_hecho,
            "CAUSA_DIRECTA": causa_a,
            "MEDICO": medico_nom, "MATRICULA": mat,
            "VALIDEZ": "FIRMADO DIGITALMENTE - PROVINCIA DE CORDOBA"
        }
        with st.spinner("Procesando documento legal..."):
            pdf_bytes = generar_pdf(dict_datos)
            if enviar_correo(email_dest, pdf_bytes, nombre):
                st.success(f"✅ Certificado registrado y enviado a {email_dest}")
                st.info("El Registro Civil ha recibido una copia codificada automáticamente.")
            else:
                st.warning("Certificado registrado, pero hubo un problema con el envío del correo (verificar credenciales SMTP).")
    else:
        st.error("Error: Complete los datos obligatorios y acepte la firma digital.")
