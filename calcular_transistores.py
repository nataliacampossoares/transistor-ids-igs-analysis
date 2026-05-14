import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_excel("data/dados_transistores_raw.xlsx")

resultados_dados = []
for i in range(1, 10):
    for j in range(len(df)):
        resultados_dados.append({
            "VG": df["Potencial (V)"][j],
            "IDS": df[f"{i}_IDS"][j],
            "IGS": df[f"{i}_IGS"][j],
            "transistor": i
        })

df_resultado = pd.DataFrame(resultados_dados)

# remove as colunas vazias (Unnamed)
df_resultado = df_resultado.dropna(subset=["IDS", "IGS"])

# coloca IDS em valor absoluto
df_resultado["IDS"] = np.abs(df_resultado["IDS"])

# calcula o log do IDS
df_resultado["log_IDS"] = np.log10(df_resultado["IDS"])

# salva o CSV
df_resultado.to_csv("outputs/dados_transistores.csv", index=False)

VG_alvo = 4.0
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

    razao_on_off = dados["IDS"].max() / dados["IDS"].min() # aq calcula a razao on/off de cada ciclo
    #eu tinha calculado a principio com o df, mas tinha os dados de ida e volta juntos. depois foi com o df_result, mas os valores de bg eram todos -2,5v 
    resultados.append({
        "Transistor": transistor,
        "VG": VG_alvo,
        "IDS (A)": ids,
        "IGS (A)": igs,
        "Razão IDS/IGS": razao,
        "Razão on/off": razao_on_off,
        "direction": "ida",
        "Valor Máximo IDS": dados["IDS"].max(),
        "Valor Mínimo IDS": dados["IDS"].min()
    })


df_result = pd.DataFrame(resultados)
df_result.to_csv("outputs/razao_transistores.csv", index=False)

print("Arquivo salvo")