import streamlit as st
import datetime

# 1. Configuración de página - Debe ser la primera instrucción de Streamlit
st.set_page_config(page_title="Defunción Digital Córdoba", layout="centered")

# 2. Encabezado basado en el modelo de informe [cite: 1]
st.title("🏥 Registro Digital de Defunción")
st.subheader("Provincia de Córdoba - Prototipo Estadístico")

# --- SECCIÓN: DATOS DEL PACIENTE (78% de la carga de datos) ---
with st.form("formulario_defuncion"):
    st.header("1. Datos del Fallecido")
    
    col1, col2 = st.columns(2)
    with col1:
        # Campos del PDF [cite: 9, 10, 11]
        nombre = st.text_input("1- Nombre/s y Apellido/s")
        tipo_doc = st.selectbox("2- Tipo Doc", ["DNI", "Pasaporte", "LC", "LE"])
        nro_doc = st.text_input("3- Nro. Documento")
        sexo = st.radio("5- Sexo", ["Masculino", "Femenino", "No binario"], horizontal=True) # [cite: 16, 19, 20]
    
    with col2:
        # Campos del PDF [cite: 12, 14, 102]
        nacionalidad = st.text_input("4- Nacionalidad", value="Argentina")
        fecha_nac = st.date_input("6- Fecha de nacimiento", value=datetime.date(1960, 1, 1))
        instruccion = st.selectbox("20- Máximo nivel de instrucción", 
                                 ["Primario", "Secundario", "Terciario", "Universitario", "Posgrado"])

    st.divider()

    # --- SECCIÓN: CAUSAS (Simulación de IA) ---
    st.header("2. Causas de la Defunción")
    st.caption("Complete la causa directa. El sistema sugerirá códigos CIE automáticamente.")
    
    # Campo para el Item 26-a del PDF [cite: 156]
    causa_a = st.text_area("a) Enfermedad o condición patológica directa", 
                           placeholder="Ej: Insuficiencia respiratoria aguda")

    # Lógica de sugerencia de IA (simulada para el prototipo)
    if causa_a:
        if "respiratoria" in causa_a.lower() or "neumo" in causa_a.lower():
            st.info("✨ **Sugerencia de IA:** Se detectó patrón respiratorio. Código CIE-10 sugerido: **J18.9**. ¿Fue consecuencia de COVID-19?")
        elif "cardiaco" in causa_a.lower() or "infarto" in causa_a.lower():
            st.info("✨ **Sugerencia de IA:** Se detectó patrón cardíaco. Código CIE-10 sugerido: **I21.9**.")

    st.divider()

    # --- SECCIÓN: DATOS DEL MÉDICO (12% de la carga de datos) ---
    st.header("3. Datos del Profesional")
    col3, col4 = st.columns(2)
    with col3:
        # Campos del PDF [cite: 289, 290]
        medico_nombre = st.text_input("Nombre y Apellido del Certificante")
        matricula = st.text_input("Matrícula Profesional")
    with col4:
        # Campos del PDF [cite: 291, 295]
        domicilio_prof = st.text_input("Domicilio Profesional")
        telefono = st.text_input("Teléfono de contacto")

    # Botón de envío
    enviado = st.form_submit_button("Firmar y Enviar Certificado")
    
    if enviado:
        if nombre and medico_nombre and matricula:
            st.success(f"Certificado de {nombre} enviado con éxito por el Dr./a {medico_nombre}.")
            st.balloons()
        else:
            st.error("Por favor, complete los campos obligatorios (Nombre, Médico y Matrícula).")