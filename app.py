
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ENEM Analysis",
                   page_icon=":bar_chart:",
                   layout="wide")

df = pd.read_csv(r"https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/06_Stats/US_Baby_Names/US_Baby_Names_right.csv")

st.dataframe(df)

