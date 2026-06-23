import streamlit as st
import requests
import pandas as pd
from utils.utils import generar_csv_bytes

# Configuración de página
st.set_page_config(
  
)
col1, col2, col3 = st.columns([0.1, 50, 0.1])

with col2:
    st.image("assets/logo.png", width=900)


# Constantes
BASE_URL = "http://127.0.0.1:8000/api/v1" 
MAPA_ESTADOS = {"Vivo": "alive", "Muerto": "dead", "Desconocido": "unknown"}
MAPA_GENEROS = {"Femenino": "female", "Masculino": "male", "Sin género": "genderless", "Desconocido": "unknown"}
BADGE_COLOR = {"Alive": "🟢", "Dead": "🔴", "unknown": "⚪"}

def consultar_api(endpoint: str, params: dict = None):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"total_records": 0, "data": []}
        else:
            st.error(f"Error del servidor ({response.status_code})")
            return None
    except requests.exceptions.ConnectionError:
        st.error(" No se pudo conectar con el backend. Verifica que FastAPI esté corriendo en el puerto 8000.")
        return None



def mostrar_visor(data: list, categoria: str):
    st.markdown("---")
    st.subheader(f"🔎 Visor de datos — {len(data)} registros")
    
    vista = st.radio("Vista:", [" Tabla", "Informacion"], horizontal=True, key=f"vista_{categoria}")

    if vista == " Tabla":
        st.dataframe(pd.DataFrame(data), width=1000, height=500)
    else:
        if categoria == "Personajes":
            cols = st.columns(4)
            for i, p in enumerate(data):
                with cols[i % 4]:
                    if p.get("image"): st.image(p["image"], use_container_width=True)
                    estado = p.get("status", "unknown")
                    st.markdown(f"**{p.get('name', '—')}**")
                    st.caption(f"{BADGE_COLOR.get(estado, '⚪')} {estado} · {p.get('species', '—')} · {p.get('gender', '—')}")
                    st.markdown("---")
        elif categoria == "Ubicaciones":
            cols = st.columns(3)
            for i, loc in enumerate(data):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"**📍 {loc.get('name', '—')}**")
                        st.caption(f"Tipo: {loc.get('type', '—')} | Dimensión: {loc.get('dimension', '—')}")
        elif categoria == "Episodios":
            cols = st.columns(3)
            # TMDB ID de Rick & Morty
            TMDB_ID = "60625" 
            
            for i, ep in enumerate(data):
                with cols[i % 3]:
                    with st.container(border=True, height=220):
                        st.markdown(f"**🎬 {ep.get('episode', 'S00E00')}**")
                        st.markdown(f"**{ep.get('name', 'Sin título')}**")
                        st.caption(f"📅 Emitido: {ep.get('air_date', '—')}")
                        
                        # Generación VidAPI(Con Anuncios)
                        cod = ep.get('episode', 'S01E01')
                        try:
                    
                            import re
                            numeros = re.findall(r'\d+', cod)
                            
                            if len(numeros) >= 2:
                                s = int(numeros[0])
                                e = int(numeros[1])
                                
                                url_video = f"https://vidapi.qzz.io/tv/{TMDB_ID}/{s}/{e}"
                                
                                st.link_button("▶️ Ver episodio", url_video, use_container_width=True)
                            else:
                                st.warning("Formato no reconocido")
                                
                        except Exception:
                            st.error("Error al generar enlace")

# ==============================================================================
# CUERPO PRINCIPAL 
# ==============================================================================
col_izq, col_centro, col_der = st.columns([0.1, 50, 0.1])

with col_centro:
    st.markdown("---")
    st.header("📦 Centro de Consultas")

    tipo_descarga = st.radio("Modalidad:", ["Completo", "Filtrado"], horizontal=True)
    categoria = st.selectbox("Dataset:", ["Personajes", "Ubicaciones", "Episodios"])
    
    endpoint_map = {"Personajes": "personajes", "Ubicaciones": "ubicaciones", "Episodios": "episodios"}
    endpoint_api = endpoint_map[categoria]

    params = {}
    if tipo_descarga == "Filtrado":
        if categoria == "Personajes":
            f_status = st.selectbox("Estado:", ["Todos", "Vivo", "Muerto", "Desconocido"])
            f_gender = st.selectbox("Género:", ["Todos", "Femenino", "Masculino", "Sin género", "Desconocido"])
            if f_status != "Todos": params["status"] = MAPA_ESTADOS[f_status]
            if f_gender != "Todos": params["gender"] = MAPA_GENEROS[f_gender]
        elif categoria == "Ubicaciones":
            
            # Nueva lista de dimensiones obtenida de tu diagnóstico
            dimensiones = [
                "Todas", 'Cronenberg Dimension', 'Dimension 5-126', 
                'Dimension C-137', 'Fantasy Dimension', 
                'Post-Apocalyptic Dimension', 'Replacement Dimension', 'unknown'
            ]
            f_dim = st.selectbox("Dimensión:", dimensiones)
            if f_dim != "Todas": 
                params["dimension"] = f_dim
        elif categoria == "Episodios":
            temporadas = ["Todas", "S01", "S02", "S03", "S04", "S05"]
            f_temp = st.selectbox("Selecciona una temporada:", temporadas)
            
            
            if f_temp != "Todas":
                params["episode"] = f_temp 


    if st.button("🔍 Consultar", type="primary", use_container_width=True):
        with st.spinner("Consultando..."):
            res = consultar_api(endpoint_api, params=params)
            st.session_state["res"] = res
            st.session_state["cat"] = categoria
            st.session_state["ep"] = endpoint_api

    if st.session_state.get("res"):
        res = st.session_state["res"]
        if res and res.get("data"):
            st.success(f"✅ {res['total_records']} registros encontrados.")
            st.download_button("⬇️ Descargar CSV", generar_csv_bytes(res["data"]), 
                               f"{st.session_state['ep']}.csv", "text/csv", use_container_width=True)
            mostrar_visor(res["data"], st.session_state["cat"])
        else:
            st.warning("No se encontraron registros.")