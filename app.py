import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium
from sklearn.cluster import KMeans

# Configurações globais
PAGE_TITLE = "Planejador Logistico"
DEFAULT_COORDS = [-22.86, -43.23] #Isso aqui é fundão
CLUSTER_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
OSRM_NEAREST_URL = "https://router.project-osrm.org/nearest/v1/driving/{lon},{lat}"

def init_state():
    if 'locations' not in st.session_state:
        st.session_state.locations = []
    if 'last_click' not in st.session_state:
        st.session_state.last_click = None

@st.cache_data(show_spinner=False)
def snap_to_road(lat, lon):
    # A média do K-means pode cair em água (rio, baía, lago). O OSRM "encaixa"
    # a coordenada no ponto mais próximo da malha viária real (sempre terra/rua).
    try:
        url = OSRM_NEAREST_URL.format(lon=lon, lat=lat)
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        waypoints = resp.json().get('waypoints') or []
        if not waypoints:
            return lat, lon
        snapped_lon, snapped_lat = waypoints[0]['location']
        return snapped_lat, snapped_lon
    except requests.RequestException:
        return lat, lon

def get_clusters(locations, k):
    if len(locations) <= k:
        return None, None

    df = pd.DataFrame(locations, columns=['lat', 'lon'])
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    model.fit(df)

    centers = [snap_to_road(lat, lon) for lat, lon in model.cluster_centers_]
    return model.labels_, centers

def main():
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    init_state()

    # --- Sidebar ---
    with st.sidebar:
        st.header("Parâmetros")
        n_centers = st.slider("Nº de Centros (Clusters)", 1, 5, 3)
        st.divider()
        st.metric("Pontos de Entrega", len(st.session_state.locations))
        
        if st.button("Resetar Dados", type="primary"):
            st.session_state.locations = []
            st.session_state.last_click = None
            st.rerun()

    # --- Main Content ---
    st.title("🚚 Otimização de Malha Logística")
    st.caption("Clique no mapa para adicionar demanda. O sistema recalcula os centróides automaticamente.")

    # Processamento
    labels, centers = get_clusters(st.session_state.locations, n_centers)

    # Renderização do Mapa
    m = folium.Map(location=DEFAULT_COORDS, zoom_start=11)

    # 1. Desenhar Pontos de Entrega
    for i, (lat, lon) in enumerate(st.session_state.locations):
        color = '#3388ff'
        if labels is not None:
            group_id = labels[i]
            color = CLUSTER_COLORS[group_id % len(CLUSTER_COLORS)]
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=color, fill=True, fill_color=color, fill_opacity=0.7,
            popup=f"ID: {i+1}"
        ).add_to(m)

    # 2. Desenhar Centróides
    if centers is not None:
        for i, (lat, lon) in enumerate(centers):
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>CD {i+1}</b>",
                icon=folium.Icon(color='black', icon='truck', prefix='fa')
            ).add_to(m)

    # Interação com o Mapa
    # O parametro returned_objects otimiza o re-render evitando reload desnecessário
    map_data = st_folium(m, width="100%", height=600, returned_objects=['last_clicked'])

    # Handler de novos cliques
    if map_data.get('last_clicked'):
        click = map_data['last_clicked']
        
        # Debounce simples: só processa se a coordenada for nova
        if click != st.session_state.last_click:
            st.session_state.locations.append([click['lat'], click['lng']])
            st.session_state.last_click = click
            st.rerun()

if __name__ == "__main__":
    main()