
import streamlit as st
import pandas as pd
import folium
import zipfile
from streamlit_folium import st_folium
import os

st.set_page_config(page_icon=":bar_chart:",
                   layout="wide")


pd.options.display.max_columns = 26


def build_dataframe():
    # Arrays e dicionários úteis
    columns = ["NU_ANO","TP_NACIONALIDADE","TP_SEXO","TP_FAIXA_ETARIA","TP_COR_RACA","TP_ESTADO_CIVIL",
            "TP_ST_CONCLUSAO","TP_ESCOLA","IN_TREINEIRO","NO_MUNICIPIO_ESC","SG_UF_PROVA","TP_PRESENCA_CN",
            "TP_PRESENCA_CH","TP_PRESENCA_LC","TP_PRESENCA_MT","NU_NOTA_CN","NU_NOTA_CH","NU_NOTA_LC",
            "NU_NOTA_MT","TP_STATUS_REDACAO","NU_NOTA_COMP1","NU_NOTA_COMP2","NU_NOTA_COMP3","NU_NOTA_COMP4",
            "NU_NOTA_COMP5","NU_NOTA_REDACAO"]

    renamed_columns = ["Ano","Nacionalidade","Sexo","Idade","Cor","Estado_civil","Situacao_EM","Tipo_Escola",
                    "Treineiro","Municipio","Estado","Presenca_CN","Presenca_CH","Presenca_LC","Presenca_MT",
                    "Ciencias_Natureza","Ciencias_Humanas","Linguagens_Codigos","Matematica","Status_Redacao",
                    "Ortografia","Desenvolvimento","Informacoes","Organizacao","Proposta","Redacao"]
    
    zip_data = {
    "Zip Files":[],
    "Folder Data":  os.listdir("information")
    }

    for zippedArch in zip_data["Folder Data"]:
        with zipfile.ZipFile(f"information\{zippedArch}") as zippedData:
            for file in zippedData.namelist():
                if "microdados" in file.lower() and file.endswith(".csv"):
                    zip_data["Zip Files"].append(file)
                    
    # Lambda pra ordenar os arquivos do mais antigo para o mais novo 2015 - 2022
    zip_data["Zip Files"].sort(key = lambda x: x[22:-4])
    zip_data["Folder Data"].sort(key = lambda x: x[16:-4])
    
    # Pegando os ultimos 3 anos
    zip_data["Folder Data"] = zip_data["Folder Data"][-1:]
    zip_data["Zip Files"] = zip_data["Zip Files"][-1:]

    # Criando o megadataframe filtrado
    enem_collection = []
    for i in range(len(zip_data["Zip Files"])):
        with zipfile.ZipFile(f"information\{zip_data['Folder Data'][i]}") as microdata:
            with microdata.open(zip_data["Zip Files"][i]) as csv:
                
                data = pd.read_csv(csv,encoding="ISO-8859-1",sep=";",usecols=columns)
                # Renomeando as colunas
                data.columns = renamed_columns
                # Removendo as linhas onde não temos notas
                data.dropna(subset=["Ciencias_Natureza",'Ciencias_Humanas',"Ciencias_Humanas","Matematica","Redacao"],inplace=True)
                data.reset_index(inplace=True,drop=True)
                # Adicionando no array pra criar o Dataframe completo posteriormente
                enem_collection.append(data)
                
    return pd.concat(enem_collection)
    

# Construindo o dataframe
enem = build_dataframe()
# Calculando a Nota Total de cada pessoa
enem['Nota Total'] = enem[['Ciencias_Natureza','Ciencias_Humanas','Matematica','Linguagens_Codigos','Redacao']].sum(axis=1)/5

# Criando os filtros
st.sidebar.header("Dashboard Filters")


choice = st.sidebar.text_input("Search:", key="choice")

gender = st.sidebar.multiselect(
    "Filtre por gênero:",
    options=enem.Sexo.unique(),
    default=enem.Sexo.unique()
)

df_selection = enem.query("Sexo == @gender")

st.dataframe(df_selection.head(20))


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


def main(df:pd.DataFrame):
    # Configuração inicial do Streamlit
    st.title("Visualização Geoespacial - ENEM")

    # Criar o mapa do Brasil usando Folium
    brazil_map = folium.Map(location=[-15.788497, -47.879873], zoom_start=6, control_scale=True)
    
    # Pegando o Dataframe da qualidade por estado
    brazil_grades = get_states_quality(enem)
    
    # Criando o overlay por cima do brasil
    choropleth = folium.Choropleth(
        geo_data=r"https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        data=brazil_grades,
        columns=("Estado","Great"),
        key_on="feature.properties.sigla",
        line_opacity=0.8,
        highlight=True)
    
        
    choropleth.geojson.add_to(brazil_map)
    
    for feature in choropleth.geojson.data['features']:
        state_acronynm = feature['properties']['sigla']
        
        percentage = str(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"Great"])[0])
        students = str(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"count"])[0])
        great_students = str(int(list(brazil_grades.loc[brazil_grades['Estado'] == state_acronynm,"great_students"])[0]))
        
        feature['properties']['porcentagem'] = f'porcentagem: {percentage}%'
        feature['properties']['vestibulandos'] = f'vestibulandos: {students}'
        feature['properties']['high-performance'] = f'high-performance: {great_students}'
        
    # Adicionando o nome dos estados no hover
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['sigla','porcentagem','vestibulandos','high-performance'],labels=False)
    )
    # Renderizar o mapa no Streamlit
    st_map = st_folium(brazil_map,width=700,height=450)


main(df_selection)


