import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Ciclo")



arquivo_upload = st.file_uploader("Suba o arquivo de dados", type=["txt"])

if arquivo_upload is not None:
    # --- salva o arquivo enviado pelo usuario ---
    with open("dados_transistor com leakage.txt", "wb") as f:
        f.write(arquivo_upload.getbuffer())
    subprocess.run(["python3", "calcular_IDSIGS.py"])
    
    # --- leitura dos arquivos ---
    
    # pontos calculados por ciclo só no VG = -2.5V
    df = pd.read_csv("razao_ids_igs_por_ciclo_-2.5V.csv")
    # pontos da varredura de VG na ida, com a coluna de log(IDS)
    df_ida_log = pd.read_csv("razao_vg_por_log_ids_ida.csv")
    # pontos da varredura de VG na volta, com a coluna de log(IDS)
    df_volta_log = pd.read_csv("razao_vg_por_log_ids_volta.csv")
    
    # --- filtro de direcao ---
    mostrar_ida = st.checkbox("Ida", value=True)
    mostrar_volta = st.checkbox("Volta", value=True)

    direcoes = []
    if mostrar_ida:
        direcoes.append("ida")
    if mostrar_volta:
        direcoes.append("volta")

    # df["direction"] pega a coluna direction no dataframe
    # .isin(direcoes) verifica linha por linha se o valor da coluna direction esta dentro da lista de direcoes, retorna bool
    # df[...] filtra o dataframe, mantendo so as true
    df = df[df["direction"].isin(direcoes)]

    # --- tabela de resultados ---
    st.subheader("Resultados")
    st.dataframe(df)

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
        df_ida_log["cycle_id"].unique(), # lista todos os ciclos sem repetir
        default=[0])
    fig = go.Figure() # cria uma figura vazia no plotly, q vai ser preenchida com as linhas de cada ciclo do loop

    cores = ["blue", "red", "green", "orange", "purple", "pink", "brown", "gray", "cyan"]  # lista de cores para diferenciar os ciclos
    razoes = []
    for i, c in enumerate(ciclo): # passa por cada ciclo que o usuario escolheu. i é pra cor e c é pro ciclo
        cor = cores[i % len(cores)] 
        if mostrar_ida:
            df_ciclo_ida = df_ida_log[df_ida_log["cycle_id"] == c].sort_values("VG") 
            # [df_ida_log["cycle_id"] isso retorna true/false
            # o df_ida_log de fora filtra somente os true
            #sort_values("VG") só ordena os pontos do ciclo do vg menor até o maior
            fig.add_trace(go.Scatter(x=df_ciclo_ida["VG"], y=df_ciclo_ida["IDS"], name=f"Ciclo {c} - ida", line=dict(color=cor, dash="solid")))
            # adiciona a linha no grafico; esse go.scatter define o tipo do grafico (nesse caso é o de linha)
            razao_on_off_ida = df[(df["Ciclo"] == c) & (df["direction"] == "ida")]["Razão on/off"].values
            # filtra o ciclo e a direcao, pega a coluna on/off e converte para uma lista de python, um array
            if len(razao_on_off_ida) > 0:
                razoes.append({"Ciclo": c, "Direção": "Ida", "Valor": razao_on_off_ida[0], "Valor Máximo IDS": df[(df["Ciclo"] == c) & (df["direction"] == "ida")]["Valor Máximo IDS"].values[0], "Valor Mínimo IDS": df[(df["Ciclo"] == c) & (df["Ciclo"] == c) & (df["direction"] == "ida")]["Valor Mínimo IDS"].values[0]})
                # adiciona um dicionario na lista de razoes
        if mostrar_volta:
            df_ciclo_volta = df_volta_log[df_volta_log["cycle_id"] == c].sort_values("VG")
            fig.add_trace(go.Scatter(x=df_ciclo_volta["VG"], y=df_ciclo_volta["IDS"], name=f"Ciclo {c} - volta", line=dict(color=cor, dash="dash")))
            razao_on_off_volta = df[(df["Ciclo"] == c) & (df["direction"] == "volta")]["Razão on/off"].values
            if len(razao_on_off_volta) > 0:
                razoes.append({"Ciclo": c, "Direção": "Volta", "Valor": razao_on_off_volta[0], "Valor Máximo IDS": df[(df["Ciclo"] == c) & (df["direction"] == "volta")]["Valor Máximo IDS"].values[0], "Valor Mínimo IDS": df[(df["Ciclo"] == c) & (df["direction"] == "volta")]["Valor Mínimo IDS"].values[0]})
                
    # --- razao on/off ---
    fig.update_layout(
        title="VG vs log(IDS)", 
        xaxis_title="VG", # nome eixo x
        yaxis_title="log(IDS)", # nome eixo y
        yaxis=dict(
            type="log", # coloca o eixo x em escala logartimica
            exponentformat="power", # mostra os valores em potencia de 10
            dtick=1 # isso é pra mostrar uma so marcacao para cada potencia de 10
    )   )
    st.plotly_chart(fig)
    
    # --- tabela de resultados on/off ---
    st.subheader("Razão on/off por ciclo")
    df_on_off = pd.DataFrame(razoes) # transoforma a lista de dicionarios em tabela
    st.dataframe(df_on_off) 
    media = df_on_off["Valor"].mean()
    st.markdown(f"#### Média da Razão on/off: {media:.2e}")
else:
    st.warning("Por favor, suba um arquivo .txt para continuar")
    st.stop()