# %%
import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import folium
import zipfile
from streamlit_folium import st_folium
import os

st.set_page_config(page_icon=":bar_chart:",
                   layout="wide")

# %%
# Configurações do Pandas
pd.options.display.max_columns = 26

# %%
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
    

# %%
enem = build_dataframe()


# %%
# Calculando a Nota Total de cada pessoa
enem['Nota Total'] = enem[['Ciencias_Natureza','Ciencias_Humanas','Matematica','Linguagens_Codigos','Redacao']].sum(axis=1)/5

# %%

# %%
def main(df):
    # Configuração inicial do Streamlit
    st.title("Visualização Geoespacial - ENEM")

    # Criar o mapa do Brasil usando Folium
    brazil_map = folium.Map(location=[-15.788497, -47.879873], zoom_start=6, control_scale=True)

    # Lendo os limites do brasil usando um geoJson do mapa do brasil
    # folium.GeoJson(
    #     "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
    #     name="geojson",
    # ).add_to(brazil_map)
    
    # Criando o overlay por cima do brasil
    choropleth = folium.Choropleth(
        geo_data=r"https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        data=df,
        columns=("Estado","Nota Total"),
        key_on="features.properties.sigla")
    choropleth.geojson.add_to(brazil_map)
    # Renderizar o mapa no Streamlit
    st_map = st_folium(brazil_map,width=700,height=450)

main(enem)

