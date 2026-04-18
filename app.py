import streamlit as st

st.set_page_config(page_title="Prototipo Defunción Córdoba", page_icon="🏥")

st.title("🏥 Sistema de Defunción Digital")
st.write("Provincia de Córdoba - Módulo de Codificación Automática")

# Contenedor principal
with st.container():
    st.header("Causas de la Defunción (Ítem 26)")
    st.info("Escriba el diagnóstico y la IA sugerirá el código CIE-10 en tiempo real.")

    # Campo de texto para la causa
    causa_input = st.text_area("Causa Directa (a):", placeholder="Ejemplo: Neumonía, Infarto, Insuficiencia renal...")

    # --- LÓGICA DE CODIFICACIÓN VISIBLE ---
    if causa_input:
        # Diccionario de simulación de IA (puedes agregar más para la demo)
        sugerencias = {
            "neumonia": "J18.9 (Neumonía, no especificada)",
            "infarto": "I21.9 (Infarto agudo de miocardio)",
            "renal": "N17.9 (Insuficiencia renal aguda)",
            "diabetes": "E14.9 (Diabetes mellitus)",
            "covid": "U07.1 (COVID-19, virus identificado)",
            "paro": "I46.9 (Paro cardíaco, no especificado)"
        }

        # Buscamos coincidencias
        encontrado = False
        for clave, codigo in sugerencias.items():
            if clave in causa_input.lower():
                # ESTO ES LO QUE SE VERÁ EN LA PRESENTACIÓN
                st.success(f"✨ **Sugerencia de Codificación IA:**")
                st.metric(label="Código CIE-10 Detectado", value=codigo)
                st.caption("La IA analizó el texto y vinculó el diagnóstico al estándar internacional.")
                encontrado = True
                break
        
        if not encontrado and len(causa_input) > 3:
            st.warning("🔍 La IA está analizando términos médicos complejos... (Buscando en base de datos CIE-11)")

st.divider()

# Simulación de otros campos para que no se vea vacío
col1, col2 = st.columns(2)
with col1:
    st.text_input("Nombre del Fallecido")
with col2:
    st.text_input("Matrícula del Médico")

if st.button("Validar y Guardar"):
    st.balloons()
    st.success("Certificado Codificado y Enviado.")
