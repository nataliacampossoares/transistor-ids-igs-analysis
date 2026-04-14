import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Ciclo")

# --- leitura dos arquivos ---
df = pd.read_csv("razao_ids_igs_por_ciclo_-2.5V.csv")
df_ida_log = pd.read_csv("razao_vg_por_log_ids_ida.csv")
df_volta_log = pd.read_csv("razao_vg_por_log_ids_volta.csv")

# --- filtro de direcao ---
mostrar_ida = st.checkbox("Ida", value=True)
mostrar_volta = st.checkbox("Volta", value=True)

direcoes = []
if mostrar_ida:
    direcoes.append("ida")
if mostrar_volta:
    direcoes.append("volta")

df = df[df["direction"].isin(direcoes)]


# --- tabela de resultados ---
st.subheader("Resultados")
st.dataframe(df)

# --- grafico ids/igs por ciclo ---
st.subheader("IDSIGS vs Ciclo")
st.line_chart(df.set_index("Ciclo")["Razão IDS/IGS"]) # coloca o ciclo no eixo x e a razão IDS/IGS no eixo y

# --- filtro de ciclos ---
st.subheader("Filtrar ciclos")
ciclos = st.multiselect(
    "Escolha os ciclos",
    df["Ciclo"],
    default=df["Ciclo"]
)
df_filtrado = df[df["Ciclo"].isin(ciclos)]
# tentei usar o pandas para plotar esse grafico, mas os pontos nao estavam ordenados e nao havia controle sobre os eixos
st.line_chart(df_filtrado.set_index("Ciclo")["Razão IDS/IGS"])

# --- gráfico vg vs log(ids) por ciclo ---
st.subheader("VG vs log(IDS)")
ciclo = st.selectbox("Escolha um ciclo", df_ida_log["cycle_id"].unique())
fig = go.Figure()
if mostrar_ida:
    df_ciclo_ida = df_ida_log[df_ida_log["cycle_id"] == ciclo].sort_values("VG")
    fig.add_trace(go.Scatter(x=df_ciclo_ida["VG"], y=df_ciclo_ida["log_IDS"], name="ida", line=dict(color="blue")))
if mostrar_volta:
    df_ciclo_volta = df_volta_log[df_volta_log["cycle_id"] == ciclo].sort_values("VG")
    fig.add_trace(go.Scatter(x=df_ciclo_volta["VG"], y=df_ciclo_volta["log_IDS"], name="volta", line=dict(color="red")))

# --- razao on/off ---
fig.update_layout(title="VG vs log(IDS)", xaxis_title="VG", yaxis_title="log(IDS)")
st.plotly_chart(fig)
if mostrar_ida:
    razao_on_off_ida = df[(df["Ciclo"] == ciclo) & (df["direction"] == "ida")]["Razão on/off"].values
    if len(razao_on_off_ida) > 0:
        st.metric(label=f"Razão on/off - Ida (Ciclo {ciclo})", value=f"{razao_on_off_ida[0]:.2e}")

if mostrar_volta:
    razao_on_off_volta = df[(df["Ciclo"] == ciclo) & (df["direction"] == "volta")]["Razão on/off"].values
    if len(razao_on_off_volta) > 0:
        st.metric(label=f"Razão on/off - Volta (Ciclo {ciclo})", value=f"{razao_on_off_volta[0]:.2e}")

