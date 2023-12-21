
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px


# Configuração inicial do Streamlit
st.set_page_config(page_icon=":bar_chart:",
                   layout="wide")

# st.title(":bar_chart: Visualização Geoespacial dos Dados - ENEM")

# Função pra construir o mapa
def build_geographic_visualization(df:pd.DataFrame):
    # Criar o mapa do Brasil usando Folium
    brazil_map = folium.Map(location=[-15.788497, -47.879873], zoom_start=4, control_scale=True)
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
        state_acronym = feature['properties']['sigla']
        
        state_data = brazil_grades[brazil_grades['Estado'] == state_acronym]
        percentage = str(state_data["Porcentagem"].iat[0])
        students = str(state_data["Vestibulandos"].iat[0])
        max_grade = str(state_data["Nota Max"].iat[0])
        min_grade = str(state_data["Nota Min"].iat[0])
        
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
trainees =  pd.read_json(r"streamlit_jsons/trainees_data.json")
grade =  pd.read_json(r"streamlit_jsons/maxGrade_data.json")

# Criando o header do Dashboard
header_box = st.container()
title,filter = header_box.columns((2,1))

with title:
    st.title(":bar_chart: Visualização Geoespacial dos Dados - ENEM")
with filter:
    years = st.selectbox('Selecione um Ano:', geographic_df['Ano'].unique())
st.markdown("---")

geographic_data = geographic_df.query("Ano == @years")

# Criando o container de KPIS 
kpis_box = st.container()
kpi1, kpi2,kpi3, kpi4,kpi5, kpi6 = kpis_box.columns(6)
st.markdown("---")
# Construindo o mapa do Brasil interativo
state = build_geographic_visualization(geographic_data)
treineiros = trainees.query("Estado == @state & Ano == @years")
max_grade = grade.query("Estado == @state & Ano == @years")

# Pegando dados do ano anterior pra comparar os KPIS
past_year = years - 1
past_treineiros = trainees.query("Estado == @state & Ano == @past_year")
past_max_grade = grade.query("Estado == @state & Ano == @past_year")
past_geographic_data = geographic_df.query("Ano == @past_year")

# Criando e organizando as métricas KPI
with kpi1:
    qntVestibulandos = int(geographic_data['Vestibulandos'].sum())
    past_qntVestibulandos = int(past_geographic_data['Vestibulandos'].sum())
    delta = qntVestibulandos - past_qntVestibulandos
    st.metric(label=":book: Vestibulandos:", value=qntVestibulandos, delta=delta,delta_color="normal")
    
with kpi2:
    qntTreineiros = int(treineiros['count'].sum())
    past_qntTreineiros = int(past_treineiros['count'].sum())
    delta = qntTreineiros - past_qntTreineiros
    st.metric(label="Treineiros:", value=qntTreineiros, delta=delta,delta_color="normal")
    
with kpi3:
    try:
        grade = max_grade['Matematica'].iloc[0]
    except:
        grade = 0
    try:
        past_grade = past_max_grade['Matematica'].iloc[0]
    except:
        past_grade = 0
    
    delta = grade - past_grade
    st.metric(label="Max. Matematica:", value=grade, delta=delta,delta_color="normal")
    
with kpi4:
    try:
        grade = max_grade['Linguagens_Codigos'].iloc[0]
    except:
        grade = 0
    try:
        past_grade = past_max_grade['Linguagens_Codigos'].iloc[0]
    except:
        past_grade = 0
    delta = grade - past_grade
    st.metric(label="Max. Linguagens e Codigos:", value=grade, delta=delta,delta_color="normal")
    
with kpi5:
    try:
        grade = max_grade['Ciencias_Humanas'].iloc[0]
    except:
        grade = 0
    try:
        past_grade = past_max_grade['Ciencias_Humanas'].iloc[0]
    except:
        past_grade = 0
    delta = grade - past_grade
    st.metric(label="Max. Ciencias Humanas:", value=grade, delta=delta,delta_color="normal")
    
with kpi6:
    try:
        grade = max_grade['Ciencias_Natureza'].iloc[0]
    except:
        grade = 0
    try:
        past_grade = past_max_grade['Ciencias_Natureza'].iloc[0]
    except:
        past_grade = 0
    delta = grade - past_grade
    st.metric(label="Max. Ciencias da Natureza:", value=grade, delta=delta,delta_color="normal")
    
# Filtrando os dados pros gráficos
lineChart_data = lineChart_df.query("Estado == @state")
errors_data = errors_df.query("Estado == @state")

# Criando as variáveis dos gráficos
line_chart = px.line(lineChart_data,x='Ano',y="Nota Total",color='Tipo_Escola',labels={"Instituição": "Tipo_Escola"},title=f"{state} - Média de Notas por Instituição")
barChart = px.bar(errors_data, x="Ano", y=['Anulada', 'Cópia Texto Motivador', 'Em Branco',
       'Fere Direitos Humanos', 'Fuga ao tema',
       'Não atendimento ao tipo textual', 'Parte desconectada',
       'Texto insuficiente'], title=f"{state} - Erros cometidos na Redação")

# Criando o container dos gráficos
graphs_box = st.container()
graph1, graph2 = graphs_box.columns(2)
with graph1:
    st.plotly_chart(line_chart,use_container_width=True)
with graph2:
    st.plotly_chart(barChart,use_container_width=True)