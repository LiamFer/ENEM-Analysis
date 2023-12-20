
import streamlit as st
import pandas as pd
import folium
import zipfile
from streamlit_folium import st_folium
import plotly.express as px
import os

st.set_page_config(page_icon=":bar_chart:",
                   layout="wide")


pd.options.display.max_columns = 26

# Construindo o dataframe geoespacial
geographic_df = pd.read_json(r"streamlit_jsons\geographic_data.json")



# Criando os filtros
st.sidebar.header("Dashboard Filters")

choice = st.sidebar.text_input("Search:", key="choice")

years = st.sidebar.selectbox('Selecione uma opção:', geographic_df.Ano.unique())


#chart_data = pd.DataFrame(enem.loc[enem.Municipio == choice].groupby(["Ano",'Tipo_Escola'])["Nota Total"].mean()).reset_index()
#chart_data['Tipo_Escola'] = chart_data['Tipo_Escola'].map(tipo_instituicao)
#chart_data['Ano'] = chart_data['Ano'].astype(str)

#line_chart = px.line(chart_data,x='Ano',y="Nota Total",color='Tipo_Escola')
#st.plotly_chart(line_chart)

geographic_data = geographic_df.query("Ano == @years")

st.dataframe(geographic_data)


def get_states_quality(df:pd.DataFrame):
    cloned = df.copy()
    
    # Filtrando os alunos por nota 800+ com uma coluna auxiliar
    cloned['Great_student'] = cloned['Nota Total'].apply(lambda x: "Great" if x >= 800 else "Bad")
    
    # Conseguindo os valores como porcentagem e dropando a coluna auxiliar
    brazil_grades = pd.DataFrame(cloned.groupby('Estado')['Great_student'].value_counts(normalize=True)).reset_index()
    
    # Pivotando a tabela e organizando os dados obtidos
    brazil_grades = brazil_grades.pivot_table('proportion', ['Estado'], 'Great_student').reset_index()
    brazil_grades = brazil_grades[['Estado',"Great"]]
    
    # Clenando os NaN
    brazil_grades.fillna(value=0,inplace=True)
    
    # Pegando o número de estudantes de cada estado
    state_students = pd.DataFrame(df.groupby('Estado')['Estado'].value_counts()).reset_index()

    # Juntando as duas Informações
    brazil_grades = pd.merge(state_students,brazil_grades,on="Estado")
    
    # Calculando quantos estudantes tem a nota boa(>=800) usando a porcentagem
    brazil_grades["great_students"] = brazil_grades['count'] * brazil_grades['Great']
    
    return brazil_grades


def build_geographic_visualization(df:pd.DataFrame):
    # Configuração inicial do Streamlit
    st.title("Visualização Geoespacial - ENEM")

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
    # Renderizar o mapa no Streamlit
    st_map = st_folium(brazil_map,width=700,height=450)


build_geographic_visualization(geographic_data)


