import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("dados_transistor com leakage.txt", sep="\t", header=0)
print(df.columns)
print(df.head())