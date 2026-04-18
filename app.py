import streamlit as st
import datetime

# Configuración de página
st.set_page_config(page_title="Sistema Digital de Defunción - Córdoba", layout="wide", page_icon="⚖️")

# --- BASE DE DATOS EXPANDIDA CIE-10 (50 CÓDIGOS) ---
CIE10_DB = {
    # CARDIOVASCULARES
    "INFARTO AGUDO DE MIOCARDIO": "I21.9", "INSUFICIENCIA CARDIACA": "I50.9", 
    "ACCIDENTE CEREBROVASCULAR (ACV)": "I64", "HIPERTENSION ARTERIAL": "I10",
    "SHOCK CARDIOGENICO": "R57.0", "ARRITMIA VENTRICULAR": "I47.2",
    "ANEURISMA DE AORTA": "I71.9", "EMBOLIA PULMONAR": "I26.9",
    "PARO CARDIORRESPIRATORIO": "I46.9", "MIOCARDITIS": "I40.9",
    # RESPIRATORIAS
    "NEUMONIA": "J18.9", "EPOC (ENFERMEDAD PULMONAR OBSTRUCTIVA)": "J44.9",
    "INSUFICIENCIA RESPIRATORIA AGUDA": "J96.0", "ASMA BRONQUIAL": "J45.9",
    "EDEMA AGUDO DE PULMON": "J81", "BRONQUITIS CRONICA": "J42",
    "COVID-19": "U07.1", "GRIPE / INFLUENZA": "J11.1",
    # TUMORES / CÁNCER
    "CANCER DE PULMON": "C34.9", "CANCER DE MAMA": "C50.9", 
    "CANCER DE COLON": "C18.9", "CANCER DE PROSTATA": "C61",
    "CANCER DE PANCREAS": "C25.9", "CANCER DE ESTOMAGO": "C16.9",
    "LEUCEMIA LINFOIDE": "C91.9", "LINFOMA NO HODGKIN": "C85.9",
    "TUMOR CEREBRAL": "C71.9", "CANCER DE HIGADO": "C22.0",
    # INFECCIOSAS Y OTROS
    "SEPSIS / SEPTICEMIA": "A41.9", "SHOCK SEPTICO": "A41.9",
    "DIABETES MELLITUS TIPO 2": "E11.9", "CIRROSIS HEPATICA": "K74.6",
    "INSUFICIENCIA RENAL AGUDA": "N17.9", "INSUFICIENCIA RENAL CRONICA": "N18.9",
    "MENINGITIS BACTERIANA": "G00.9", "TUBERCULOSIS PULMONAR": "A15.0",
    "HIV / SIDA": "B24", "DENGUE GRAVE": "A91",
    "ALZHEIMER": "G30.9", "DEMENCIA SENIL": "F03",
    # CAUSAS EXTERNAS / TRAUMAS
    "TRAUMATISMO CRANEOENCEFALICO (TCE)": "S06.9", "POLITRAUMATISMO": "T07",
    "HERIDA POR ARMA DE FUEGO": "W34", "HERIDA POR ARMA BLANCA": "W26",
    "INTOXICACION POR MONOXIDO DE CARBONO": "T58", "AHOGAMIENTO": "W74",
    "QUEMADURAS GRAVES": "T30.0", "ASFIXIA MECANICA": "W84",
    "CAIDA DE ALTURA": "W19", "SINCOPE": "R55"
}

# Mantener la causa seleccionada en la sesión
if 'causa_seleccionada' not in st.session_state:
    st.session_state['causa_seleccionada'] = ""

st.title("⚖️ Registro Digital de Defunción - Córdoba")
st.info("Formulario completo adaptado al formato digital (Ítems 1-43)")

# --- SECCIÓN 1: DATOS DEL REGISTRO ---
with st.expander("📂 I. DATOS DEL REGISTRO CIVIL"):
    c_reg = st.columns(4)
    c_reg[0].text_input("Dpto/Partido")
    c_reg[1].text_input("Delegación")
    c_reg[2].text_input("Acta Nro")
    c_reg[3].date_input("Fecha Inscripción")

# --- SECCIÓN 2: DATOS DEL FALLECIDO ---
with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("1- Apellidos y Nombres")
        doc = st.text_input("3- Nro de Documento")
        sexo = st.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True)
    with col2:
        f_nac = st.date_input("6- Fecha Nacimiento", value=datetime.date(1960,1,1))
        st.selectbox("17- Identidad de Género", ["Varón", "Mujer", "Trans", "No binario", "Otro"])
        st.selectbox("20- Nivel Instrucción", ["Primario", "Secundario", "Terciario/Univ.", "Sin instrucción"])
    with col3:
        st.text_input("8- Domicilio Legal")
        st.text_input("10- Domicilio Real")
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
st.write("Escriba para buscar entre los 50 diagnósticos precargados:")

busqueda = st.text_input("🔍 BUSCADOR DE DIAGNÓSTICOS (Ej: ACV, Cancer, Infarto...)", "").upper()

if busqueda:
    matches = {k: v for k, v in CIE10_DB.items() if busqueda in k}
    if matches:
        st.write("Sugerencias encontradas:")
        for diag, cod in matches.items():
            if st.button(f"Seleccionar: {cod} - {diag}"):
                st.session_state['causa_seleccionada'] = f"{cod} - {diag}"
    else:
        st.warning("No se encontraron coincidencias exactas.")

# Campos de causas (Ítem 26)
c_causas = st.columns([2, 1])
with c_causas[0]:
    st.text_area("26- a) Causa Directa", value=st.session_state['causa_seleccionada'])
    st.text_input("26- b) Debido a")
    st.text_area("27- Otros estados significativos")
with c_causas[1]:
    st.selectbox("35- Determinación", ["Historia Clínica", "Autopsia", "Laboratorio"])
    st.radio("36- ¿Atención médica?", ["Sí", "No", "Se desconoce"])

# --- SECCIÓN 5: CASOS ESPECIALES ---
with st.expander("⚠️ V. CAUSAS EXTERNAS / MENORES / MATERNA"):
    st.selectbox("37- Manera de morir", ["Enfermedad", "Accidente", "Suicidio", "Homicidio", "Investigación"])
    st.markdown("**Si es menor de 1 año:**")
    c_min = st.columns(2)
    c_min[0].number_input("28- Peso al nacer (grs)", 0)
    c_min[1].number_input("29- Semanas gestación", 0)

# --- SECCIÓN 6: MÉDICO ---
with st.expander("🖋️ VI. DATOS DEL PROFESIONAL"):
    c_med = st.columns(2)
    c_med[0].text_input("Nombre del Médico")
    c_med[1].text_input("Matrícula (M.P.)")

# --- FINALIZAR ---
if st.button("CONFIRMAR Y CERRAR CERTIFICADO"):
    if nombre and st.session_state['causa_seleccionada']:
        st.success("✅ CERTIFICADO CONFIRMADO Y CODIFICADO")
        st.info(f"Fallecido: {nombre} | Código CIE-10: {st.session_state['causa_seleccionada']}")
    else:
        st.error("Faltan datos críticos para el registro.")
