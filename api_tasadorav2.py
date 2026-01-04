# ==========================================
# api_tasadorav2.py
# ==========================================
import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# 1. CONFIGURACIÓN
app = FastAPI(title="ViviendaRadar AI 2.0", version="2.0")

# 2. MODELO DE DATOS (Input exacto que esperamos del rastreador)
class PisoInput(BaseModel):
    ubicacion: str
    metros: int
    habitaciones: int
    banos: int
    planta: int
    ascensor: bool   
    garaje: bool
    amueblado: bool
    reformado: bool
    terraza: bool   
    aire: bool       
    precio_actual: float 

# 3. VARIABLES GLOBALES
modelo = None
columnas_modelo = None

# 4. CARGA AL INICIO
@app.on_event("startup")
def cargar_cerebro():
    global modelo, columnas_modelo
    try:
        print("🔄 Cargando cerebro Random Forest V2...")
        pack = joblib.load("modelo_tasadorv2.joblib") 
        modelo = pack['modelo']
        columnas_modelo = pack['columnas']
        print(f"✅ Cerebro cargado. Espera {len(columnas_modelo)} variables.")
    except Exception as e:
        print(f"❌ ERROR: No encuentro 'modelo_tasadorv2.joblib'. {e}")

# 5. LÓGICA DE DETECCIÓN DE BARRIO
def buscar_barrio_en_texto(texto, columnas):
    cols_barrios = [c for c in columnas if c.startswith("barrio_")]
    texto = texto.lower()
    
    for col in cols_barrios:
        nombre_barrio = col.replace("barrio_", "").lower()
        if nombre_barrio in texto:
            return col, nombre_barrio.capitalize()
            
    return None, "Otros / Desconocido"

# 6. ENDPOINT DE TASACIÓN
@app.post("/tasar")
def tasar_propiedad(piso: PisoInput):
    if modelo is None:
        raise HTTPException(status_code=503, detail="Cerebro no cargado.")

    try:
        # --- A) FEATURE ENGINEERING ---
        # Calculamos las variables extra igual que en el entrenamiento
        es_estudio = 1 if piso.habitaciones == 0 else 0
        metros_por_habitacion = round(piso.metros / max(piso.habitaciones, 1), 2)
        es_piso_alto = 1 if piso.planta >= 3 else 0
        penalizacion_sin_ascensor = 1 if (not piso.ascensor and piso.planta >= 3) else 0
        
        score_calidad = (
            int(piso.ascensor) + int(piso.garaje) + int(piso.terraza) + 
            int(piso.aire) + int(piso.amueblado) + int(piso.reformado)
        )

        # --- B) PREPARAR EL DATAFRAME ---
        # Creamos DataFrame vacío con las columnas EXACTAS del entrenamiento
        df_input = pd.DataFrame(0, index=[0], columns=columnas_modelo)
        
        # Rellenamos datos (Usando los nombres cortos del CSV original)
        df_input['metros'] = piso.metros
        df_input['habitaciones'] = piso.habitaciones
        df_input['banos'] = piso.banos
        df_input['planta'] = piso.planta
        df_input['ascensor'] = int(piso.ascensor)
        df_input['garaje'] = int(piso.garaje)
        df_input['terraza'] = int(piso.terraza)
        df_input['aire'] = int(piso.aire)
        df_input['amueblado'] = int(piso.amueblado)
        df_input['reformado'] = int(piso.reformado)
        
        # Rellenamos calculadas
        df_input['es_estudio'] = es_estudio
        df_input['metros_por_habitacion'] = metros_por_habitacion
        df_input['es_piso_alto'] = es_piso_alto
        df_input['penalizacion_sin_ascensor'] = penalizacion_sin_ascensor
        df_input['score_calidad'] = score_calidad

        # --- C) BARRIO ---
        col_barrio, nombre_real = buscar_barrio_en_texto(piso.ubicacion, columnas_modelo)
        if col_barrio:
            df_input[col_barrio] = 1
        
        # --- D) PREDICCIÓN ---
        # Aseguramos que solo pasamos las columnas que el modelo conoce (ordenadas)
        df_final = df_input[columnas_modelo]
        
        pred_log = modelo.predict(df_final)[0]
        precio_justo = round(np.exp(pred_log), 0)

        # --- E) VEREDICTO ---
        diferencia = piso.precio_actual - precio_justo
        porcentaje_diff = (diferencia / precio_justo) * 100
        
        veredicto = "PRECIO DE MERCADO"
        if porcentaje_diff < -25: veredicto = "🔥 GANGA"
        elif porcentaje_diff < -15: veredicto = "✅ OPORTUNIDAD"
        elif porcentaje_diff > 20: veredicto = "❌ MUY CARO"
        elif porcentaje_diff > 10: veredicto = "⚠️ ALGO CARO"

        return {
            "tasacion_ia": precio_justo,
            "precio_anuncio": piso.precio_actual,
            "diferencia_porcentaje": f"{porcentaje_diff:.1f}%",
            "veredicto": veredicto,
            "barrio_oficial": nombre_real
        }

    except Exception as e:
        print(f"Error interno API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)