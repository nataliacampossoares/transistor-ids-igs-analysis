import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Leitura dos dados ---
arquivo_dados = "dados_transistor com leakage.txt"
df = pd.read_csv(arquivo_dados, sep="\t", header=0)

# --- Limpeza dos dados ---
df = df[pd.to_numeric(df["VG"], errors='coerce').notnull()]
df = df[pd.to_numeric(df["IDS"], errors='coerce').notnull()]
df = df[pd.to_numeric(df["IGS"], errors='coerce').notnull()]
df["VG"] = df["VG"].astype(float)
df["IDS"] = df["IDS"].astype(float)
df["IGS"] = df["IGS"].astype(float)

# --- Identificação dos ciclos ---
cycle = -1
cycle_ids = []
prev_in_cycle_start = False

for val in df["VG"]:
    in_cycle_start = (val <= -0.95)  # define o início de um novo ciclo
    if in_cycle_start and not prev_in_cycle_start:
        cycle += 1
    cycle_ids.append(cycle)
    prev_in_cycle_start = in_cycle_start

df["cycle_id"] = cycle_ids

# --- Direção: subida ou descida ---
df["diff_VG"] = df["VG"].diff()
df["direction"] = np.where(df["diff_VG"] < 0, "ida", "volta")  # descida = ida negativa

# --- Filtra apenas a ida (descida de +0.5 V até -2.5 V) ---
df_ida = df[df["direction"] == "ida"].copy()

# --- Análise por ciclo ---
resultados = []

VG_alvo = -2.5
tolerancia = 0.1  # ajuste conforme necessário

for ciclo in sorted(df_ida["cycle_id"].unique()):
    dados = df_ida[df_ida["cycle_id"] == ciclo]
    ponto = dados[np.isclose(dados["VG"], VG_alvo, atol=tolerancia)]

    if ponto.empty:
        continue

    ids = ponto["IDS"].values[0]
    igs = ponto["IGS"].values[0]
    
    if igs == 0:
        razao = np.nan
    else:
        razao = ids / igs

    resultados.append({
        "Ciclo": ciclo,
        "VG": VG_alvo,
        "IDS (A)": ids,
        "IGS (A)": igs,
        "Razão IDS/IGS": razao
    })

df_result = pd.DataFrame(resultados)

# --- Estatísticas ---
media_razao = df_result["Razão IDS/IGS"].mean()
std_razao = df_result["Razão IDS/IGS"].std()

# --- Salvamento dos resultados ---
df_result.to_csv("razao_ids_igs_por_ciclo_-2.5V.csv", index=False)

# --- Gráfico: razão IDS/IGS por ciclo ---
plt.figure(figsize=(10,6))
plt.plot(df_result["Ciclo"], df_result["Razão IDS/IGS"], 'd-', color='purple', label='Razão IDS/IGS por ciclo')
plt.axhline(media_razao, color='orange', linestyle='--', label=f"Média = {media_razao:.2e}")
plt.fill_between(df_result["Ciclo"], media_razao - std_razao, media_razao + std_razao, color='orange', alpha=0.2, label="±1σ")
plt.xlabel("Número do Ciclo")
plt.ylabel("Razão IDS / IGS (em VG = -2.5 V)")
plt.title("Razão IDS/IGS por Ciclo (ida negativa)")
plt.yscale('log')  # Escala logarítmica
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig("razao_ids_igs_por_ciclo_-2.5V.png", dpi=300)
plt.show()