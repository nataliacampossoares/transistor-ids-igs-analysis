import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_excel("Dados Transistores maiza_ic_natalia.xlsx")

resultados = []
for i in range(1, 10):
    for j in range(len(df)):
        resultados.append({
            "VG": df["Potencial (V)"][j],
            "IDS": df[f"{i}_IDS"][j],
            "IGS": df[f"{i}_IGS"][j],
            "transistor": i
        })

df_resultado = pd.DataFrame(resultados)

# remove as colunas vazias (Unnamed)
df_resultado = df_resultado.dropna(subset=["IDS", "IGS"])

# coloca IDS em valor absoluto
df_resultado["IDS"] = np.abs(df_resultado["IDS"])

# calcula o log do IDS
df_resultado["log_IDS"] = np.log10(df_resultado["IDS"])

# salva o CSV
df_resultado.to_csv("dados_transistores.csv", index=False)

print("Arquivo salvo")
print(df_resultado.head())