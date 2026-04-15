import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Ciclo")

arquivo_upload = st.file_uploader("Suba o arquivo de dados", type=["txt"])

if arquivo_upload is not None:
    with open("dados_transistor com leakage.txt", "wb") as f:
        f.write(arquivo_upload.getbuffer())
    subprocess.run(["python3", "calcular_IDSIGS.py"])
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
    ciclo = st.multiselect(
        "Escolha um ciclo", 
        df_ida_log["cycle_id"].unique(), 
        default=[0])
    fig = go.Figure()

    cores = ["blue", "red", "green", "orange", "purple", "pink", "brown", "gray", "cyan"]  # lista de cores para diferenciar os ciclos
    razoes = []
    for i, c in enumerate(ciclo):
        cor = cores[i % len(cores)]
        if mostrar_ida:
            df_ciclo_ida = df_ida_log[df_ida_log["cycle_id"] == c].sort_values("VG")
            fig.add_trace(go.Scatter(x=df_ciclo_ida["VG"], y=df_ciclo_ida["log_IDS"], name=f"Ciclo {c} - ida", line=dict(color=cor, dash="solid")))
            razao_on_off_ida = df[(df["Ciclo"] == c) & (df["direction"] == "ida")]["Razão on/off"].values
            if len(razao_on_off_ida) > 0:
                razoes.append({"label": f"Razão on/off - Ida (Ciclo {c})", "valor": razao_on_off_ida[0]})
        if mostrar_volta:
            df_ciclo_volta = df_volta_log[df_volta_log["cycle_id"] == c].sort_values("VG")
            fig.add_trace(go.Scatter(x=df_ciclo_volta["VG"], y=df_ciclo_volta["log_IDS"], name=f"Ciclo {c} - volta", line=dict(color=cor, dash="dash")))
            razao_on_off_volta = df[(df["Ciclo"] == c) & (df["direction"] == "volta")]["Razão on/off"].values
            if len(razao_on_off_volta) > 0:
                razoes.append({"label": f"Razão on/off - Volta (Ciclo {c})", "valor": razao_on_off_volta[0]})
                            
    # --- razao on/off ---
    fig.update_layout(title="VG vs log(IDS)", xaxis_title="VG", yaxis_title="log(IDS)")
    st.plotly_chart(fig)
    for r in razoes:
        st.metric(label=r["label"], value=f"{r['valor']:.2e}")

else:
    st.warning("Por favor, suba um arquivo .txt para continuar")
    st.stop()

