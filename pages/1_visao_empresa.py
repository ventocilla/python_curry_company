#Libraries
from haversine import haversine
import plotly.express as px
#import ploty.graph_objects as go

import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import datetime


st.set_page_config(page_title='Visao Empresa', layout='wide')

# -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Funções
# -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def country_maps(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = (df1.loc[:, cols]
              .groupby(['City', 'Road_traffic_density'])
              .median()
              .reset_index())
    df_aux = df_aux[df_aux['City'] != 'NaN']
    df_aux = df_aux[df_aux['Road_traffic_density'] != 'NaN']

    # Desenhar o mapa
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

    folium_static(map, width=1024, height=600)

def order_share_by_week(df1):
    df_aux01 = df1.loc[:, ['ID', 'Week_Of_Year']].groupby('Week_Of_Year').count().reset_index()
    df_aux02 = df1.loc[:,['Delivery_person_ID', 'Week_Of_Year']].groupby('Week_Of_Year').nunique().reset_index()
    #df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_Of_Year', y='order_by_deliver')
    return fig
        
def order_by_week(df1):
    df1['Week_Of_Year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID','Week_Of_Year']].groupby('Week_Of_Year').count().reset_index()
    fig = px.line(df_aux, x='Week_Of_Year', y='ID')
    return fig

def traffic_order_city(df1):
    colsLoc = ['ID', 'City', 'Road_traffic_density']
    colGroupBy = ['City', 'Road_traffic_density']
    df_aux = df1.loc[:, colsLoc].groupby(colGroupBy).count().reset_index()
    fig = px.scatter(df_aux, x= 'City', y='Road_traffic_density', size='ID', color='City')
    return fig

def traffic_order_share(df1):
    cols = ['ID', 'Road_traffic_density']
    df_aux = (df1.loc[:, cols]
              .groupby('Road_traffic_density')
              .count()
              .reset_index())
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values = 'entregas_perc', names='Road_traffic_density')
    return fig

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    # seleção de linhas
    df_aux = df1.loc[:,cols].groupby('Order_Date').count().reset_index()

    # desenhar o gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig

def clean_code(df1):
    """ Esta funcao tem a responsabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Retirada dos espacos das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( retirada do texto da variável numerica )
        
        Input: Dataframe
        Output: Dataframe
    
    """
    # 1. Fazer antes a retirada de NaN na coluna Age
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 2. Mudanca de tipo:
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 3. Convertendo multiple-delivery de texto para numeros inteiro (int)
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 4. Retirada os espaços dentro de strings/texto/object
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # 5. Limpando a coluna de Time_taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# -- - - - - - - - - - - - - - - - - - - - - Inicio da Estrutura lógica do código  - - - - - - - - - - 
# - - - - - - - - 
# Import dataset
# - - - - - - - - 
df = pd.read_csv('dataset/train.csv')

# - - - - - - - - 
# Limpando os dados
# - - - - - - - - 
df1 = clean_code(df)

# - - - - - VISAO EMPRESA - - - - - - - - - - - - - - - - - - - -
# ==========================================================================
# Barra Lateral no StreamLit 
# ==========================================================================
st.header('Markdown - Visão Cliente')

image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('### Cury Company ###')
st.sidebar.markdown('## Fastest Delivery in Town ##')
st.sidebar.markdown("""---""")
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022,4,13),
    #value=datetime(2022,4,13),
    min_value=pd.datetime(2022,2,11),
    #min_value=datetime(2022,2,11),
    max_value=pd.datetime(2022,4,6),
    #max_value=datetime(2022,4,6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    "Quais as condições do transito",
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Power by CDS ###")

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==========================================================================
# Layout no StreamLit 
# ==========================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    # Area com 1 columas - Graf1.
    with st.container():
        # Order Metric
        fig = order_metric(df1)
        st.markdown('Orders by Day')
        st.plotly_chart(fig, use_container_width = True)
            
    # Area com 2 columas - Graf2 e Graf3.
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.markdown('Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.markdown('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width = True)
                
with tab2:
    with st.container():
        st.markdown('Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        st.markdown('Order share by week')  
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.markdown('Country Maps')
    country_maps(df1)

# ==========================================================================

