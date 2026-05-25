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

# coloca IDS em valor absoluto
df_resultado["IDS"] = np.abs(df_resultado["IDS"])

# calcula o log do IDS
df_resultado["log_IDS"] = np.log10(df_resultado["IDS"])

# salva o CSV
df_resultado.to_csv("outputs/dados_transistores.csv", index=False)

print(df_resultado["VG"].max())
print(df_resultado["VG"].min())

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
    resultados.append({
        "Transistor": transistor,
        "VG": VG_alvo,
        "IDS (A)": ids,
        "IGS (A)": igs,
        "Razão IDS/IGS": razao,
        "Razão on/off": razao_on_off,
        "Valor Máximo IDS": dados["IDS"].max(),
        "Valor Mínimo IDS": dados["IDS"].min()
    })


df_result = pd.DataFrame(resultados)
df_result.to_csv("outputs/razao_transistores.csv", index=False)