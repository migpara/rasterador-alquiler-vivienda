import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error
)
import joblib

# =========================
# CONFIGURACIÓN
# =========================
ARCHIVO = "dataset_madrid_limpio_IA.csv"
MODELO_SALIDA = "modelo_tasadorv2.joblib"

pd.set_option('display.max_columns', None)

print("🏠 ENTRENANDO IA DE ALQUILERES (RANDOM FOREST - VERSIÓN FINAL)")

# =========================
# 1. CARGA DE DATOS
# =========================
try:
    df = pd.read_csv(ARCHIVO, sep=';')
    print(f"✅ Datos cargados correctamente: {len(df)} pisos.")
except FileNotFoundError:
    print(f"❌ Error: No se encuentra '{ARCHIVO}'. Ejecuta primero el script de limpieza.")
    exit()

# =========================
# 2. TARGET (y) Y PREPARACIÓN
# =========================
# Predecimos el LOG del precio para estabilidad
y = df['log_precio']

# Eliminamos columnas que NO deben ver la IA
columnas_a_borrar = [
    'precio',        # objetivo real
    'log_precio',    # objetivo transformado
    'precio_m2',     # TRAMPA (leakage)
    'titulo',        # texto
    'url'            # identificador
]
X_bruto = df.drop(columns=columnas_a_borrar)

# =========================
# 3. SEGURIDAD: FILTRAR BARRIOS SOLITARIOS
# =========================
# Antes del One-Hot, eliminamos barrios con 1 solo piso para evitar errores en stratify
conteo_barrios = df['barrio'].value_counts()
barrios_solitarios = conteo_barrios[conteo_barrios < 2].index

if len(barrios_solitarios) > 0:
    print(f"⚠️ Eliminando {len(barrios_solitarios)} barrios con 1 solo piso para poder estratificar.")
    # Filtramos el DataFrame original para mantener la coherencia
    df_seguro = df[~df['barrio'].isin(barrios_solitarios)].copy()
    
    # Recalculamos X e y con el df filtrado
    y = df_seguro['log_precio']
    X_bruto = df_seguro.drop(columns=columnas_a_borrar)
else:
    df_seguro = df

# =========================
# 4. ONE-HOT ENCODING
# =========================
print("🔄 Transformando barrios a formato numérico...")
X = pd.get_dummies(X_bruto, columns=['barrio'], drop_first=True)

print(f"🧠 Total de variables usadas por la IA: {X.shape[1]}")

# =========================
# 5. TRAIN / TEST SPLIT (ESTRATIFICADO)
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=df_seguro['barrio']   # Usamos el df filtrado
)

print(f"📚 Train: {len(X_train)} pisos")
print(f"📝 Test:  {len(X_test)} pisos")

# =========================
# 6. ENTRENAMIENTO DEL MODELO
# =========================
print("🏋️‍♂️ Entrenando Random Forest...")

modelo = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

modelo.fit(X_train, y_train)

# =========================
# 7. EVALUACIÓN (FIX DE ERROR)
# =========================
print("🧪 Evaluando modelo...")

# Predicciones
pred_log_test = modelo.predict(X_test)
pred_test = np.exp(pred_log_test)
y_real_test = np.exp(y_test)

pred_log_train = modelo.predict(X_train)
pred_train = np.exp(pred_log_train)
y_real_train = np.exp(y_train)

# Métricas
mae = mean_absolute_error(y_real_test, pred_test)
mape = mean_absolute_percentage_error(y_real_test, pred_test)

# ---Calculamos RMSE manualmente ---
mse = mean_squared_error(y_real_test, pred_test) # Calculamos error cuadrático medio
rmse = np.sqrt(mse)                              # Y hacemos la raíz cuadrada con Numpy
# ----------------------------------------------------

train_mape = mean_absolute_percentage_error(y_real_train, pred_train)

print("\n" + "=" * 45)
print("📊 RESULTADOS DEL MODELO")
print(f"🔹 MAE (Error medio):       {mae:.0f} €")
print(f"🔹 RMSE (Desviación):      {rmse:.0f} €")
print(f"🔹 MAPE TEST:              {mape:.2%}")
print(f"🔹 MAPE TRAIN:             {train_mape:.2%}")
print("=" * 45)

# Interpretación
if mape < 0.15:
    print("🌟 EXCELENTE: IA a nivel tasador profesional")
elif mape < 0.20:
    print("✅ MUY BUENA: válida para detectar gangas")
else:
    print("⚠️ Mejorable: considera más datos o features")

# =========================
# 8. IMPORTANCIA DE VARIABLES
# =========================
importancias = pd.Series(
    modelo.feature_importances_,
    index=X.columns
).sort_values(ascending=False)

print("\n🔍 TOP 10 VARIABLES MÁS IMPORTANTES")
print(importancias.head(10))

# =========================
# 9. GUARDAR MODELO
# =========================
pack_modelo = {
    "modelo": modelo,
    "columnas": list(X.columns),
    "mae": mae,
    "mape": mape
}

joblib.dump(pack_modelo, MODELO_SALIDA)

print("\n💾 Modelo guardado correctamente como:")
print(f"   👉 {MODELO_SALIDA}")
print("🚀 LISTO PARA DETECTAR GANGAS")