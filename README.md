# Otimização de Malha Logística com K-Means

Aplicação web em Streamlit para planejamento de rotas de entrega: o usuário marca pontos de demanda em um mapa interativo e o sistema agrupa automaticamente esses pontos em clusters usando K-Means, sugerindo a localização ideal de cada Centro de Distribuição (CD).

## Funcionalidades

- Adição de pontos de entrega com clique direto no mapa (Folium)
- Clusterização automática via K-Means (`scikit-learn`), com número de centros ajustável (1 a 5)
- Ajuste dos centróides para a via mais próxima (snap-to-road) usando a API pública do [OSRM](https://project-osrm.org/), evitando que um centro caia em água ou área sem acesso
- Reset dos dados a qualquer momento pela barra lateral

Mais detalhes sobre a modelagem podem ser encontrados em [Relatorio_Otimizacao_Entregas_Kmeans.pdf](Relatorio_Otimizacao_Entregas_Kmeans.pdf).

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```
