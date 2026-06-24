import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

abas = ["Data", "Append1", "Append2", "Append3", "Append4", "Append5"]

resultados_dados = []
for i in range(6):             
    df = pd.read_excel("data/dados_brutos.xls", sheet_name=abas[i])
    for j in range(len(df)):
        resultados_dados.append({                       
            "VG" : df["BaseV"][j],               
            "IDS" : df["CollectorI"][j],                  
            "IGS" : df["BaseI"][j],
            "transistor": i
})

df_resultado = pd.DataFrame(resultados_dados)

# identifica a direção usando o diff do VG
df_resultado["diff_VG"] = df_resultado.groupby("transistor")["VG"].diff()
df_resultado["direction"] = np.where(df_resultado["diff_VG"] > 0, "ida", "volta")

# remove as colunas vazias (Unnamed)
df_resultado = df_resultado.dropna(subset=["IDS", "IGS"])

# coloca IDS e IGS em valor absoluto
df_resultado["IDS"] = np.abs(df_resultado["IDS"])
df_resultado["IGS"] = np.abs(df_resultado["IGS"])

# calcula o log do IDS
df_resultado["log_IDS"] = np.log10(df_resultado["IDS"])

# calcula a raiz quadrada do IDS
df_resultado["sqrt_IDS"] = np.sqrt(df_resultado["IDS"])

# salva o CSV
df_resultado.to_csv("outputs/dados_transistores.csv", index=False)


VG_alvo = 12.0
tolerancia = 0.1

resultados = []
for transistor in sorted(df_resultado["transistor"].unique()):
    dados = df_resultado[df_resultado["transistor"] == transistor]
    ponto = dados[np.isclose(dados["VG"], VG_alvo, atol=tolerancia)]

    if ponto.empty:
        continue

    ids = ponto["IDS"].values[0]
    igs = ponto["IGS"].values[0]
    
    if igs == 0:
        razao = np.nan
    else:
        razao = ids / igs

    razao_on_off = dados["IDS"].max() / dados["IDS"].min()
    
    
    dados_ida = dados[dados["direction"] == "ida"].dropna(subset=["sqrt_IDS", "VG"])
    
    # filtra so a faixa de vg onde a curva ja ta subindo (regiao linear)
    VG_MIN_AJUSTE = 5.0  
    VG_MAX_AJUSTE = 11.0
    dados_validos = dados_ida[(dados_ida["VG"] >= VG_MIN_AJUSTE) & (dados_ida["VG"] <= VG_MAX_AJUSTE)] #aq ajusta a janela de vg
    
    vg_vals = dados_validos["VG"].values #eixo x
    sqrt_ids_vals = dados_validos["sqrt_IDS"].values #eixo y

    if len(vg_vals) >= 2: #isso eh pra garantir que eh uma reta
        # np.polyfit(x, y, 1) encontra a reta y = a*x + b que minimiza a soma
        # dos erros ao quadrado entre os pontos reais e a reta (metodo dos
        # minimos quadrados). Aqui: sqrt_IDS = a*VG + b.
        coef = np.polyfit(vg_vals, sqrt_ids_vals, 1) #eixo x e y, grau de polinomio = 1. retorna os pontos 
        a, b = coef[0], coef[1]
        vth = -b / a if a != 0 else np.nan
    else:
        a, b, vth = np.nan, np.nan, np.nan
    
    resultados.append({
        "Transistor": transistor,
        "VG": VG_alvo,
        "IDS (A)": ids,
        "IGS (A)": igs,
        "Razão IDS/IGS": razao,
        "Razão on/off": razao_on_off,
        "Valor Máximo IDS": dados["IDS"].max(),
        "Valor Mínimo IDS": dados["IDS"].min(),
        "Vth (V)": round(vth, 4) if not np.isnan(vth) else np.nan,
        "a (coef. angular)": a,
        "b (coef. linear)": b
    })
    
df_result = pd.DataFrame(resultados)
df_result.to_csv("outputs/razao_transistores.csv", index=False)