import pandas as pd
import numpy as np

# =========================
# CONFIGURACIÓN
# =========================
ARCHIVO_ENTRADA = "dataset_madrid_definitivo.csv"
ARCHIVO_SALIDA = "dataset_madrid_limpio_IA.csv"

print("🧹 INICIANDO LIMPIEZA DE DATOS PARA IA ...")

# =========================
# 1. CARGA DEL DATASET
# =========================
try:
    df = pd.read_csv(ARCHIVO_ENTRADA, sep=';')
    print(f"📥 Archivo cargado correctamente. Filas originales: {len(df)}")
except FileNotFoundError:
    print(f"❌ Error: No se encuentra el archivo '{ARCHIVO_ENTRADA}'")
    exit()

# =========================
# 2. ELIMINAR DUPLICADOS
# =========================
filas_antes_dup = len(df)
df = df.drop_duplicates(subset='url', keep='first')
print(f"🗑️  Duplicados eliminados: {filas_antes_dup - len(df)} pisos.")

# =========================
# 3. RECUPERAR BARRIOS DESDE EL TÍTULO
# =========================
def recuperar_barrio(row):
    if row['barrio'] != 'Otros Madrid':
        return row['barrio']

    titulo = str(row['titulo'])
    partes = [p.strip() for p in titulo.split(',')]

    if len(partes) >= 2:
        posible = partes[-2]
        if (
            any(char.isdigit() for char in posible)
            or "Calle" in posible
            or "Plaza" in posible
            or "Avenida" in posible
            or "Paseo" in posible
        ):
            if len(partes) >= 3:
                posible = partes[-3]

        posible = posible.replace("Madrid", "").strip()

        if len(posible) > 2:
            return posible

    return "Otros Madrid"

print("🕵️‍♂️  Recuperando barrios ocultos...")
df['barrio'] = df.apply(recuperar_barrio, axis=1)

# =========================
# 4. LIMPIEZA BÁSICA
# =========================
filas_antes_hard = len(df)
df = df[
    (df['metros'] >= 15) & (df['metros'] <= 500) &
    (df['precio'] >= 400) & (df['precio'] <= 15000)
]
print(f"📉 Filas eliminadas por valores irreales: {filas_antes_hard - len(df)}")

# =========================
# 5. NORMALIZAR PLANTA
# =========================
df['planta'] = df['planta'].clip(lower=-1, upper=15)

# =========================
# 6. FEATURE ENGINEERING (COMPLETO)
# =========================

# A) BÁSICAS
df['precio_m2'] = (df['precio'] / df['metros']).round(2)
df['es_piso_alto'] = (df['planta'] >= 3).astype(int)

# B) AVANZADAS
df['es_estudio'] = (df['habitaciones'] == 0).astype(int)
# Metros por habitación (protegiendo división por cero)
df['metros_por_habitacion'] = (df['metros'] / df['habitaciones'].replace(0, 1)).round(2)
# Logaritmo del precio (Vital para la IA)
df['log_precio'] = np.log(df['precio'])

# C) CASTIGOS Y SCORES
df['penalizacion_sin_ascensor'] = ((df['ascensor'] == 0) & (df['planta'] >= 3)).astype(int)
df['score_calidad'] = (
    df['ascensor'] + df['garaje'] + df['terraza'] +
    df['aire'] + df['amueblado'] + df['reformado']
)

print("➕ Variables de Inteligencia Artificial generadas (incluido Log y Metros/Hab).")

# =========================
# 7. ELIMINAR OUTLIERS POR BARRIO
# =========================
filas_antes_outlier = len(df)

def filtrar_outliers_barrio(grupo):
    # PROTECCIÓN BARRIOS PEQUEÑOS
    if len(grupo) < 5:
        return grupo
    
    p5 = grupo['precio_m2'].quantile(0.05)
    p95 = grupo['precio_m2'].quantile(0.95)
    return grupo[(grupo['precio_m2'] >= p5) & (grupo['precio_m2'] <= p95)]

df = df.groupby('barrio', group_keys=False).apply(filtrar_outliers_barrio)

print(f"🧠 Outliers contextuales eliminados: {filas_antes_outlier - len(df)}")

# =========================
# 8. GUARDAR
# =========================
df = df.reset_index(drop=True)
df.to_csv(ARCHIVO_SALIDA, sep=';', index=False, encoding='utf-8-sig')

print("\n" + "=" * 45)
print("✅ LIMPIEZA COMPLETADA (VERSIÓN FULL)")
print(f"📄 Archivo generado: {ARCHIVO_SALIDA}")
print(f"📊 Total pisos: {len(df)}")
print("=" * 45)