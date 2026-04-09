import streamlit as st 
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Ciclo")

arquivo = "razao_ids_igs_por_ciclo_-2.5V.csv"

df = pd.read_csv(arquivo)

arquivo_log = "razao_vg_por_log_ids.csv"
df_ida = pd.read_csv(arquivo_log)


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
st.subheader("VG vs log(IDS)")
ciclo = st.selectbox("Escolha um ciclo para análise detalhada", df_ida["cycle_id"].unique())
df_ciclo = df_ida[df_ida["cycle_id"] == ciclo]
df_ciclo = df_ciclo.sort_values("VG")
fig = px.line(df_ciclo, x="VG", y="log_IDS", title="VG vs log(IDS)")
st.plotly_chart(fig)

razao_on_off = df[df["Ciclo"] == ciclo]["Razão on/off"].values[0]
st.metric(label="Razão on/off", value=f"{razao_on_off:.2e}")


