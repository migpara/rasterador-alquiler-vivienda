# 🏠 ViviendaRadar: Inteligencia Artificial para el Mercado de Alquileres en Madrid

[Español](#español) | [English](#english)

---

# Español

> **Un proyecto personal nacido de ver a muchos jóvenes cercanos luchar por acceder a una vivienda digna en Madrid**

---
## ⚠️ Nota:
Idealista bloquea tráfico desde IPs de datacenter (GitHub Actions, Azure, etc.).
El scraper está diseñado para ejecución local o con proxy residencial

## ⚠️ DISCLAIMER LEGAL Y COPYRIGHT

**AVISO IMPORTANTE - LEE ESTO ANTES DE USAR**

### Propiedad Intelectual
© 2026 **Miguel Paniagua** - Todos los derechos reservados.

Este proyecto fue creado originalmente por Miguel Paniagua y está **completamente protegido** por derechos de autor.

### Sobre la Licencia MIT + Restricciones Comerciales

Este proyecto está licenciado bajo una **MIT License modificada** con restricciones adicionales para uso comercial:

✅ **PERMITIDO (Uso No-Comercial):**
- Usar el código para aprender y educación
- Modificar el código para uso personal
- Compartir el código (siempre dando crédito)
- Contribuir mejoras al proyecto original

❌ **PROHIBIDO (Sin Autorización Previa):**
- **Cualquier uso comercial** (vender servicios basados en esto)
- **Generar ingresos** directa o indirectamente
- **Usar para un negocio o startup** sin permiso
- **Vender acceso a la herramienta**
- **Reclamar la autoría** o presentarlo como propio
- **Crear un producto comercial** basado en este código

### Clave: Beneficio Económico = Necesitas Permiso

Si tu intención es hacer dinero con este código (de cualquier forma):
- 🚫 **NO PUEDES** hacerlo sin autorización
- 📧 **DEBES** contactar a Miguel Paniagua para una licencia comercial
- 💼 Se requiere acuerdo explícito y por escrito
- 💰 Puede requerir compensación económica

---

## 📖 Sobre Este Proyecto

**ViviendaRadar** es un sistema completo de aprendizaje automático diseñado para democratizar el acceso a información del mercado de alquileres en Madrid. Combina web scraping, ingeniería de datos e inteligencia artificial para identificar pisos con precios injustos y alertar sobre oportunidades excepcionales.

### 💡 La Motivación

Creé este proyecto porque veía que mucha gente joven cercana no podía acceder a un alquiler digno. Los precios de alquiler se han desvinculado cada vez más de la realidad y, sin una inteligencia de mercado adecuada, los inquilinos quedan atrapados entre opciones imposibles: pagar demasiado por una vivienda básica o aceptar condiciones muy precarias.

**ViviendaRadar** existe para nivelar el campo de juego: poner herramientas potentes de análisis de mercado en manos de quienes más las necesitan, ayudándoles a encontrar una vivienda digna a precios más justos.

---

## 🎯 ¿Qué Hace ViviendaRadar?

1. **Recopila** ~2.100 anuncios de alquiler desde Idealista (Madrid)
2. **Limpia y transforma** los datos con más de 20 variables diseñadas para IA
3. **Entrena** un modelo Random Forest que estima el precio justo de alquiler
4. **Rastrea** nuevos anuncios en tiempo (casi) real con Selenium
5. **Evalúa** cada anuncio y detecta gangas y oportunidades
6. **Envía alertas** por Telegram cuando detecta chollos
7. **Expone una API REST** para usar el tasador desde otras apps o scripts

---

## 🏗️ Arquitectura del Sistema

```text
PROYECTO_INMOBILIARIO_BOT/       
├── .env                     <-- ¡AQUÍ IRÁN TUS CLAVES!
├── .gitignore               <-- EL ESCUDO (protege .env)
├── requirements.txt         <-- LIBRERÍAS
├── LICENSE                  <-- PROTECCIÓN LEGAL
├── README.md                <-- ESTE ARCHIVO
├── api_tasadorav2.py
├── cosechadorav2.py
├── entrenar_tasadorav2.py
├── etl_limpiezav2.py
├── explorador_datosv2.py
├── rastreadorv2.py
└── dataset_madrid_*.csv     (no se suben a GitHub)
```

---

## 📦 Componentes del Proyecto

### 1. `cosechadorav2.py` – Recopilación de Datos
- Extrae ~2.100 anuncios desde Idealista
- Incluye 70 páginas de alquileres en Madrid
- **Características Extraídas:**
  - Precio, metros cuadrados, habitaciones, baños
  - Número de planta, amenidades (ascensor, parking, terraza, aire acondicionado)
  - Estado de amueblamiento y reforma
  - Detección de barrio desde el título del anuncio
  - Enlaces directos a las propiedades

### 2. `etl_limpiezav2.py` – Preparación de Datos
- **Deduplicación**: Elimina anuncios duplicados
- **Recuperación de Barrios**: Extrae inteligentemente el barrio del título del anuncio
- **Validación de Datos**: 
  - Metros cuadrados: 15-500 m²
  - Precio: €400-€15.000/mes
  - Elimina valores atípicos irreales
- **Ingeniería de Características** (20+ características):
  - `precio_m2`: Precio por metro cuadrado
  - `log_precio`: Transformación logarítmica del precio (estabiliza el modelo)
  - `metros_por_habitacion`: Métrica de eficiencia espacial
  - `es_piso_alto`: Binaria (planta ≥ 3)
  - `score_calidad`: Suma de amenidades (0-6)
  - `penalizacion_sin_ascensor`: Penalización por pisos altos sin ascensor

### 3. `entrenar_tasadorav2.py` – Entrenamiento del Modelo
- **Algoritmo**: Random Forest Regressor (300 árboles, profundidad=15)
- **Objetivo**: Precio de alquiler transformado logarítmicamente
- **Estrategia de Validación**: División train/test estratificada 80/20 por barrio
- **Métricas de Rendimiento**:
  - MAE (Error Medio Absoluto): ~€100-150
  - RMSE: ~€150-200
  - MAPE (Error Porcentual Medio Absoluto): ~15-18%
- **Salida**: Modelo serializado (`modelo_tasadorv2.joblib`)

### 4. `api_tasadorav2.py` – Servicio REST API
- **Framework**: FastAPI
- **Endpoint**: `POST /tasar`
- **Entrada**: Detalles de la propiedad (ubicación, tamaño, amenidades, etc.)
- **Salida**:
  ```json
  {
    "tasacion_ia": 1850,
    "precio_anuncio": 2100,
    "diferencia_porcentaje": "-13.5%",
    "veredicto": "✅ OPORTUNIDAD",
    "barrio_oficial": "Salamanca"
  }
  ```
- **Lógica de Veredicto**:
  - 🔥 **GANGA** (Gran oportunidad): > -25% por debajo del precio justo
  - ✅ **OPORTUNIDAD** (Buena oferta): -15% a -25% por debajo
  - ⚠️ **ALGO CARO** (Algo caro): +10% a +20% por encima
  - ❌ **MUY CARO** (Muy caro): > +20% por encima

### 5. `rastreadorv2.py` – Rastreador en Tiempo Real
- **Tecnología**: Selenium sin detección (anti-bot)
- **Función**: Monitorea continuamente Idealista buscando nuevos anuncios
- **Proceso**:
  1. Obtiene páginas de listado
  2. Accede a cada ficha de propiedad
  3. Extrae toda la información de la propiedad
  4. Llama a la API de predicción
  5. Envía alerta por Telegram si encuentra una ganga
  6. Guarda resultados en CSV
- **Características Clave**:
  - Delays aleatorios (2-4s) entre solicitudes
  - Pausa de 60 segundos cada 10 páginas para evitar bloqueos
  - Detecta palabras clave de oportunidad: "negociable", "urgente", "gastos incluidos"
  - Notificaciones Telegram con detalles y enlaces

### 6. `explorador_datosv2.py` – Exploración de Datos
- Genera mapas de calor de correlación
- Muestra distribución de barrios
- Identifica características más importantes para debugging del modelo

---

## 🚀 Cómo Ejecutar el Proyecto

### Requisitos Previos
```bash
pip install -r requirements.txt
```

### Ejecución del Pipeline Completo

**Paso 1: Recopilar Datos**
```bash
python cosechadorav2.py
# Salida: dataset_madrid_definitivo.csv (~2.100 propiedades)
```

**Paso 2: Limpiar y Preparar**
```bash
python etl_limpiezav2.py
# Salida: dataset_madrid_limpio_IA.csv (datos limpios, características ingeniadas)
```

**Paso 3: Entrenar Modelo**
```bash
python entrenar_tasadorav2.py
# Salida: modelo_tasadorv2.joblib (Random Forest entrenado)
```

**Paso 4: Iniciar Servicio API**
```bash
python api_tasadorav2.py
# Inicia FastAPI en http://0.0.0.0:8000
# Documentación de API: http://localhost:8000/docs
```

**Paso 5: Ejecutar Rastreador en Tiempo Real** (en otra terminal)
```bash
# Configurar primero el archivo .env:
# API_URL=http://localhost:8000/tasar
# TELEGRAM_TOKEN=tu_token_bot
# TELEGRAM_CHAT_ID=tu_chat_id

python rastreadorv2.py
# Monitorea Idealista y envía alertas a Telegram
```

---

## 🔌 Ejemplo de Uso de la API

### cURL

```bash
curl -X POST "http://localhost:8000/tasar" \
  -H "Content-Type: application/json" \
  -d '{
    "ubicacion": "Salamanca, Madrid",
    "metros": 85,
    "habitaciones": 2,
    "banos": 1,
    "planta": 4,
    "ascensor": true,
    "garaje": false,
    "amueblado": false,
    "reformado": true,
    "terraza": false,
    "aire": true,
    "precio_actual": 1800
  }'
```

### Respuesta tipo

```json
{
  "tasacion_ia": 1750,
  "precio_anuncio": 1800,
  "diferencia_porcentaje": "2.9%",
  "veredicto": "PRECIO DE MERCADO",
  "barrio_oficial": "Salamanca"
}
```

---

## 📱 Integración con Telegram

1. Crear bot con **@BotFather**.
2. Obtener `TELEGRAM_TOKEN`.
3. Obtener `CHAT_ID`.
4. Crear `.env`:

```env
TELEGRAM_TOKEN=tu_token_bot_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
API_URL=http://localhost:8000/tasar
```

Cuando se encuentre una ganga, recibirás:

```text
🚨 🔥 GANGA
📍 Salamanca
💰 Pide: 1500€ | IA: 1900€
📉 -21% descuento
🏠 75m² | 2 hab | 🚽 1 baño
🔗 https://www.idealista.com/...
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| **Web Scraping** | Selenium + BeautifulSoup4 + ChromeDriver sin detección |
| **Procesado de Datos** | Pandas + NumPy |
| **Machine Learning** | Scikit-learn (Random Forest) |
| **API** | FastAPI + Uvicorn + Pydantic |
| **Notificaciones** | API de Bot de Telegram |
| **Serialización de Modelo** | Joblib |
| **EDA/Visualización** | Seaborn + Matplotlib |

---

## 📋 Estructura de Protección de Archivos

### `.gitignore` - El Escudo
Protege los archivos sensibles de subirse a GitHub:
- `.env` ← TUS CLAVES PRIVADAS (nunca se suben)
- `*.csv` ← Datos (no se suben)
- `*.joblib` ← Modelos (no se suben)
- `__pycache__/` ← Basura Python

### `.env` - Credenciales Privadas
**NUNCA compartas este archivo.** Contiene:
```env
TELEGRAM_TOKEN=abc123xyz456
TELEGRAM_CHAT_ID=987654321
API_URL=http://localhost:8000/tasar
```

### `LICENSE` - Tu Escudo Legal
Archivo que establece:
- Quién es el propietario (Miguel Paniagua)
- Qué pueden hacer otros (MIT License)
- QUÉ NO PUEDEN HACER (Uso comercial sin permiso)

---

## ⚠️ Notas Legales, Limitaciones y Ética

### Sobre Web Scraping y Legalidad

El web scraping existe en una **zona gris legal**. Este proyecto fue desarrollado **únicamente para fines educativos**:

- ✅ **Permitido generalmente**: Recopilar datos públicos para investigación y educación.
- ❌ **Prohibido usualmente**: Violar términos de servicio, comercializar datos, sobrecargar servidores, recopilar datos personales sin consentimiento.

**Recomendaciones:**
- Revisa siempre `robots.txt` y `Terms of Service` del sitio.
- En España: respeta el RGPD (Reglamento General de Protección de Datos).
- Implementa delays suficientes para no sobrecargar los servidores.
- Usa User-Agent realista.
- No redistribuyas los datos sin permiso.

---

### Sobre Este Proyecto

- El scraper introduce esperas aleatorias y pausas largas para minimizar el riesgo de bloqueo y ser respetuoso.
- Este código se proporciona **tal cual**, sin garantías.
- El autor **no se responsabiliza** por usos no autorizados.
- Este proyecto está pensado **exclusivamente para aprendizaje y educación**.

---

### Limitaciones Técnicas

- El modelo está entrenado solo con datos de **Madrid**:
  - No extrapolar directamente a otras ciudades.
- No ve factores cualitativos no recogidos:
  - Vecindario concreto, ruido, vecinos, estado real de la finca, etc.
- Las "gangas" detectadas deben revisarse manualmente antes de tomar decisiones.

---

## 📈 Posibles Mejoras Futuras

- [ ] Soporte para otras ciudades (Barcelona, Valencia, etc.)
- [ ] Análisis de series temporales (tendencias de precio por barrio)
- [ ] Modelo de deep learning (redes neuronales)
- [ ] Dashboard web interactivo
- [ ] Integración con WhatsApp además de Telegram
- [ ] Resumen semanal por correo electrónico
- [ ] Rastreo histórico de precios por propiedad
- [ ] Puntuación de reputación de propietarios
- [ ] Pronóstico predictivo de precios

---

## 📝 Licencia y Copyright

**Copyright © 2026 Miguel Paniagua**

Este proyecto está licenciado bajo **MIT License con restricciones comerciales adicionales**.

Ver archivo `LICENSE` para los términos completos.

**Regla de Oro:** Si vas a generar dinero con esto → **Contacta con Miguel Paniagua primero.**

Para solicitar licencia comercial:
- 📧 Email: [migpanra@gmail.com]
- 💼 Incluye: detalles del uso, mercado objetivo, proyecciones financieras

---

## 👨‍💻 Autor

**Creado por:** Miguel Paniagua  
**Propósito:** Ayudar a que la vivienda digna sea más accesible para gente joven en Madrid  
**Motivación:** "Veía que mucha gente joven cercana no podía acceder a un alquiler digno"  
**Fecha:** 2026

---

## 🤝 Contribuir

Si quieres colaborar **de forma no-comercial**:

1. Haz un **fork** del repositorio
2. Crea una rama (`feature/mi-mejora`)
3. Envía un **pull request**
4. Proporciona atribución al proyecto original

---

## 🙏 Agradecimientos

- A todas las personas jóvenes que buscan vivienda en Madrid: este proyecto nace pensando en vosotras.
- A Idealista, como fuente de datos (usados respetuosamente).
- A la comunidad open source de Python, FastAPI y scikit-learn.

---

---

# English

> **A personal project born from seeing many young people around me struggling to access dignified housing in Madrid**

---

## ⚠️ LEGAL DISCLAIMER AND COPYRIGHT

**IMPORTANT NOTICE - READ THIS BEFORE USING**

### Intellectual Property
© 2026 **Miguel Paniagua** - All rights reserved.

This project was originally created by Miguel Paniagua and is **fully protected** by copyright.

### About MIT License + Commercial Restrictions

This project is licensed under a **modified MIT License** with additional restrictions for commercial use:

✅ **ALLOWED (Non-Commercial Use):**
- Use code for learning and education
- Modify code for personal use
- Share the code (always giving credit)
- Contribute improvements to the original project

❌ **PROHIBITED (Without Prior Authorization):**
- **Any commercial use** (selling services based on this)
- **Generating revenue** directly or indirectly
- **Using for a business or startup** without permission
- **Selling access to the tool**
- **Claiming authorship** or presenting it as your own
- **Creating a commercial product** based on this code

### Key: Economic Benefit = You Need Permission

If your intention is to make money with this code (in any way):
- 🚫 **YOU CANNOT** do it without authorization
- 📧 **YOU MUST** contact Miguel Paniagua for a commercial license
- 💼 Explicit written agreement required
- 💰 May require monetary compensation

---

## 📖 About This Project

**ViviendaRadar** is an end-to-end machine learning system designed to democratize access to rental market intelligence in Madrid. It combines web scraping, data engineering and AI to detect unfairly priced rentals and highlight exceptional opportunities.

### 💡 Motivation

This project was created after seeing many young people close to me unable to access decent rentals in Madrid. Rental prices have become increasingly detached from reality, and without proper market data, tenants are forced into impossible choices: overpay for basic housing or accept very poor conditions.

**ViviendaRadar** aims to level the playing field by putting powerful market analysis tools in the hands of those who need them most, helping them find dignified housing at fairer prices.

---

## 🎯 What ViviendaRadar Does

1. **Collects** ~2,100 rental listings from Idealista (Madrid)
2. **Cleans & transforms** the data with 20+ AI-ready features
3. **Trains** a Random Forest model to estimate fair market rent
4. **Monitors** new listings in (near) real time using Selenium
5. **Evaluates** each listing to flag bargains and overpriced units
6. **Sends alerts** via Telegram when a great deal is detected
7. **Exposes a REST API** so the pricing engine can be consumed by other tools

---

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Scrape data:
   ```bash
   python cosechadorav2.py
   ```

3. Clean & prepare:
   ```bash
   python etl_limpiezav2.py
   ```

4. Train model:
   ```bash
   python entrenar_tasadorav2.py
   ```

5. Start API:
   ```bash
   python api_tasadorav2.py
   ```

6. Run tracker (with `.env` configured):
   ```bash
   python rastreadorav2.py
   ```

For full implementation details, refer to the Spanish section above.

---

## ⚠️ Legal & Ethical Notes

### On Web Scraping and Legality

Web scraping exists in a **legal gray area**. This project was developed **solely for educational purposes**:

- ✅ **Generally Allowed**: Collecting public data for research and education.
- ❌ **Usually Prohibited**: Violating Terms of Service, commercializing data, overloading servers, collecting personal data without consent.

---

## 📝 License and Copyright

**Copyright © 2026 Miguel Paniagua**

This project is licensed under **MIT License with additional commercial restrictions**.

See `LICENSE` file for complete terms.

**Golden Rule:** If you're going to make money with this → **Contact Miguel Paniagua first.**

For commercial licensing inquiries:
- 📧 Email: [migpanra@gmail.com]
- 💼 Include: details of use, target market, financial projections

---

## 🙏 Acknowledgments

- To all young people searching for housing in Madrid: this project exists with you in mind.
- To Idealista, as a data source (used responsibly).
- To the open source community of Python, FastAPI and scikit-learn.

---

**Remember:** Dignified housing is a right, not a privilege. ViviendaRadar exists to help democratize access to market information. Use it wisely. ✊
