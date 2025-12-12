import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans

# Configurações globais
PAGE_TITLE = "Planejador Logistico"
DEFAULT_COORDS = [-22.86, -43.23] #Isso aqui é fundão
CLUSTER_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']

def init_state():
    """Inicializa variáveis de sessão se não existirem."""
    if 'locations' not in st.session_state:
        st.session_state.locations = []
    if 'last_click' not in st.session_state:
        st.session_state.last_click = None

def get_clusters(locations, k):
    """Calcula K-Means apenas se houver dados suficientes."""
    if len(locations) <= k:
        return None, None
    
    df = pd.DataFrame(locations, columns=['lat', 'lon'])
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    model.fit(df)
    return model.labels_, model.cluster_centers_

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