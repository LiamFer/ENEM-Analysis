
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px


# Configuração inicial do Streamlit
st.set_page_config(page_icon=":bar_chart:",
                   layout="wide")

st.title(":bar_chart: Visualização Geoespacial dos Dados - ENEM")

# Função pra construir o mapa
def build_geographic_visualization(df:pd.DataFrame):
    # Criar o mapa do Brasil usando Folium
    brazil_map = folium.Map(location=[-15.788497, -47.879873], zoom_start=6, control_scale=True)
    brazil_grades = df
    
    # Criando o overlay por cima do brasil
    choropleth = folium.Choropleth(
        geo_data=r"https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        data=brazil_grades,
        columns=("Estado","Porcentagem"),
        key_on="feature.properties.sigla",
        line_opacity=0.8,
        highlight=True)
    
        
    choropleth.geojson.add_to(brazil_map)
    
    for feature in choropleth.geojson.data['features']:
        state_acronynm = feature['properties']['sigla']
        
        percentage = str(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"Porcentagem"])[0])
        students = str(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"Vestibulandos"])[0])
        max_grade = str(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"Nota Max"])[0])
        min_grade = str(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"Nota Min"])[0])
        
        feature['properties']['vestibulandos'] = f'Vestibulandos: {students}'
        feature['properties']['high-performance'] = f'High-Performance: {percentage}%'
        feature['properties']['Nota Máxima'] = f'Nota Máxima: {max_grade}'
        feature['properties']['Nota Mínima'] = f'Nota Mínima: {min_grade}'
        
    # Adicionando o nome dos estados no hover
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['sigla','vestibulandos','high-performance','Nota Máxima','Nota Mínima'],labels=False)
    )
    # Renderizar o mapa no Streamlit dentro de uma coluna

    
    st_map = st_folium(brazil_map, width=700, height=450, use_container_width=True)
    state = ''
    if st_map['last_active_drawing']:
        state = st_map['last_active_drawing']['properties']['sigla']
        return state
    else:
        return ''

# Construindo os dataframes a partir dos JSONS compactados
geographic_df = pd.read_json(r"streamlit_jsons/geographic_data.json")
lineChart_df = pd.read_json(r"streamlit_jsons/institutional_data.json")
errors_df = pd.read_json(r"streamlit_jsons/errors_data.json")


#years = c2.selectbox('Selecione um Ano:', geographic_df.Ano.unique())




# Criando a sidebar
st.sidebar.title("Dashboard Filters")
years = st.sidebar.selectbox('Selecione um Ano:', geographic_df['Ano'].unique())

st.markdown("---")
geographic_data = geographic_df.query("Ano == @years")
# Criando o container de KPIS 
container_1 = st.container()
col1, col2 = container_1.columns(2)

with col1:
    st.subheader(f":book:Vestibulandos: {geographic_data['Vestibulandos'].sum()}")
# with col2:





state = build_geographic_visualization(geographic_data)
lineChart_data = lineChart_df.query("Estado == @state")
errors_data = errors_df.query("Estado == @state")

# Criando as variáveis dos gráficos
line_chart = px.line(lineChart_data,x='Ano',y="Nota Total",color='Tipo_Escola',labels={"Instituição": "Tipo_Escola"},title=f"{state} - Média de Notas por Instituição")
barChart = px.bar(errors_data, x="Ano", y=['Anulada', 'Cópia Texto Motivador', 'Em Branco',
       'Fere Direitos Humanos', 'Fuga ao tema',
       'Não atendimento ao tipo textual', 'Parte desconectada',
       'Texto insuficiente'], title=f"{state} - Erros cometidos na Redação")

# Criando o container dos gráficos
container_2 = st.container()
col3, col4 = container_2.columns(2)
with col3:
    st.plotly_chart(line_chart,use_container_width=True)
with col4:
    st.plotly_chart(barChart,use_container_width=True)