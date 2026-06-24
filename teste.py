import pandas as pd
df = pd.read_csv("outputs/razao_transistores.csv")
print(df[["Transistor", "IDS (A)", "Vth (V)"]].to_string())