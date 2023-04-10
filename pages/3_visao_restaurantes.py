#Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import datetime

st.set_page_config(page_title='Visao Restaurantes', layout='wide')

# -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Funções
# -- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def avg_std_time_on_traffic(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = (df1.loc[:, cols]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', 
          color='std_time', color_continuous_scale='RdBu', 
          color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df1):
    cols = ['Time_taken(min)', 'City']
    df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta funcao calucla o tempo medio e o desvio padrao do tempo de entrega.
        Parametros:
            Input: 
                - df: Dataframe com os dados necessarios para o calculo
                - op: Tipo de operacao que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão médio
            Output: 
                - df: Dataframe com 2 colunas e 1 linha

    """
    cols = ['Time_taken(min)', 'Festival']
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
              .groupby(['Festival'])
              .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2) 
    return df_aux

def distance(df1, fig):    
        if fig == False:
            cols = ['Delivery_location_longitude','Delivery_location_latitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = ( df1.loc[:, cols].apply(lambda x: haversine(
                (x['Restaurant_latitude'],x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) )

            avg_distance = np.round(df1['distance'].mean(),2)
            return avg_distance
        else:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

            df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine(
    (x['Restaurant_latitude'],x['Restaurant_longitude']),
    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
            avg_distance = df1.loc[:, ['City','distance']].groupby('City').mean().reset_index()

            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0] )] )
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

# - - - - - VISAO RESTAURANTES - - - - - - - - - - - - - - - - - - - -
#1. Quantidade de pedidos por dia.
df_aux = df1.loc[:,['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
df_aux.head()

# Desenhar o grafico de linhas
px.bar(df_aux, x='Order_Date', y='ID')

# ==========================================================================
# Barra Lateral no StreamLit 
# ==========================================================================
st.header('Markdown - Visão Restaurantes')

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

#st.dataframe(df1)

# ==========================================================================
# Layout no StreamLit
# ==========================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '', ''])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)
            
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('Distância média', avg_distance)
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')  
            col3.metric('Tempo médio', df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')  
            col4.metric('STD Entrega', df_aux)
           
        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')  
            col5.metric('Tempo médio', df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')  
            col6.metric('STD Entrega', df_aux)
            
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)
            
        with col2:
            cols = ['Time_taken(min)', 'City', 'Type_of_order']
            df_aux = ( df1.loc[:, cols]
                      .groupby(['City', 'Type_of_order'])
                      .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
    
    with st.container():
        st.markdown( """---""")
        st.title("Distribuição do Tempo")
        col1, col2 = st.columns(2)
        with col1:
            #st.markdown('##### Coluna 1')
#             cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

#             df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine(
#     (x['Restaurant_latitude'],x['Restaurant_longitude']),
#     (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
#             avg_distance = df1.loc[:, ['City','distance']].groupby('City').mean().reset_index()

#             fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0] )] )
            fig = distance(df1, fig=True)
            st.plotly_chart(fig)
    
        with col2:
            #st.markdown('##### Coluna 2')                
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)
        