import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Transistor")

arquivo_upload = st.file_uploader("Suba o arquivo de dados", type=["xlsx"])

if arquivo_upload is not None:
    
    # --- salva o arquivo enviado pelo usuario ---
    with open("data/dados_transistores_raw.xlsx", "wb") as f:
        f.write(arquivo_upload.getbuffer())
    subprocess.run(["python3", "calcular_transistores.py"])
    
    # --- leitura dos arquivos ---
    df = pd.read_csv("outputs/razao_ids_igs_por_transistor_4V.csv")
    df_log = pd.read_csv("outputs/dados_transistores.csv")
    
    # --- tabela de resultados ---
    st.subheader("Resultados")
    st.dataframe(df)
    
     # --- filtro de transistores ---
    st.subheader("Filtrar transistores")
    transistores = st.multiselect(
        "Escolha os transistores",
        df["Transistor"],
        default=df["Transistor"]
    )
    df_filtrado = df[df["Transistor"].isin(transistores)]
    # tentei usar o pandas para plotar esse grafico, mas os pontos nao estavam ordenados e nao havia controle sobre os eixos
    st.line_chart(df_filtrado.set_index("Transistor")["Razão IDS/IGS"])
    
    
    # --- gráfico vg vs log(ids) por ciclo ---
    st.subheader("VG vs log(IDS)")
    transistor = st.multiselect(
        "Escolha um transistor", 
        df["Transistor"].unique(), # lista todos os ciclos sem repetir
        default=[1])
    fig = go.Figure() # cria uma figura vazia no plotly, q vai ser preenchida com as linhas de cada ciclo do loop


    cores = ["blue", "red", "green", "orange", "purple", "pink", "brown", "gray", "cyan"]  # lista de cores para diferenciar os ciclos
    razoes = []
    for i, t in enumerate(transistor): # passa por cada ciclo que o usuario escolheu. i é pra cor e c é pro ciclo
        cor = cores[i % len(cores)]
        df_transistor = df_log[df_log["transistor"] == t].sort_values("VG")
        fig.add_trace(go.Scatter(x=df_transistor["VG"], y=df_transistor["IDS"], name=f"Transistor {t}", line=dict(color=cor, dash="solid")))
        razao_on_off = df[(df["Transistor"] == t)]["Razão on/off"].values
        if len(razao_on_off) > 0:
                razoes.append({"Transistor": t, "Valor": razao_on_off[0], "Valor Máximo IDS": df[(df["Transistor"] == t)]["Valor Máximo IDS"].values[0], "Valor Mínimo IDS": df[(df["Transistor"] == t) & (df["Transistor"] == t)]["Valor Mínimo IDS"].values[0]})
               
        
    fig.update_layout(title="VG vs log(IDS)", xaxis_title="VG", yaxis_title="IDS",
    yaxis=dict(type="log", exponentformat="power", dtick=1))
    st.plotly_chart(fig)
    
    # --- tabela de resultados on/off ---
    st.subheader("Razão on/off por transistor")
    df_on_off = pd.DataFrame(razoes) # transoforma a lista de dicionarios em tabela
    st.dataframe(df_on_off) 
    media = df_on_off["Valor"].mean()
    st.markdown(f"#### Média da Razão on/off: {media:.2e}")
else:
    st.warning("Por favor, suba um arquivo .xlsx para continuar")
    st.stop()
        
    