import streamlit as st
import datetime
import time

# Configuración institucional
st.set_page_config(page_title="Sistema Digital de Defunción - Córdoba", layout="wide", page_icon="⚖️")

# --- BASE DE DATOS CIE-10 (50 CÓDIGOS) ---
CIE10_DB = {
    "INFARTO AGUDO DE MIOCARDIO": "I21.9", "INSUFICIENCIA CARDIACA": "I50.9", 
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10",
    "SHOCK CARDIOGENICO": "R57.0", "ARRITMIA VENTRICULAR": "I47.2",
    "ANEURISMA DE AORTA": "I71.9", "EMBOLIA PULMONAR": "I26.9",
    "PARO CARDIORRESPIRATORIO": "I46.9", "MIOCARDITIS": "I40.9",
    "NEUMONIA": "J18.9", "EPOC (ENFERMEDAD PULMONAR OBSTRUCTIVA)": "J44.9",
    "INSUFICIENCIA RESPIRATORIA AGUDA": "J96.0", "ASMA BRONQUIAL": "J45.9",
    "EDEMA AGUDO DE PULMON": "J81", "BRONQUITIS CRONICA": "J42",
    "COVID-19": "U07.1", "GRIPE / INFLUENZA": "J11.1",
    "CANCER DE PULMON": "C34.9", "CANCER DE MAMA": "C50.9", 
    "CANCER DE COLON": "C18.9", "CANCER DE PROSTATA": "C61",
    "CANCER DE PANCREAS": "C25.9", "CANCER DE ESTOMAGO": "C16.9",
    "LEUCEMIA LINFOIDE": "C91.9", "LINFOMA NO HODGKIN": "C85.9",
    "TUMOR CEREBRAL": "C71.9", "CANCER DE HIGADO": "C22.0",
    "SEPSIS / SEPTICEMIA": "A41.9", "SHOCK SEPTICO": "A41.9",
    "DIABETES MELLITUS TIPO 2": "E11.9", "CIRROSIS HEPATICA": "K74.6",
    "INSUFICIENCIA RENAL AGUDA": "N17.9", "INSUFICIENCIA RENAL CRONICA": "N18.9",
    "MENINGITIS BACTERIANA": "G00.9", "TUBERCULOSIS PULMONAR": "A15.0",
    "HIV / SIDA": "B24", "DENGUE GRAVE": "A91",
    "ALZHEIMER": "G30.9", "DEMENCIA SENIL": "F03",
    "TRAUMATISMO CRANEOENCEFALICO (TCE)": "S06.9", "POLITRAUMATISMO": "T07",
    "HERIDA POR ARMA DE FUEGO": "W34", "HERIDA POR ARMA BLANCA": "W26",
    "INTOXICACION POR MONOXIDO DE CARBONO": "T58", "AHOGAMIENTO": "W74",
    "QUEMADURAS GRAVES": "T30.0", "ASFIXIA MECANICA": "W84",
    "CAIDA DE ALTURA": "W19", "SINCOPE": "R55"
}

if 'causa_seleccionada' not in st.session_state:
    st.session_state['causa_seleccionada'] = ""

st.title("⚖️ Registro Digital de Defunción - Córdoba")
st.caption("Módulo de Integración RENAPER / REFES / Ciudadano Digital")

# --- SECCIÓN 1: DATOS DEL REGISTRO ---
with st.expander("📂 I. DATOS DEL REGISTRO CIVIL"):
    c_reg = st.columns(4)
    c_reg[0].text_input("Dpto/Partido")
    c_reg[1].text_input("Delegación")
    c_reg[2].text_input("Acta Nro")
    c_reg[3].date_input("Fecha Inscripción")

# --- SECCIÓN 2: PACIENTE (CON SIMULACIÓN RENAPER) ---
with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    col_dni1, col_dni2 = st.columns([1, 2])
    dni_input = col_dni1.text_input("3- Nro de Documento (Presione Enter para validar)")
    
    if dni_input:
        with st.spinner("Consultando base de RENAPER..."):
            time.sleep(1) # Simulación de delay de API
            st.success("✅ Identidad validada en RENAPER")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("1- Apellidos y Nombres", value="JUAN PEREZ" if dni_input else "")
        sexo = st.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    with col2:
        f_nac = st.date_input("6- Fecha Nacimiento", value=datetime.date(1960,1,1))
        st.selectbox("17- Identidad de Género", ["Varón", "Mujer", "Trans", "No binario", "Otro"])
    with col3:
        st.text_input("8- Domicilio Legal", value="Av. Colón 1234, Córdoba" if dni_input else "")
        st.text_input("22- Ocupación habitual")

# --- SECCIÓN 3: EL HECHO ---
with st.expander("📍 III. LUGAR DE LA DEFUNCIÓN"):
    c_hecho = st.columns(3)
    c_hecho[0].date_input("11- Fecha Defunción")
    c_hecho[1].time_input("12- Hora Defunción")
    c_hecho[2].selectbox("13- Lugar", ["Salud Pública", "Privado", "Vivienda", "Vía Pública", "Otro"])
    st.text_input("15- Dirección Exacta del Hecho (Calle, Nro, Localidad)")

# --- SECCIÓN 4: CAUSAS Y BUSCADOR CIE-10 ---
st.markdown("---")
st.header("🩺 IV. CERTIFICACIÓN MÉDICA")
busqueda = st.text_input("🔍 BUSCADOR DE DIAGNÓSTICOS (Ej: ACV, Cancer, Infarto...)", "").upper()

if busqueda:
    matches = {k: v for k, v in CIE10_DB.items() if busqueda in k}
    if matches:
        for diag, cod in matches.items():
            if st.button(f"Seleccionar: {cod} - {diag}"):
                st.session_state['causa_seleccionada'] = f"{cod} - {diag}"

c_causas = st.columns([2, 1])
with c_causas[0]:
    st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
    st.text_input("26- b) Debido a")
with c_causas[1]:
    st.selectbox("35- Determinación", ["Historia Clínica", "Autopsia", "Laboratorio"])

# --- SECCIÓN 5: MÉDICO (CON SIMULACIÓN REFES) ---
with st.expander("🖋️ V. DATOS DEL PROFESIONAL Y FIRMA", expanded=True):
    m1, m2 = st.columns(2)
    mat_input = m1.text_input("Matrícula Profesional (M.P.)")
    
    if mat_input:
        with st.spinner("Validando matrícula en REFES..."):
            time.sleep(1)
            st.success("✅ Profesional habilitado: Dr. Carlos Medicina (Especialidad: Cardiología)")
    
    m2.text_input("Nombre del Médico", value="Carlos Medicina" if mat_input else "")
    
    st.markdown("---")
    st.markdown("### 🖋️ Firma Digital")
    st.warning("Al confirmar, usted está firmando digitalmente este documento con validez legal según Ley 25.506.")
    check_firma = st.checkbox("Yo, el profesional certificante, confirmo la veracidad de los datos y firmo digitalmente.")

# --- FINALIZAR ---
if st.button("CONFIRMAR Y CERRAR CERTIFICADO"):
    if nombre and st.session_state['causa_seleccionada'] and check_firma:
        st.success("✅ CERTIFICADO FIRMADO Y REGISTRADO")
        st.markdown(f"""
            **Documento Electrónico Generado:**
            - **ID Transacción:** CBA-REFES-99283
            - **Hash de Seguridad:** 8f2d1e...9a
            - **Estado:** Enviado a Registro Civil y Ministerio de Salud.
        """)
        st.info("Se ha generado un PDF firmado que será enviado al correo institucional del médico y del Registro Civil.")
    elif not check_firma:
        st.error("Debe marcar el cuadro de firma digital para continuar.")
    else:
        st.error("Faltan datos críticos para el registro.")
