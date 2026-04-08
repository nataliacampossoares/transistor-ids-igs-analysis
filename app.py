import streamlit as st 
import pandas as pd

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Ciclo")

arquivo = "razao_ids_igs_por_ciclo_-2.5V.csv"

df = pd.read_csv(arquivo)

st.subheader("Resultados")
st.dataframe(df)


st.subheader("IDSIGS vs Ciclo")
st.line_chart(df.set_index("Ciclo")["Razão IDS/IGS"]) # coloca o ciclo no eixo x e a razão IDS/IGS no eixo y

# filtro
st.subheader("Filtrar ciclos")

ciclos = st.multiselect(
    "Escolha os ciclos",
    df["Ciclo"],
    default=df["Ciclo"]
)

df_filtrado = df[df["Ciclo"].isin(ciclos)]

st.line_chart(df_filtrado.set_index("Ciclo")["Razão IDS/IGS"])