import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

ARCHIVO="dataset_madrid_limpio_IA.csv"

#Cargar archivo
df=pd.read_csv(ARCHIVO,sep=';')
print(df.head())

#Crear mapa de calor para comprobar que variables infulyen mas

# Seleccionamos solo las columnas numéricas
cols_numericas = df.select_dtypes(include=[np.number])

matriz_corr=cols_numericas.corr()

#Dibujar el mapa de calor
plt.figure(figsize=(10, 8))
sns.heatmap(matriz_corr,annot=True,cmap="coolwarm",fmt=".2f")
plt.show()

print(df["barrio"].value_counts())