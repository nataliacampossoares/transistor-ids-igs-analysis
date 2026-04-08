import streamlit as st 
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Ciclo")

arquivo = "razao_ids_igs_por_ciclo_-2.5V.csv"

df = pd.read_csv(arquivo)

arquivo_log = "razao_vg_por_log_ids.csv"
df_ida = pd.read_csv(arquivo_log)

st.subheader("VG vs log(IDS)")
df_ciclo0 = df_ida[df_ida["cycle_id"] == 0]
df_ciclo0 = df_ciclo0.sort_values("VG")
fig = px.line(df_ciclo0, x="VG", y="log_IDS", title="VG vs log(IDS)")
st.plotly_chart(fig)

df_on_off = pd.read_csv("razao_on_off.csv")
razao_on_off = df_on_off["Razão on/off"].values[0]
st.metric(label="Razão on/off", value=f"{razao_on_off:.2e}")

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