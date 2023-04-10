import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=""
)

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('### Cury Company ###')
st.sidebar.markdown('## Fastest Delivery in Town ##')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """ 
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos Entregadores e Resturantes
    ### Como utilizar este Growth Dashboard ?
    - Visão Empresa:
        -  Visão Gerencial: Métricas gerais de acompanhamento
        -  Visão Tática: Indicadores semanais de crescimento
        -  Visão Geográfica: Insights de geolocalização
    - Visão Entregador:
        -  Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
    - Time de Data Science no Discord
        - @Leo_Vento
    """
)