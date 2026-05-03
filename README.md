# 🔋 Dashboard — Transición Energética en Colombia
**Bootcamp Talento Tech · Análisis de Datos · Nivel Integrador**

---

## 📁 Estructura del proyecto

```
streamlit_energia/
├── app.py              ← App principal (ejecutar este)
├── database.py         ← Conexión MySQL + carga de datasets
├── theme.py            ← Paleta de colores y utilidades visuales
├── requirements.txt    ← Dependencias Python
├── .streamlit/
│   └── config.toml     ← Tema oscuro personalizado
└── README.md
```

---

## 🚀 Ejecutar localmente

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Lanzar la app
```bash
streamlit run app.py
```

La app abre automáticamente en `http://localhost:8501`

---

## 🌐 Desplegar en Streamlit Community Cloud (gratis)

### Paso 1 — Subir a GitHub
```bash
git init
git add .
git commit -m "Dashboard Transición Energética Colombia"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/dashboard-energia-colombia.git
git push -u origin main
```

### Paso 2 — Conectar con Streamlit Cloud
1. Ve a **[share.streamlit.io](https://share.streamlit.io)**
2. Inicia sesión con tu cuenta de GitHub
3. Clic en **"New app"**
4. Selecciona tu repositorio → Rama: `main` → Archivo: `app.py`
5. Clic en **"Deploy!"**

✅ En ~2 minutos tendrás una URL pública tipo:
`https://tu-usuario-dashboard-energia-colombia-app-xxxx.streamlit.app`

---

## 📊 Módulos del Dashboard

| Tab | Contenido | Filtros |
|-----|-----------|---------|
| ⚡ Capacidad Renovable | Ranking dpto + mix por fuente | Año · Región · Fuente · Top N |
| 📈 Evolución Temporal | Líneas / Área / Barras por fuente + CAGR | Fuentes · Depto · Métrica · Tipo gráfico |
| 💡 Consumo & Costos | Barras apiladas + heatmap costos | Región · Sector · Rango años |
| 🌿 Emisiones CO₂ | Tendencia · Apilado · vs Meta NDC | Sector · Depto · Vista |
| 🏗️ Proyectos ERNC | Inversión · Scatter · Tabla completa | Estado · Tipo · Depto |
| 🗺️ Zonas ZNI | Horas servicio · Población · Proyectos | Región · Cobertura |
| 🔬 Análisis Comparativo | Índice transición · CAGR · Correlaciones | Vista |

---

## 🗄️ Base de datos
- **Motor:** MySQL 8.0
- **Host:** 82.197.82.63
- **BD:** u748235332_energetica
- **Tablas:** 7 (departamentos, fuentes_energia, capacidad_instalada, consumo_energetico, emisiones_co2, proyectos_ernc, zonas_no_interconectadas)
- **Fuente:** [datos.gov.co](https://www.datos.gov.co) — IPSE · UPME · IDEAM · DANE
