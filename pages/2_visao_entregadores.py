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

st.set_page_config(page_title='Visao Entregadores', layout='wide')

# -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Funções
# -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def top_delivers(df1, top_asc):
    df2 = ( df1.loc[:, ['Delivery_person_ID','City', 'Time_taken(min)']]
       .groupby(['City','Delivery_person_ID'])
       .mean().sort_values(['City','Time_taken(min)'], ascending=top_asc).reset_index() )
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10) 
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10) 
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10) 
    df3 = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True)
    return df3

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

# - - - - - VISAO ENTREGADORES - - - - - - - - - - - - - - - - - - - -
# ==========================================================================
# Barra Lateral no StreamLit 
# ==========================================================================
st.header('Markdown - Visão Entregadores')

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

# No código acima:
# Ao usar datetime --> TypeError: 'module' object is not callable

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '', ''])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            # A manor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            # A melhor condição de veiculos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor codição', melhor_condicao)

        with col4:
            # A pior condição de veiculos
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior codição', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.title("Avaliações")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacao medias por entregador')
            df_avg_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']]
                                                   .groupby('Delivery_person_ID')
                                                   .mean().reset_index() )
            st.dataframe(df_avg_ratings_per_deliver)
                
        with col2:
            st.markdown('##### Avaliacao medias por transito')
            df_avg_and_std_ratings_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                      .groupby('Road_traffic_density')
                                      .agg({'Delivery_person_Ratings': ['mean','std']}) )
            
            # mudanca de nome das colunas
            df_avg_and_std_ratings_by_traffic.columns = ['delivey_mean','delivey_std']
            
            # reset dos index
            df_avg_and_std_ratings_by_traffic.reset_index()
            st.dataframe(df_avg_and_std_ratings_by_traffic)
            
            st.markdown('##### Avaliacao medias por clima')
            df_avg_and_std_ratings_by_weather_conditions = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                      .groupby('Weatherconditions')
                                      .agg({'Delivery_person_Ratings': ['mean','std']}) )
            
            # mudanca de nome das colunas
            df_avg_and_std_ratings_by_weather_conditions.columns = ['condition_mean','condition_std']
            
            # reset dos index
            df_avg_and_std_ratings_by_weather_conditions.reset_index()
            
            #Exibicao dos dados
            st.dataframe(df_avg_and_std_ratings_by_weather_conditions)
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Top entregador mais rapidos")
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown("Top entregador mais lentos")
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
            
                
                