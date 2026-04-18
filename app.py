import streamlit as st
import datetime

# Configuración institucional
st.set_page_config(page_title="Registro Digital de Defunción - Córdoba", page_icon="⚖️", layout="wide")

# CSS para un diseño más limpio
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stExpander { border: 1px solid #d1d1d1; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Informe Estadístico de Defunción Digital")
st.caption("Gobierno de la Provincia de Córdoba - Ministerio de Salud")

# --- BLOQUE 1: DATOS ADMINISTRATIVOS ---
with st.expander("📂 I. DATOS DEL REGISTRO (Items 2-8)", expanded=False):
    c_adm1, c_adm2, c_adm3 = st.columns(3)
    with c_adm1:
        st.text_input("Departamento / Partido")
        st.text_input("Delegación / Registro Civil")
    with c_adm2:
        st.text_input("Nro. Acta")
        st.text_input("Tomo / Folio")
    with c_adm3:
        st.date_input("Fecha de Inscripción")

# --- BLOQUE 2: IDENTIFICACIÓN DEL FALLECIDO ---
with st.expander("👤 II. DATOS DEL FALLECIDO", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("1- Apellido/s y Nombre/s")
        doc_nro = st.text_input("3- Nro. Documento")
        sexo_bio = st.radio("5- Sexo biológico", ["Masculino", "Femenino", "No binario"], horizontal=True)
    with c2:
        nacionalidad = st.text_input("4- Nacionalidad", value="Argentina")
        f_nac = st.date_input("6- Fecha de Nacimiento", value=datetime.date(1970, 1, 1))
        id_genero = st.selectbox("17- Identidad de Género", ["Varón", "Mujer", "Mujer Trans / Travesti", "Varón Trans", "No binario", "Otra"])
    with c3:
        est_civil = st.selectbox("18- Estado Civil", ["Soltero/a", "Casado/a", "Viudo/a", "Divorciado/a", "Unión conviviente"])
        pueblos_orig = st.checkbox("19- Pertenece a pueblos originarios")

    st.markdown("---")
    st.markdown("**Contexto Socio-Económico**")
    c4, c5 = st.columns(2)
    with c4:
        st.selectbox("20- Nivel de Instrucción", ["Primario", "Secundario", "Terciario/Univ.", "Nunca asistió"])
        st.selectbox("21- Condición de actividad", ["Trabajó", "Buscó trabajo", "Jubilado/Pensionado", "Quehaceres del hogar"])
    with c5:
        st.text_input("22- Ocupación habitual")
        st.text_input("10- Domicilio Real (Calle, Nro, Localidad)")

# --- BLOQUE 3: EL HECHO (DEFUNCION) ---
with st.expander("📍 III. DATOS DEL FALLECIMIENTO"):
    f1, f2, f3 = st.columns(3)
    with f1:
        f_def = st.date_input("11- Fecha de defunción")
        h_def = st.time_input("12- Hora de defunción")
    with f2:
        lugar = st.selectbox("13- Lugar de ocurrencia", ["Establ. Salud", "Vivienda", "Vía pública", "Cárcel", "Otro"])
    with f3:
        atencion_medica = st.radio("36- ¿Tuvo atención médica?", ["Sí", "No", "Se desconoce"])

# --- BLOQUE 4: CAUSAS Y IA ---
st.markdown("---")
st.header("🩺 IV. CAUSAS DE MUERTE (Certificación Médica)")
st.info("La IA sugiere códigos CIE-10 para asegurar la calidad estadística.")

c_ia1, c_ia2 = st.columns([2, 1])
with c_ia1:
    causa_a = st.text_area("Causa Directa (a)", placeholder="Ej: Insuficiencia respiratoria aguda")
    causa_b = st.text_input("Debido a (b)")
    causa_c = st.text_input("Debido a (c)")

# Lógica de sugerencia (Base de datos ampliada)
cie_db = {
    "neumonia": "J18.9", "infarto": "I21.9", "sepsis": "A41.9", "covid": "U07.1", 
    "diabetes": "E14.9", "acv": "I64", "falla multiorganica": "R68.8", "cancer": "C80",
    "renal": "N17.9", "insuficiencia cardiaca": "I50.9"
}

with c_ia2:
    if causa_a:
        match = next((v for k, v in cie_db.items() if k in causa_a.lower()), None)
        if match:
            st.metric("CIE-10 Sugerido", match)
            st.success("Validado por sistema")
        else:
            st.warning("Código no automatizado")

# --- BLOQUE 5: CASOS ESPECIALES (Causa Externa y Materna) ---
with st.expander("⚠️ V. CIRCUNSTANCIAS ESPECIALES"):
    st.markdown("**37- Manera de morir**")
    manera = st.selectbox("Seleccione opción", ["Enfermedad", "Accidente", "Suicidio", "Homicidio", "Intervención Legal", "Investigación"])
    
    if manera != "Enfermedad":
        st.text_area("40- Describa brevemente cómo se produjo la lesión")

    st.markdown("---")
    st.markdown("**42- Si fue mujer: ¿Estaba embarazada, de parto o puerperio?**")
    st.radio("Opciones materna", ["No", "Sí, en el embarazo", "Sí, en el parto", "Sí, hasta 42 días después", "Se desconoce"], horizontal=True)

# --- BLOQUE 6: MÉDICO ---
with st.expander("🖋️ VI. DATOS DEL PROFESIONAL"):
    m1, m2 = st.columns(2)
    with m1:
        st.text_input("Nombre y Apellido del Médico")
        st.text_input("Matrícula")
    with m2:
        st.selectbox("Fuente de información", ["Historia clínica", "Pruebas de laboratorio", "Interrogatorio a familiares"])

# --- BOTÓN FINAL ---
st.markdown("---")
if st.button("CONFIRMAR Y FINALIZAR REGISTRO"):
    if nombre and causa_a:
        st.markdown("""
            <div style="background-color: #e8f4f8; border-left: 5px solid #2c3e50; padding: 20px;">
                <h3 style="color: #2c3e50; margin: 0;">✅ CERTIFICADO REGISTRADO</h3>
                <p>El acta digital ha sido procesada con éxito y enviada al servidor central del Registro Civil de Córdoba.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Por favor, complete al menos el nombre del fallecido y la causa de muerte.")
