import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import numpy as np

st.set_page_config(layout="wide") 

st.title("Análise de IDSIGS por Transistor")

arquivo_upload = st.file_uploader("Suba o arquivo de dados", type=["xlsx", "xls"])

if arquivo_upload is not None:
    
    # --- salva o arquivo ---
    with open("data/dados_brutos.xls", "wb") as f:
        f.write(arquivo_upload.getbuffer())
    subprocess.run(["python3", "calcular_transistores.py"])
    
    # --- leitura dos arquivos ---
    df = pd.read_csv("outputs/razao_transistores.csv")
    df_log = pd.read_csv("outputs/dados_transistores.csv")
    
    # --- tabela de resultados ---
    st.subheader("Resultados")
    st.dataframe(df)    
    
    # --- gráfico vg vs log(ids) por ciclo ---
    st.subheader("VG vs log(IDS)")
    transistor = st.multiselect(
        "Escolha um transistor", 
        df["Transistor"].unique(),
        default=[1])
    fig = go.Figure() 

    cores = ["blue", "red", "green", "orange", "purple", "pink", "brown", "gray", "cyan"]  
    razoes = []
    for i, t in enumerate(transistor): 
        cor = cores[i % len(cores)]
        df_transistor = df_log[df_log["transistor"] == t]
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
    
     # --- gráfico vg vs log(igs) por ciclo ---
    st.subheader("VG vs log(IGS)")
    transistor2 = st.multiselect(
    "Escolha um transistor", 
    df["Transistor"].unique(),
    default=[1],
    key="transistor_igs")
    fig2 = go.Figure() 

    cores = ["blue", "red", "green", "orange", "purple", "pink", "brown", "gray", "cyan"]  
    razoes = []
    for i, t in enumerate(transistor2): 
        cor = cores[i % len(cores)]
        df_transistor = df_log[df_log["transistor"] == t]
        fig2.add_trace(go.Scatter(x=df_transistor["VG"], y=df_transistor["IGS"], name=f"Transistor {t}", line=dict(color=cor, dash="solid")))
        # razao_on_off = df[(df["Transistor"] == t)]["Razão on/off"].values
        if len(razao_on_off) > 0:
                razoes.append({"Transistor": t, "Valor": razao_on_off[0]})
               
        
    fig2.update_layout(title="VG vs log(IGS)", xaxis_title="VG", yaxis_title="IGS",
    yaxis=dict(type="log", exponentformat="power", dtick=1))
    st.plotly_chart(fig2)
    
    
   # --- gráfico vg vs log(IDS) e log(IGS) sobrepostos ---
    st.subheader("VG vs log(IDS) e log(IGS)")
    transistor3 = st.multiselect(
        "Escolha um transistor",
        df["Transistor"].unique(),
        default=[1],
        key="transistor_ids_igs")
    fig3 = go.Figure()

    for i, t in enumerate(transistor3):
        cor = cores[i % len(cores)]
        df_transistor = df_log[df_log["transistor"] == t]
        fig3.add_trace(go.Scatter(x=df_transistor["VG"], y=df_transistor["IDS"], name=f"Transistor {t} - IDS", line=dict(color="blue", dash="solid")))  
        fig3.add_trace(go.Scatter(x=df_transistor["VG"], y=df_transistor["IGS"], name=f"Transistor {t} - IGS", line=dict(color="red", dash="solid")))
        fig3.update_layout(title="VG vs log(IDS) e log(IGS)", xaxis_title="VG", yaxis_title="Corrente (A)",
        yaxis=dict(type="log", exponentformat="power", dtick=1))
    st.plotly_chart(fig3)   
    
    
     # --- razao ids/igs ---
    st.subheader("Razão IDS/IGS por Transistor")
    transistores = st.multiselect(
        "Escolha os transistores",
        df["Transistor"],
        default=df["Transistor"]
    )
    df_filtrado = df[df["Transistor"].isin(transistores)]  
    fig_razao = go.Figure()
    fig_razao.add_trace(go.Scatter(x=df_filtrado["Transistor"], y=df_filtrado["Razão IDS/IGS"], mode="lines+markers"))
    fig_razao.update_layout(
        title="Razão IDS/IGS por Transistor",
        xaxis_title="Transistor"
    )
    st.plotly_chart(fig_razao)
    
    # grafico raiz do ids com reta de ajuste (vth)
    st.subheader("VG vs √IDS — Extração do Vth")
    transistor4 = st.multiselect(
        "Escolha um transistor",
        df["Transistor"].unique(),
        default=[df["Transistor"].unique()[0]],
        key="transistor_vth"
    )

    fig4 = go.Figure()

    vth_resultados = []
    for i, t in enumerate(transistor4):
        cor = cores[i % len(cores)]
        df_t = df_log[(df_log["transistor"] == t) & (df_log["direction"] == "ida")].dropna(subset=["IDS", "VG", "sqrt_IDS"]) #dropna joga fora os nan

        vg_vals = df_t["VG"].values
        sqrt_ids_vals = df_t["sqrt_IDS"].values

        # curva raiz do ids
        fig4.add_trace(go.Scatter(
            x=vg_vals,
            y=sqrt_ids_vals,
            name=f"Transistor {t} — √IDS (ida)",
            mode="lines",
            line=dict(color=cor, dash="solid")
        ))

        row = df[df["Transistor"] == t]
        if not row.empty:
            a = row["a (coef. angular)"].values[0]
            b = row["b (coef. linear)"].values[0]
            vth = row["Vth (V)"].values[0]

            vg_reta = np.linspace(vg_vals.min(), vg_vals.max(), 200) #retorna um array de 200 numeros
            sqrt_reta = a * vg_reta + b #eixo y
            
            #isso é pra deixar o eixo y acima de 0
            mask = sqrt_reta >= 0
            vg_reta = vg_reta[mask]
            sqrt_reta = sqrt_reta[mask]

            fig4.add_trace(go.Scatter(
                x=vg_reta,
                y=sqrt_reta,
                name=f"Transistor {t} — Reta de ajuste (Vth={vth:.2f} V)",
                line=dict(color=cor, dash="dash", width=2)
            ))

            fig4.add_trace(go.Scatter(
                x=[vth],
                y=[0],
                mode="markers+text",
                marker=dict(color=cor, size=10, symbol="x"),
                text=[f"Vth={vth:.2f} V"],
                textposition="top right",
                showlegend=False
            ))

            vth_resultados.append({"Transistor": t, "Vth (V)": vth})

    fig4.update_layout(
        xaxis_title="VG (V)",
        yaxis_title="√IDS (A^0.5)",
    )
    st.plotly_chart(fig4)

    # tabela vth
    if vth_resultados:
        st.subheader("Vth por Transistor")

        resumo = []
        for t in transistor4:
            linha_df = df[df["Transistor"] == t]
            if not linha_df.empty:
                vg_ref = linha_df["VG"].values[0]
                ids_ref = linha_df["IDS (A)"].values[0]
                vth_ref = linha_df["Vth (V)"].values[0]
                resumo.append({
                    "Transistor": t,
                    "IDS (A)": ids_ref,
                    "√IDS (A^0.5)": np.sqrt(ids_ref),
                    "Vth (V)": vth_ref
                })

        df_resumo = pd.DataFrame(resumo)
        st.dataframe(
            df_resumo,
            use_container_width=True,
            column_config={
                "IDS (A)": st.column_config.NumberColumn(format="%.6e"),
                "√IDS (A^0.5)": st.column_config.NumberColumn(format="%.6e"),
                "Vth (V)": st.column_config.NumberColumn(format="%.4f"),
            }
        )
        
        media_vth = df_resumo["Vth (V)"].mean()
        st.markdown(f"#### Média do Vth: {media_vth:.4f} V")
        
            # --- resumo geral ---
    st.header("Resumo Geral")

    onoff_media = df["Razão on/off"].mean()
    onoff_dp = df["Razão on/off"].std()
    vth_media = df["Vth (V)"].mean()
    vth_dp = df["Vth (V)"].std()

    resumo_geral = pd.DataFrame([{
        "Arquivo": arquivo_upload.name,
        "Razão on/off": f"{onoff_media:.2e} ± {onoff_dp:.2e}",
        "Vth (V)": f"{vth_media:.4f} ± {vth_dp:.4f}",
    }])

    st.dataframe(resumo_geral, use_container_width=True)
else:
    st.warning("Por favor, suba um arquivo .xlsx para continuar")
    st.stop()
        
    