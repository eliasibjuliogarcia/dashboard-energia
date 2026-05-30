"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  DASHBOARD NACIONAL DE TRANSICIÓN ENERGÉTICA — COLOMBIA 2026               ║
║  Sistema de Inteligencia Energética · Nivel Ejecutivo                       ║
║  Stack: Python · Streamlit · Plotly · PyDeck · Pandas                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ── Dependencias ──────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import math

def _ca(hex_color: str, alpha_hex: str) -> str:
    """Convierte hex color + alpha hex a rgba() válido para CSS/Plotly."""
    _alpha_map = {
        '08':0.03,'0A':0.04,'10':0.06,'18':0.09,'1A':0.10,'20':0.13,
        '28':0.16,'30':0.19,'33':0.20,'40':0.25,'44':0.27,'50':0.31,
        '60':0.38,'66':0.40,'80':0.50,'88':0.53,'90':0.56,'A0':0.63,
        'B0':0.69,'C0':0.75,'D0':0.82,'E0':0.88,'F0':0.94,'FF':1.00,
    }
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    a = _alpha_map.get(alpha_hex.upper(), 0.5)
    return f"rgba({r},{g},{b},{a})"


# ══════════════════════════════════════════════════════════════════════════════
# 0 · CONFIGURACIÓN GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SITEN Colombia · Dashboard Energético 2026",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta "Deep Space Operations" ───────────────────────────────────────────
# Única, no genérica: sala de control energético, estética satelital
P = dict(
    void      = "#040810",   # negro absoluto (fondo)
    deep      = "#060D1A",   # azul abismo
    surface   = "#0A1628",   # superficie panel
    raised    = "#0E1F35",   # panel elevado
    glass     = "#122540",   # glassmorphism
    rim       = "#1A3A5C",   # bordes
    rimhi     = "#234E7A",   # bordes activos

    # Energía primaria — verde esmeralda neón
    neon      = "#00FF9D",   # neón puro
    neon_mid  = "#00D68A",   # neón medio
    neon_dim  = "#00A86B",   # neón apagado
    neon_glow = "rgba(0,255,157,0.15)",

    # Acento frío — cian eléctrico
    ice       = "#00E5FF",
    ice_mid   = "#00B8D4",
    ice_glow  = "rgba(0,229,255,0.12)",

    # Calor — ámbar para alertas y solar
    amber     = "#FFB020",
    amber_glow= "rgba(255,176,32,0.15)",

    # Crítico — rojo coral
    alert     = "#FF4560",
    alert_glow= "rgba(255,69,96,0.15)",

    # Tipografía
    text_hi   = "#E8F4FE",   # texto principal
    text_mid  = "#7AAFD4",   # texto secundario
    text_lo   = "#3D6B8E",   # texto apagado
    text_mute = "#1E4060",   # muy apagado

    # Grid
    grid      = "#0D2040",
    gridhi    = "#163060",

    # alias
    border    = "#1A3A5C",   # alias de rim
)

# ── Colores por tipo de fuente energética ────────────────────────────────────
ENERGY_COLORS = {
    "Solar":          P["amber"],
    "Eólica":         P["ice"],
    "Hidroeléctrica": P["neon"],
    "Gas Natural":    "#FF7043",
    "Carbón":         "#78909C",
    "Biomasa":        "#66BB6A",
    "Geotérmica":     "#CE93D8",
    "Nuclear":        P["neon_mid"],
}

REGION_COLORS = {
    "Andina":    "#7986CB",
    "Caribe":    P["amber"],
    "Pacífica":  P["neon"],
    "Orinoquía": "#FF7043",
    "Amazónica": "#66BB6A",
}

DEPT_REGION = {
    "Antioquia":"Andina","Bogotá D.C.":"Andina","Cundinamarca":"Andina",
    "Boyacá":"Andina","Santander":"Andina","N. Santander":"Andina",
    "Tolima":"Andina","Huila":"Andina","Caldas":"Andina","Risaralda":"Andina",
    "Quindío":"Andina",
    "La Guajira":"Caribe","Magdalena":"Caribe","Atlántico":"Caribe",
    "Bolívar":"Caribe","Cesar":"Caribe","Córdoba":"Caribe","Sucre":"Caribe",
    "San Andrés":"Caribe",
    "Valle del Cauca":"Pacífica","Cauca":"Pacífica","Nariño":"Pacífica",
    "Chocó":"Pacífica",
    "Meta":"Orinoquía","Casanare":"Orinoquía","Arauca":"Orinoquía",
    "Vichada":"Orinoquía",
    "Amazonas":"Amazónica","Caquetá":"Amazónica","Putumayo":"Amazónica",
    "Guainía":"Amazónica","Guaviare":"Amazónica","Vaupés":"Amazónica",
}

# ══════════════════════════════════════════════════════════════════════════════
# 1 · CSS PREMIUM — "Deep Space Operations"
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Barlow:wght@300;400;500&display=swap');

  html, body, [class*="css"] {{
    background-color: {P['void']} !important;
    font-family: 'Barlow', sans-serif;
    color: {P['text_hi']};
  }}

  .stApp {{
    background-color: {P['void']};
    background-image:
      linear-gradient(rgba(0,229,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
  }}

  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg,
      {P['deep']} 0%, {P['surface']} 40%, {P['deep']} 100%) !important;
    border-right: 1px solid {P['rim']};
  }}
  [data-testid="stSidebar"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, {P['neon']}, transparent);
  }}

  [data-testid="metric-container"] {{
    background: linear-gradient(145deg, {P['raised']}, {P['surface']}) !important;
    border: 1px solid {P['rim']} !important;
    border-radius: 10px !important;
    padding: 16px !important;
    backdrop-filter: blur(8px);
    transition: all .3s ease;
  }}
  [data-testid="metric-container"]:hover {{
    border-color: {P['neon_dim']} !important;
    box-shadow: 0 0 20px rgba(0,255,157,0.15);
  }}
  [data-testid="metric-container"] label {{
    color: {P['text_mid']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 2px;
    text-transform: uppercase;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {P['neon']} !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    text-shadow: 0 0 20px rgba(0,255,157,0.15);
  }}
  [data-testid="metric-container"] [data-testid="stMetricDelta"] svg {{
    display: none;
  }}

  .stTabs [data-baseweb="tab-list"] {{
    background: {P['surface']};
    border: 1px solid {P['rim']};
    border-radius: 8px;
    padding: 3px 4px;
    gap: 2px;
  }}
  .stTabs [data-baseweb="tab"] {{
    color: {P['text_lo']};
    border-radius: 6px;
    padding: 7px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: .8px;
    text-transform: uppercase;
    transition: all .2s;
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    color: {P['text_mid']};
    background: {P['raised']};
  }}
  .stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {P['glass']}, {P['raised']}) !important;
    color: {P['neon']} !important;
    border-bottom: 2px solid {P['neon']} !important;
    text-shadow: 0 0 12px rgba(0,255,157,0.15);
  }}

  .stButton > button {{
    background: transparent;
    border: 1px solid {P['neon_dim']};
    color: {P['neon']};
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
    transition: all .25s;
  }}
  .stButton > button:hover {{
    background: rgba(0,255,157,0.15);
    border-color: {P['neon']};
    box-shadow: 0 0 16px rgba(0,255,157,0.15);
  }}

  [data-baseweb="select"] > div,
  [data-baseweb="input"] > div {{
    background: {P['raised']} !important;
    border-color: {P['rim']} !important;
    color: {P['text_hi']} !important;
  }}

  [data-testid="stExpander"] {{
    background: {P['surface']};
    border: 1px solid {P['rim']};
    border-radius: 8px;
  }}

  ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
  ::-webkit-scrollbar-track {{ background: {P['deep']}; }}
  ::-webkit-scrollbar-thumb {{ background: {P['rim']}; border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: {P['neon_dim']}; }}

  [data-testid="stDataFrame"] {{
    border: 1px solid {P['rim']};
    border-radius: 8px;
    overflow: hidden;
  }}

  hr {{ border-color: {P['rim']} !important; }}

  .stSpinner > div {{
    border-top-color: {P['neon']} !important;
  }}

  [data-testid="stWarning"] {{
    background: rgba(255,176,32,0.15);
    border-color: {P['amber']};
    border-radius: 8px;
  }}

  @keyframes scan {{
    0%   {{ top: -2px; opacity: 1; }}
    100% {{ top: 100%; opacity: 0; }}
  }}
  .scan-line {{ position: relative; overflow: hidden; }}
  .scan-line::after {{
    content: '';
    position: absolute;
    top: -100%; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg,
      transparent, rgba(0,255,157,0.25), transparent);
    animation: scan 3s linear infinite;
  }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 2 · DATOS SIMULADOS — Colombia, realistas 2018-2026
# ══════════════════════════════════════════════════════════════════════════════

np.random.seed(42)
ANIOS = list(range(2018, 2027))

# ── Capacidad instalada por fuente (MW) ───────────────────────────────────────
@st.cache_data
def gen_capacidad():
    base = {
        "Solar":          [48, 105, 212, 480, 850, 1348, 2100, 3200, 4800],
        "Eólica":         [18,  18,  28, 100, 280, 532,  820, 1200, 1800],
        "Hidroeléctrica": [11200,11400,11600,11800,12000,12400,12800,13200,13800],
        "Gas Natural":    [3800,3850,3900,3950,4000,4050,4100,4150,4200],
        "Carbón":         [1050,1020, 980, 940, 900, 860, 820, 780, 720],
        "Biomasa":        [220, 240, 260, 290, 320, 355, 400, 450, 510],
    }
    rows = []
    for fuente, vals in base.items():
        for i, anio in enumerate(ANIOS):
            rows.append({"anio": anio, "fuente": fuente,
                         "capacidad_mw": vals[i]})
    return pd.DataFrame(rows)


# ── Emisiones CO₂ por sector (Mt) ─────────────────────────────────────────────
@st.cache_data
def gen_emisiones():
    sectores = {
        "Energía Eléctrica": [18.2,17.8,17.1,16.4,15.8,15.1,14.2,13.0,11.8],
        "Transporte":        [30.1,31.2,30.5,28.8,29.4,31.0,32.1,31.8,30.9],
        "Industria":         [22.4,22.8,22.5,20.1,21.2,22.0,22.8,23.1,22.5],
        "Agropecuario":      [14.2,14.5,14.8,14.6,14.9,15.1,15.3,15.0,14.8],
        "Residencial":       [6.8, 6.9, 7.0, 6.8, 6.9, 7.1, 7.2, 7.0, 6.8],
    }
    rows = []
    for sec, vals in sectores.items():
        for i, anio in enumerate(ANIOS):
            rows.append({"anio": anio, "sector": sec, "mt_co2": vals[i]})
    return pd.DataFrame(rows)


# ── Consumo por departamento (GWh) ────────────────────────────────────────────
@st.cache_data
def gen_consumo():
    deptos = {
        "Antioquia": 15800, "Bogotá D.C.": 14200, "Valle del Cauca": 11200,
        "Atlántico": 5600, "Cundinamarca": 4800, "Santander": 4400,
        "Bolívar": 3800, "Córdoba": 2900, "Meta": 2600, "Nariño": 2200,
        "Tolima": 2100, "Huila": 1900, "Cesar": 1800, "Cauca": 1700,
        "La Guajira": 1400, "Caldas": 1600, "Boyacá": 1500, "Magdalena": 1600,
        "Sucre": 1100, "N. Santander": 2000, "Casanare": 1200, "Risaralda": 1800,
        "Chocó": 480, "Quindío": 980, "Caquetá": 420, "Putumayo": 380,
        "Arauca": 310, "Vichada": 85, "Guainía": 60, "Vaupés": 55,
        "Amazonas": 70, "Guaviare": 140, "San Andrés": 250,
    }
    rows = []
    for dpto, base in deptos.items():
        for anio in ANIOS:
            factor = 1 + (anio - 2018) * 0.025 + np.random.normal(0, 0.01)
            rows.append({
                "departamento": dpto,
                "anio": anio,
                "consumo_gwh": round(base * factor, 1),
                "region": DEPT_REGION.get(dpto, "Otra"),
            })
    return pd.DataFrame(rows)


# ── Proyectos ERNC ────────────────────────────────────────────────────────────
@st.cache_data
def gen_proyectos():
    data = [
        # (nombre, tipo, depto, lat, lon, mw, estado, inversion_musd, empleos, anio)
        ("Windpeshi",       "Eólica",   "La Guajira",   11.8,-72.5, 204,"Operativo", 280,450,2022),
        ("Jepírachi II",    "Eólica",   "La Guajira",   11.7,-72.4, 198,"Operativo", 260,420,2022),
        ("Alta Guajira I",  "Eólica",   "La Guajira",   11.9,-72.6, 300,"En Constr.", 390,600,2024),
        ("Alta Guajira II", "Eólica",   "La Guajira",   11.85,-72.5,250,"Radicado",  320,500,2025),
        ("Guajira Wind 3",  "Eólica",   "La Guajira",   12.0,-72.3, 350,"Radicado",  450,700,2026),
        ("LATAM Solar Loma","Solar",    "Cesar",        10.4,-73.3, 150,"Operativo", 185,280,2023),
        ("Portón del Sol",  "Solar",    "Caldas",        5.5,-74.7, 102,"Operativo", 130,210,2023),
        ("Solar La Unión",  "Solar",    "Córdoba",       8.2,-75.8, 100,"Operativo", 128,195,2023),
        ("Sol del Norte",   "Solar",    "Magdalena",    10.8,-74.0, 180,"En Constr.", 225,350,2024),
        ("Atalaya Solar",   "Solar",    "Tolima",        4.8,-75.0, 120,"Operativo", 152,240,2023),
        ("Termoflores",     "Solar",    "Atlántico",    10.9,-74.8,  80,"Operativo",  98,160,2022),
        ("Gaia Solar",      "Solar",    "Antioquia",     6.8,-75.2,  95,"En Constr.", 118,190,2024),
        ("Caribbean Wind",  "Eólica",   "Atlántico",    11.0,-74.9, 120,"Radicado",  155,250,2025),
        ("Ituango",  "Hidroeléctrica",  "Antioquia",     7.2,-75.7,2400,"En Constr.",3500,4500,2025),
        ("El Quimbo","Hidroeléctrica",  "Huila",         2.5,-75.5, 400,"Operativo", 840,1200,2019),
        ("Sogamoso", "Hidroeléctrica",  "Santander",     6.9,-73.8, 820,"Operativo",1200,1800,2019),
        ("ZNI Chocó",       "Solar",    "Chocó",         5.7,-76.6,  15,"Operativo",  22, 40,2022),
        ("ZNI Guainía",     "Solar",    "Guainía",       3.8,-67.9,  8, "Operativo",  12, 25,2023),
        ("ZNI Vaupés",      "Solar",    "Vaupés",        1.2,-70.2,  6, "En Constr.", 10, 20,2024),
        ("Biomasa Llanos",  "Biomasa",  "Meta",          4.1,-73.6,  80,"Operativo",  95,180,2021),
        ("Biogas Córdoba",  "Biomasa",  "Córdoba",       8.1,-75.9,  40,"Operativo",  52, 90,2022),
        ("Pacific Wind",    "Eólica",   "Nariño",        1.8,-77.0, 160,"Radicado",  210,330,2025),
        ("Solar Caribe 2",  "Solar",    "Bolívar",       9.5,-75.4, 200,"En Constr.", 248,380,2024),
        ("Solar Orinoquia", "Solar",    "Casanare",      5.5,-72.5, 140,"Radicado",  178,270,2026),
        ("Geo Nevado",   "Geotérmica",  "Caldas",        5.1,-75.4,  50,"Radicado",  180, 80,2026),
    ]
    cols = ["nombre","tipo","departamento","lat","lon","capacidad_mw",
            "estado","inversion_musd","empleos","anio_fpo"]
    df = pd.DataFrame(data, columns=cols)
    df["region"] = df["departamento"].map(DEPT_REGION).fillna("Otra")
    return df


# ── ZNI — Zonas No Interconectadas ────────────────────────────────────────────
@st.cache_data
def gen_zni():
    data = [
        ("Nuquí",       "Chocó",    "Pacífica",    5.71,-77.27, 8500, 12, True,  False),
        ("Bahía Solano","Chocó",    "Pacífica",    6.22,-77.40, 9200, 14, True,  True),
        ("Acandí",      "Chocó",    "Pacífica",    8.52,-77.29, 4800,  8, True,  False),
        ("Mituú",       "Vaupés",   "Amazónica",   1.25,-70.23, 5200, 10, True,  True),
        ("Puerto Inírida","Guainía", "Amazónica",   3.86,-67.92,19000, 16, True,  True),
        ("Leticia",     "Amazonas", "Amazónica",  -4.21,-69.94,42000, 22, True,  True),
        ("Puerto Carreño","Vichada", "Orinoquía",   6.19,-67.49,16000, 14, True,  False),
        ("San José Guav.","Guaviare","Amazónica",   2.58,-72.64,55000, 20, True,  True),
        ("La Pedrera",  "Amazonas", "Amazónica",  -1.32,-69.58, 2800,  8, False, False),
        ("Tarapacá",    "Amazonas", "Amazónica",  -2.87,-69.74, 3400,  8, False, False),
        ("Puerto Leguíz.","Putumayo","Amazónica",   0.19,-74.77, 8500, 12, False, False),
        ("Mocoa Rural", "Putumayo", "Amazónica",   1.15,-76.65, 4200,  8, False, False),
    ]
    cols=["zona","departamento","region","lat","lon","poblacion",
          "horas_dia","con_servicio","tiene_proyecto"]
    return pd.DataFrame(data, columns=cols)


# ── Carga de datos ────────────────────────────────────────────────────────────
df_cap   = gen_capacidad()
df_emis  = gen_emisiones()
df_cons  = gen_consumo()
df_proy  = gen_proyectos()
df_zni   = gen_zni()


# ══════════════════════════════════════════════════════════════════════════════
# 3 · FUNCIONES DE COMPONENTES UI
# ══════════════════════════════════════════════════════════════════════════════

def plotly_base(height=360, **kwargs):
    """Layout base Plotly para todos los gráficos del sistema."""
    base = dict(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = P["surface"],
        font = dict(family="Barlow, sans-serif",
                    color=P["text_mid"], size=11),
        margin = dict(l=44, r=20, t=48, b=40),
        height = height,
        xaxis = dict(
            gridcolor     = P["grid"],
            zerolinecolor = P["rim"],
            linecolor     = P["rim"],
            tickfont      = dict(
                family="JetBrains Mono, monospace",
                color=P["text_lo"], size=9),
        ),
        yaxis = dict(
            gridcolor     = P["grid"],
            zerolinecolor = P["rim"],
            linecolor     = P["rim"],
            tickfont      = dict(
                family="JetBrains Mono, monospace",
                color=P["text_lo"], size=9),
        ),
        legend = dict(
            bgcolor     = "rgba(6,13,26,0.90)",
            bordercolor = P["rim"],
            borderwidth = 1,
            font        = dict(size=10, color=P["text_mid"],
                               family="Barlow, sans-serif"),
        ),
        hoverlabel = dict(
            bgcolor    = "#040C1A",
            bordercolor= P["neon_dim"],
            font       = dict(color=P["text_hi"], size=12,
                              family="Barlow, sans-serif"),
        ),
        title = dict(
            font = dict(size=13, color=P["ice"],
                        family="Barlow Condensed, sans-serif"),
            x = 0.01, y = 0.97,
        ),
        modebar = dict(
            bgcolor     = "rgba(0,0,0,0)",
            color       = P["text_lo"],
            activecolor = P["neon"],
        ),
    )
    base.update(kwargs)
    return base


def neon_header(icon, title, subtitle="", badge="", badge_col=""):
    """Header de sección estilo sala de control."""
    badge_col = badge_col or P["neon"]
    badge_html = (
        f'<span style="background:{_ca(badge_col,"1A")};color:{badge_col};'
        f'border:1px solid {_ca(badge_col,"44")};border-radius:3px;'
        f'padding:2px 8px;font-size:9px;letter-spacing:2px;'
        f'font-family:JetBrains Mono,monospace;font-weight:500;'
        f'vertical-align:middle;margin-left:12px;">{badge.upper()}</span>'
    ) if badge else ""
    sub = (
        f'<div style="color:{P["text_lo"]};font-size:11px;margin-top:4px;'
        f'font-family:JetBrains Mono,monospace;letter-spacing:.8px;">'
        f'{subtitle}</div>'
    ) if subtitle else ""
    return f"""
<div style="
    background: linear-gradient(135deg, {P['surface']} 0%, {P['raised']} 100%);
    padding: 18px 24px;
    border-radius: 10px;
    border: 1px solid {P['rim']};
    border-left: 3px solid {P['neon']};
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;">
  <div style="
      position:absolute;right:0;top:0;width:200px;height:100%;
      background:radial-gradient(rgba(0,255,157,0.04),transparent 70%);
      pointer-events:none;"></div>
  <div style="display:flex;align-items:center;gap:14px;position:relative;">
    <div style="
        background:{P['glass']};border:1px solid {P['rimhi']};
        border-radius:8px;padding:10px;
        filter:drop-shadow(0 0 10px {P['neon_glow']});
        font-size:22px;line-height:1;">{icon}</div>
    <div>
      <div style="
          color:{P['text_hi']};
          font-family:'Barlow Condensed',sans-serif;
          font-size:19px;font-weight:700;letter-spacing:.5px;
          text-transform:uppercase;line-height:1.2;">{title}{badge_html}</div>
      {sub}
    </div>
  </div>
</div>"""


def kpi_card(label, value, unit, icon, delta_pct, sparkline_data,
             color=None, description=""):
    """Tarjeta KPI premium — sparkline CSS puro, sin SVG."""
    color = color or P["neon"]
    delta_color = P["neon"] if delta_pct >= 0 else P["alert"]
    delta_arrow = "▲" if delta_pct >= 0 else "▼"
    delta_sign  = "+" if delta_pct >= 0 else ""

    # Sparkline como barras CSS (sin SVG, compatible con Streamlit)
    mn, mx = min(sparkline_data), max(sparkline_data)
    rng = mx - mn if mx != mn else 1
    bars = ""
    for v in sparkline_data:
        h = max(4, int(((v - mn) / rng) * 24) + 4)
        bars += (
            f'<div style="width:4px;height:{h}px;'
            f'background:{color};border-radius:2px 2px 0 0;'
            f'opacity:0.7;align-self:flex-end;"></div>'
        )
    spark = (
        f'<div style="display:flex;align-items:flex-end;gap:2px;'
        f'height:28px;padding-top:4px;">{bars}</div>'
    )

    h = color.lstrip("#")
    r_c, g_c, b_c = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

    return (
        f'<div style="background:linear-gradient(145deg,{P["raised"]} 0%,{P["surface"]} 100%);'
        f'border:1px solid {P["rim"]};border-top:2px solid {color};'
        f'border-radius:10px;padding:16px;position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:-20px;right:-20px;width:80px;height:80px;'
        f'border-radius:50%;background:radial-gradient(rgba({r_c},{g_c},{b_c},0.12),'
        f'transparent 70%);pointer-events:none;"></div>'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:flex-start;margin-bottom:10px;">'
        f'<div style="background:{P["glass"]};border:1px solid {P["rimhi"]};'
        f'border-radius:7px;padding:8px;font-size:18px;line-height:1;'
        f'box-shadow:0 0 12px rgba({r_c},{g_c},{b_c},0.19);">{icon}</div>'
        f'<div style="opacity:.85;">{spark}</div>'
        f'</div>'
        f'<div style="color:{color};font-family:Barlow Condensed,sans-serif;'
        f'font-size:26px;font-weight:800;line-height:1;'
        f'text-shadow:0 0 16px rgba({r_c},{g_c},{b_c},0.31);'
        f'margin-bottom:3px;">{value}</div>'
        f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;'
        f'font-size:8px;letter-spacing:1.5px;text-transform:uppercase;'
        f'margin-bottom:8px;">{unit}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'border-top:1px solid {P["rim"]};padding-top:8px;">'
        f'<span style="color:{P["text_mid"]};font-size:11px;">{label}</span>'
        f'<span style="color:{delta_color};font-size:10px;font-weight:600;'
        f'font-family:JetBrains Mono,monospace;">'
        f'{delta_arrow} {delta_sign}{delta_pct:.1f}%</span>'
        f'</div></div>'
    )



def alert_chip(title, body, level="warn"):
    """Chip de alerta de sistema con niveles."""
    cfg = {
        "crit": (P["alert"],   "🔴", P["alert_glow"]),
        "warn": (P["amber"],   "🟡", P["amber_glow"]),
        "info": (P["ice"],     "🔵", P["ice_glow"]),
        "good": (P["neon"],    "🟢", P["neon_glow"]),
    }
    color, dot, glow = cfg.get(level, cfg["info"])
    return f"""
<div style="
    background: linear-gradient(135deg, {glow}, {P['surface']});
    border: 1px solid {_ca(color,'30')};
    border-left: 3px solid {color};
    border-radius: 8px;
    padding: 12px 14px;
    margin: 5px 0;
    position: relative;
    overflow: hidden;">
  <div style="
      position:absolute;right:10px;top:50%;transform:translateY(-50%);
      font-size:28px;opacity:.08;">{dot}</div>
  <div style="
      display:flex;align-items:center;gap:8px;margin-bottom:4px;">
    <span style="font-size:11px;">{dot}</span>
    <span style="
        color:{color};
        font-family:'Barlow Condensed',sans-serif;
        font-size:13px;font-weight:700;letter-spacing:.5px;
        text-transform:uppercase;">{title}</span>
  </div>
  <div style="
      color:{P['text_mid']};font-size:11px;
      line-height:1.6;margin-left:19px;">{body}</div>
</div>"""


def data_label(key, value, color=None):
    """Etiqueta de dato técnico estilo monospace."""
    color = color or P["neon"]
    return f"""<span style="
        font-family:'JetBrains Mono',monospace;font-size:10px;">
      <span style="color:{P['text_lo']};letter-spacing:1px;">{key.upper()} </span>
      <span style="color:{color};font-weight:500;">▸ {value}</span>
    </span>"""


def section_rule(label=""):
    if label:
        return f"""
<div style="display:flex;align-items:center;gap:12px;margin:18px 0 12px;">
  <div style="flex:1;height:1px;background:linear-gradient(
      90deg,transparent,{P['rim']});"></div>
  <span style="
      color:{P['text_lo']};
      font-family:'JetBrains Mono',monospace;
      font-size:9px;letter-spacing:2.5px;
      text-transform:uppercase;">{label}</span>
  <div style="flex:1;height:1px;background:linear-gradient(
      90deg,{P['rim']},transparent);"></div>
</div>"""
    return f'<div style="height:1px;background:{P["rim"]};margin:16px 0;"></div>'


# ══════════════════════════════════════════════════════════════════════════════
# 4 · SIDEBAR — Panel de Control
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Logotipo ──────────────────────────────────────────────────────────────
    _neon   = P["neon"]
    _dim    = P["neon_dim"]
    _glass  = P["glass"]
    _thi    = P["text_hi"]
    _tlo    = P["text_lo"]
    _tmd    = P["text_mid"]
    _surf   = P["surface"]
    _rim    = P["rim"]
    _bdr    = P["border"] if "border" in P else P["rim"]

    st.markdown(
        "<div style='text-align:center;padding:16px 0 10px;'>"
        f"<div style='font-size:38px;line-height:1;margin-bottom:10px;'>"
        "&#9889;</div>"
        f"<div style='color:{_thi};font-family:Barlow Condensed,sans-serif;"
        "font-size:15px;font-weight:800;letter-spacing:2px;"
        "text-transform:uppercase;line-height:1.25;'>SITEN &middot; Colombia</div>"
        f"<div style='color:{_dim};font-family:JetBrains Mono,monospace;"
        "font-size:9px;letter-spacing:3px;margin-top:3px;'>"
        "SISTEMA INTELIGENCIA ENERG&Eacute;TICA</div>"
        f"<div style='display:inline-flex;align-items:center;gap:5px;"
        f"margin-top:8px;background:{_glass};border:1px solid {_dim};"
        "border-radius:20px;padding:3px 10px;'>"
        f"<div style='width:6px;height:6px;border-radius:50%;"
        f"background:{_neon};'></div>"
        f"<span style='color:{_neon};font-family:JetBrains Mono,monospace;"
        "font-size:8px;letter-spacing:1.5px;'>EN L&Iacute;NEA &middot; 2026"
        "</span></div></div>"
        f"<div style='height:1px;background:{_rim};margin:8px 0 14px;'></div>",
        unsafe_allow_html=True,
    )

    # ── Filtros ───────────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='color:{_tlo};font-family:JetBrains Mono,monospace;"
        "font-size:9px;letter-spacing:2px;margin-bottom:6px;'>"
        "FILTROS DEL SISTEMA</div>",
        unsafe_allow_html=True,
    )

    todos_deptos = sorted(df_cons["departamento"].unique().tolist())
    sel_deptos   = st.multiselect(
        "Departamento", todos_deptos, default=todos_deptos[:6], key="dep")

    tipos_energia = sorted(df_proy["tipo"].unique().tolist())
    sel_tipos     = st.multiselect(
        "Tipo de Energ\u00eda", tipos_energia, default=tipos_energia, key="tip")

    anio_sel = st.select_slider(
        "A\u00f1o de An\u00e1lisis", options=ANIOS, value=2025)

    estados = ["Operativo", "En Constr.", "Radicado"]
    sel_estados = st.multiselect(
        "Estado del Proyecto", estados, default=estados, key="est")

    st.markdown(section_rule("DATOS EN TIEMPO REAL"), unsafe_allow_html=True)

    # ── Indicadores del sidebar ───────────────────────────────────────────────
    total_cap_solar = df_cap[
        (df_cap["fuente"] == "Solar") &
        (df_cap["anio"]   == anio_sel)
    ]["capacidad_mw"].sum()
    total_proyectos = len(df_proy[df_proy["estado"].isin(sel_estados)])

    st.metric("Capacidad Solar Activa",
              f"{total_cap_solar:,.0f} MW",
              delta=f"+{total_cap_solar * 0.18:.0f} MW vs 2024")
    st.metric("Proyectos Monitoreados",
              total_proyectos,
              delta=f"+{int(total_proyectos * 0.12)} nuevos")

    st.markdown(
        f"<div style='margin-top:12px;padding:10px;background:{_surf};"
        f"border:1px solid {_rim};border-radius:8px;'>"
        f"<div style='color:{_tlo};font-family:JetBrains Mono,monospace;"
        "font-size:8px;letter-spacing:2px;margin-bottom:8px;'>"
        "FUENTES DE DATOS</div>"
        f"<div style='color:{_tmd};font-size:10px;line-height:2;'>"
        f"<span style='color:{_dim};'>&#9658;</span> UPME &mdash; Plan 6GW+<br>"
        f"<span style='color:{_dim};'>&#9658;</span> IPSE &mdash; Cobertura ZNI<br>"
        f"<span style='color:{_dim};'>&#9658;</span> IDEAM &mdash; Inventario GEI<br>"
        f"<span style='color:{_dim};'>&#9658;</span> DANE &mdash; DIVIPOLA<br>"
        f"<span style='color:{_dim};'>&#9658;</span> XM &mdash; Despacho SIN"
        "</div></div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# 5 · HEADER PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

# ── Header principal — string concatenado (máxima compatibilidad Streamlit) ──
_h_bg   = f"linear-gradient(135deg,{P['deep']} 0%,{P['surface']} 40%,{P['raised']} 70%,{P['deep']} 100%)"
_h_line = f"linear-gradient(90deg,transparent 0%,{P['neon']} 30%,{P['ice']} 70%,transparent 100%)"
_header_html = (
    f"<div style='background:{_h_bg};padding:28px 32px;border-radius:14px;"
    f"border:1px solid {P['rim']};margin-bottom:20px;position:relative;overflow:hidden;'>"
    f"<div style='position:absolute;top:0;left:0;right:0;height:2px;"
    f"background:{_h_line};box-shadow:0 0 12px rgba(0,255,157,0.4);'></div>"
    "<div style='position:relative;display:flex;align-items:center;"
    "justify-content:space-between;flex-wrap:wrap;'>"
    "<div>"
    f"<div style='display:inline-flex;align-items:center;gap:8px;"
    f"background:{P['glass']};border:1px solid rgba(0,255,157,0.2);"
    "border-radius:4px;padding:3px 10px;margin-bottom:12px;'>"
    f"<div style='width:6px;height:6px;border-radius:50%;"
    f"background:{P['neon']};box-shadow:0 0 8px {P['neon']};'></div>"
    f"<span style='color:{P['neon']};font-family:JetBrains Mono,monospace;"
    "font-size:9px;letter-spacing:2px;'>"
    "SISTEMA ACTIVO &middot; ACTUALIZACI&Oacute;N EN TIEMPO REAL</span></div>"
    f"<h1 style='color:{P['text_hi']};font-family:Barlow Condensed,sans-serif;"
    "font-size:30px;font-weight:800;letter-spacing:1px;text-transform:uppercase;"
    "margin:0 0 8px;line-height:1.1;'>"
    "Dashboard Nacional de<br>"
    f"<span style='color:{P['neon']};text-shadow:0 0 20px rgba(0,255,157,0.4);'>"
    "Transici&oacute;n Energ&eacute;tica</span>"
    f"<span style='color:{P['text_mid']};'> &mdash; Colombia 2026</span></h1>"
    f"<p style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
    "font-size:10px;letter-spacing:1px;margin:0;'>"
    "MONITOREO ESTRAT&Eacute;GICO &nbsp;&middot;&nbsp; "
    "ENERG&Iacute;AS RENOVABLES &nbsp;&middot;&nbsp; "
    "DESCARBONIZACI&Oacute;N &nbsp;&middot;&nbsp; COBERTURA NACIONAL</p>"
    "</div>"
    "<div style='display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;'>"
    f"<div style='text-align:center;padding:12px 18px;background:{P['glass']};"
    "border:1px solid rgba(0,255,157,0.2);border-radius:8px;'>"
    f"<div style='color:{P['neon']};font-family:Barlow Condensed,sans-serif;"
    "font-size:28px;font-weight:800;text-shadow:0 0 16px rgba(0,255,157,0.4);'>9%</div>"
    f"<div style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
    "font-size:8px;letter-spacing:1.5px;'>FNCER / SIN</div></div>"
    f"<div style='text-align:center;padding:12px 18px;background:{P['glass']};"
    "border:1px solid rgba(255,176,32,0.2);border-radius:8px;'>"
    f"<div style='color:{P['amber']};font-family:Barlow Condensed,sans-serif;"
    "font-size:28px;font-weight:800;'>+187%</div>"
    f"<div style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
    "font-size:8px;letter-spacing:1.5px;'>SOLAR 2024</div></div>"
    f"<div style='text-align:center;padding:12px 18px;background:{P['glass']};"
    "border:1px solid rgba(0,229,255,0.2);border-radius:8px;'>"
    f"<div style='color:{P['ice']};font-family:Barlow Condensed,sans-serif;"
    "font-size:28px;font-weight:800;'>80%</div>"
    f"<div style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
    "font-size:8px;letter-spacing:1.5px;'>META PND 2026</div></div>"
    "</div></div></div>"
)
st.markdown(_header_html, unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# 6 · KPI STRIP — 6 Tarjetas con sparkline
# ══════════════════════════════════════════════════════════════════════════════
anio_idx = ANIOS.index(anio_sel)

kpi_defs = [
    {
        "label":  "Capacidad Solar",
        "value":  f"{df_cap[(df_cap['fuente']=='Solar')&(df_cap['anio']==anio_sel)]['capacidad_mw'].values[0]:,.0f}",
        "unit":   "MW instalados",
        "icon":   "☀️",
        "color":  P["amber"],
        "delta":  +187.3,
        "spark":  df_cap[df_cap['fuente']=='Solar']['capacidad_mw'].tolist()[:anio_idx+1],
    },
    {
        "label":  "Capacidad Eólica",
        "value":  f"{df_cap[(df_cap['fuente']=='Eólica')&(df_cap['anio']==anio_sel)]['capacidad_mw'].values[0]:,.0f}",
        "unit":   "MW instalados",
        "icon":   "💨",
        "color":  P["ice"],
        "delta":  +62.8,
        "spark":  df_cap[df_cap['fuente']=='Eólica']['capacidad_mw'].tolist()[:anio_idx+1],
    },
    {
        "label":  "Reducción CO₂",
        "value":  "12.4",
        "unit":   "Mt evitadas/año",
        "icon":   "🌿",
        "color":  P["neon"],
        "delta":  +8.6,
        "spark":  [4.2,5.1,6.3,7.8,9.2,10.8,12.4,12.4,12.4][:anio_idx+1],
    },
    {
        "label":  "Cobertura Nacional",
        "value":  "97.8",
        "unit":   "% hogares electrificados",
        "icon":   "⚡",
        "color":  P["neon"],
        "delta":  +1.2,
        "spark":  [94.2,94.8,95.3,95.9,96.5,97.0,97.4,97.8,97.8][:anio_idx+1],
    },
    {
        "label":  "Inversión ERNC",
        "value":  "USD 4.8B",
        "unit":   "acumulada 2022-2026",
        "icon":   "💰",
        "color":  P["amber"],
        "delta":  +34.0,
        "spark":  [0.4,0.6,0.9,1.4,2.1,3.1,4.1,4.8,4.8][:anio_idx+1],
    },
    {
        "label":  "Proyectos Activos",
        "value":  f"{len(df_proy[df_proy['estado'].isin(['Operativo','En Constr.'])])}",
        "unit":   "plan 6GW+",
        "icon":   "🏗",
        "color":  P["ice"],
        "delta":  +18.5,
        "spark":  [8,12,18,24,34,42,52,62,62][:anio_idx+1],
    },
]

kpi_cols = st.columns(6)
for col, kd in zip(kpi_cols, kpi_defs):
    col.markdown(
        kpi_card(kd["label"], kd["value"], kd["unit"],
                 kd["icon"], kd["delta"], kd["spark"], kd["color"]),
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin:14px 0;'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 7 · TABS PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "▸ PANORAMA ENERGÉTICO",
    "▸ MAPA NACIONAL",
    "▸ PROYECTOS",
    "▸ EMISIONES CO₂",
    "▸ CONSUMO",
    "▸ ALERTAS",
    "▸ IA PREDICTIVA",
    "▸ ZONAS ZNI",
    "▸ COMPARATIVO",
    "▸ FNCER 2025",
    "▸ DATOS",
])


# ──────────────────────────────────────────────────────────────────────────────
# TAB 0 · PANORAMA ENERGÉTICO
# ──────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown(neon_header(
        "⚡", "Panorama de la Matriz Energética Nacional",
        subtitle="capacidad instalada · evolución histórica · mix de generación",
        badge="SIN · 2018-2026",
    ), unsafe_allow_html=True)

    row1_l, row1_r = st.columns([1.6, 1])

    # ── Gráfico área apilada — evolución capacidad por fuente ─────────────────
    with row1_l:
        cap_piv = df_cap.pivot(
            index="anio", columns="fuente", values="capacidad_mw").fillna(0)
        fuentes_orden = ["Solar","Eólica","Biomasa","Hidroeléctrica",
                         "Gas Natural","Carbón"]

        fig_area = go.Figure()
        colors_area = [P["amber"], P["ice"], "#66BB6A",
                       P["neon"], "#FF7043", "#78909C"]

        for fuente, color in zip(fuentes_orden, colors_area):
            if fuente not in cap_piv.columns:
                continue
            fig_area.add_trace(go.Scatter(
                x=cap_piv.index,
                y=cap_piv[fuente],
                name=fuente,
                mode="lines",
                fill="tonexty",
                line=dict(color=color, width=1.5),
                fillcolor=(lambda h: f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},0.28)")(color.lstrip("#")),
                stackgroup="one",
                hovertemplate=(
                    f"<b>{fuente}</b><br>%{{x}}: "
                    f"%{{y:,.0f}} MW<extra></extra>"
                ),
            ))

        # Línea de meta PND
        fig_area.add_hline(
            y=2297, line_dash="dot", line_color=P["neon"],
            line_width=1.5,
            annotation_text="META PND 2026: 2.297 MW FNCER",
            annotation_font=dict(color=P["neon"], size=10,
                                 family="JetBrains Mono, monospace"),
        )

        fig_area.update_layout(**plotly_base(
            height=360,
            title_text="CAPACIDAD INSTALADA (MW) · EVOLUCIÓN 2018-2026",
            hovermode="x unified",
            xaxis_title="AÑO",
            yaxis_title="CAPACIDAD (MW)",
        ))
        st.plotly_chart(fig_area, use_container_width=True)

    # ── Donut matrix energética ───────────────────────────────────────────────
    with row1_r:
        cap_anio = df_cap[df_cap["anio"] == anio_sel].copy()
        total_mw = cap_anio["capacidad_mw"].sum()

        # Agrupar en Renovable vs Convencional
        cap_anio["categoria"] = cap_anio["fuente"].map({
            "Solar": "Renovable FNCER",
            "Eólica": "Renovable FNCER",
            "Biomasa": "Renovable FNCER",
            "Geotérmica": "Renovable FNCER",
            "Hidroeléctrica": "Renovable Hídrica",
            "Gas Natural": "Convencional",
            "Carbón": "Convencional",
        }).fillna("Otro")

        # Donut por fuente
        fuentes_anio = cap_anio.groupby("fuente")["capacidad_mw"].sum().reset_index()
        fuentes_anio = fuentes_anio.sort_values("capacidad_mw", ascending=False)

        pct_renov = (
            cap_anio[cap_anio["categoria"].str.contains("Renovable")]
            ["capacidad_mw"].sum() / total_mw * 100
        )

        fig_donut = go.Figure(go.Pie(
            labels=fuentes_anio["fuente"],
            values=fuentes_anio["capacidad_mw"],
            hole=0.68,
            marker=dict(
                colors=[ENERGY_COLORS.get(f, P["text_lo"])
                        for f in fuentes_anio["fuente"]],
                line=dict(color=P["void"], width=2),
            ),
            textinfo="percent",
            textfont=dict(size=9, family="JetBrains Mono, monospace"),
            hovertemplate=(
                "<b>%{label}</b><br>%{value:,.0f} MW<br>%{percent}"
                "<extra></extra>"
            ),
        ))
        fig_donut.add_annotation(
            text=f"<b>{pct_renov:.0f}%</b>",
            x=0.5, y=0.56,
            font=dict(size=28, color=P["neon"],
                      family="Barlow Condensed, sans-serif"),
            showarrow=False,
        )
        fig_donut.add_annotation(
            text="RENOVABLE",
            x=0.5, y=0.42,
            font=dict(size=9, color=P["text_lo"],
                      family="JetBrains Mono, monospace"),
            showarrow=False,
        )
        fig_donut.update_layout(**plotly_base(
            height=360,
            title_text=f"MIX ENERGÉTICO {anio_sel}",
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5,
                        font=dict(size=9)),
        ))
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── Fila 2: Barras departamento + CAGR ────────────────────────────────────
    st.markdown(section_rule("ANÁLISIS DEPARTAMENTAL"), unsafe_allow_html=True)
    row2_l, row2_r = st.columns([1.3, 0.7])

    with row2_l:
        cons_anio = df_cons[df_cons["anio"] == anio_sel].copy()
        if sel_deptos:
            cons_sel = cons_anio[cons_anio["departamento"].isin(sel_deptos)]
        else:
            cons_sel = cons_anio.nlargest(10, "consumo_gwh")

        cons_sel = cons_sel.sort_values("consumo_gwh", ascending=True)
        colors_dept = [
            REGION_COLORS.get(r, P["text_lo"])
            for r in cons_sel["region"]
        ]

        fig_bar = go.Figure(go.Bar(
            x=cons_sel["consumo_gwh"],
            y=cons_sel["departamento"],
            orientation="h",
            marker=dict(
                color=colors_dept,
                opacity=0.85,
                line=dict(color=P["void"], width=0.5),
            ),
            text=[f"{v:,.0f} GWh" for v in cons_sel["consumo_gwh"]],
            textposition="outside",
            textfont=dict(size=9, color=P["text_lo"],
                          family="JetBrains Mono, monospace"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Consumo: %{x:,.0f} GWh<extra></extra>"
            ),
        ))
        fig_bar.update_layout(**plotly_base(
            height=340,
            title_text="CONSUMO ENERGÉTICO POR DEPARTAMENTO (GWh)",
            xaxis_title="CONSUMO (GWh)",
            yaxis=dict(automargin=True),
            plot_bgcolor=P["surface"],
        ))
        st.plotly_chart(fig_bar, use_container_width=True)

    with row2_r:
        # Bullet chart: FNCER vs Meta PND por región
        fncer_region = (df_proy[df_proy["estado"].isin(["Operativo","En Constr."])]
                        .groupby("region")["capacidad_mw"].sum()
                        .reset_index()
                        .sort_values("capacidad_mw", ascending=False))

        metas_region = {
            "Caribe":    1200, "Andina": 600,
            "Pacífica":  200,  "Orinoquía": 150, "Amazónica": 80,
        }

        fig_bullet = go.Figure()
        for i, row in fncer_region.iterrows():
            reg  = row["region"]
            real = row["capacidad_mw"]
            meta = metas_region.get(reg, 200)
            pct  = min(real / meta * 100, 100)
            col  = REGION_COLORS.get(reg, P["neon"])
            fig_bullet.add_trace(go.Bar(
                x=[real], y=[reg],
                orientation="h",
                marker_color=col,
                marker_opacity=0.85,
                name=reg,
                showlegend=False,
                width=0.5,
                hovertemplate=(
                    f"<b>{reg}</b><br>"
                    f"Capacidad: {real:,.0f} MW<br>"
                    f"Meta: {meta:,.0f} MW<br>"
                    f"Avance: {pct:.0f}%"
                    "<extra></extra>"
                ),
            ))
            # Línea de meta
            fig_bullet.add_shape(
                type="line", xref="x", yref="y",
                x0=meta, x1=meta,
                y0=i - 0.35, y1=i + 0.35,
                line=dict(color=P["text_mid"], width=2, dash="dot"),
            )

        fig_bullet.update_layout(**plotly_base(
            height=340,
            title_text="CAPACIDAD FNCER vs META PND (MW)",
            xaxis_title="MW",
            yaxis=dict(automargin=True),
        ))
        st.plotly_chart(fig_bullet, use_container_width=True)


    # ── Heatmap capacidad renovable departamento × año ────────────────────────
    st.markdown(section_rule("EVOLUCIÓN CAPACIDAD RENOVABLE · MAPA DE CALOR"), unsafe_allow_html=True)
    # df_proy tiene departamento + capacidad_mw + anio_fpo
    _proy_hm = df_proy[df_proy["tipo"].isin(["Solar","Eólica","Biomasa"])].copy()
    _proy_hm["anio"] = _proy_hm["anio_fpo"].fillna(2023).astype(int)
    cap_piv_hm = (_proy_hm.groupby(["departamento","anio"])["capacidad_mw"]
                  .sum().unstack(fill_value=0))
    top_deptos_hm = cap_piv_hm.max(axis=1).nlargest(14).index
    cap_piv_hm = cap_piv_hm.loc[top_deptos_hm]

    fig_hm_cap = go.Figure(go.Heatmap(
        z=cap_piv_hm.values,
        x=[str(int(a)) for a in cap_piv_hm.columns],
        y=cap_piv_hm.index.tolist(),
        colorscale=[
            [0.0, P["deep"]], [0.15, P["surface"]], [0.4, P["neon_dim"]],
            [0.7, P["neon"]], [1.0, P["amber"]],
        ],
        text=[[f"{v:,.0f}" if v > 0 else "" for v in row] for row in cap_piv_hm.values],
        texttemplate="%{text}",
        textfont=dict(size=8, color=P["void"], family="JetBrains Mono,monospace"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:,.0f} MW<extra></extra>",
        colorbar=dict(title=dict(text="MW",font=dict(color=P["text_mid"],size=10)),
                      tickfont=dict(color=P["text_lo"],size=9),thickness=12),
    ))
    fig_hm_cap.update_layout(**plotly_base(
        height=400,
        title_text="CAPACIDAD FNCER (MW) POR DEPARTAMENTO Y AÑO",
        xaxis_title="AÑO", yaxis_title="DEPARTAMENTO",
    ))
    st.plotly_chart(fig_hm_cap, use_container_width=True)

    # ── CAGR por fuente ────────────────────────────────────────────────────────
    st.markdown(section_rule("TASA DE CRECIMIENTO ANUAL COMPUESTO (CAGR)"), unsafe_allow_html=True)
    cagr_rows = []
    for fuente in df_cap["fuente"].unique():
        sub = df_cap[df_cap["fuente"]==fuente].sort_values("anio")
        if len(sub) >= 2:
            v0, vn = sub["capacidad_mw"].iloc[0], sub["capacidad_mw"].iloc[-1]
            n = sub["anio"].iloc[-1] - sub["anio"].iloc[0]
            if v0 > 0 and n > 0:
                cagr_rows.append({"fuente": fuente,
                                   "cagr": round((vn/v0)**(1/n)-1, 4)*100,
                                   "mw_actual": vn})
    cagr_df = pd.DataFrame(cagr_rows).sort_values("cagr", ascending=True)

    fig_cagr = go.Figure(go.Bar(
        x=cagr_df["cagr"], y=cagr_df["fuente"],
        orientation="h",
        marker=dict(
            color=[ENERGY_COLORS.get(f, P["text_lo"]) for f in cagr_df["fuente"]],
            opacity=0.88,
            line=dict(color=P["void"], width=0.5),
        ),
        text=[f"{v:+.1f}%" for v in cagr_df["cagr"]],
        textposition="outside",
        textfont=dict(size=10, color=P["text_mid"], family="JetBrains Mono,monospace"),
        customdata=cagr_df["mw_actual"].values,
        hovertemplate="<b>%{y}</b><br>CAGR: %{x:+.1f}%<br>MW actual: %{customdata:,.0f}<extra></extra>",
    ))
    fig_cagr.update_layout(**plotly_base(
        height=300, title_text="CAGR POR FUENTE ENERGÉTICA (PERÍODO COMPLETO)",
        xaxis_title="CAGR %", yaxis=dict(automargin=True),
    ))
    st.plotly_chart(fig_cagr, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 · MAPA NACIONAL
# ──────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown(neon_header(
        "🗺", "Mapa Nacional de Infraestructura Energética",
        subtitle="proyectos · zonas ZNI · hubs regionales",
        badge="GEORREFERENCIADO",
    ), unsafe_allow_html=True)

    # ── Controles del mapa ────────────────────────────────────────────────────
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        mostrar_tipos = st.multiselect(
            "Tipo de proyecto", tipos_energia, default=tipos_energia, key="mapa_t")
    with mc2:
        mostrar_estados = st.multiselect(
            "Estado", estados, default=estados, key="mapa_e")
    with mc3:
        mostrar_zni = st.checkbox("Mostrar Zonas ZNI", value=True)

    df_p_map = df_proy[
        (df_proy["tipo"].isin(mostrar_tipos)) &
        (df_proy["estado"].isin(mostrar_estados))
    ].copy()

    # ── Mapa Plotly Scattergeo ────────────────────────────────────────────────
    # Usar Scattermapbox para mapa interactivo y moderno
    tipo_cfg = {
        "Solar":          (P["amber"],   "★", 14),
        "Eólica":         (P["ice"],     "▲", 13),
        "Hidroeléctrica": (P["neon"],    "◆", 15),
        "Biomasa":        ("#66BB6A",    "●", 11),
        "Geotérmica":     ("#CE93D8",    "✦", 11),
    }

    fig_map = go.Figure()

    # Capa proyectos
    for tipo in df_p_map["tipo"].unique():
        sub = df_p_map[df_p_map["tipo"] == tipo]
        cfg = tipo_cfg.get(tipo, (P["text_mid"], "●", 10))

        fig_map.add_trace(go.Scattergeo(
            lat=sub["lat"], lon=sub["lon"],
            mode="markers+text",
            marker=dict(
                size=sub["capacidad_mw"].apply(
                    lambda x: max(8, min(28, x / 80))),
                color=cfg[0],
                opacity=0.85,
                line=dict(color=P["void"], width=1),
                symbol="circle",
            ),
            text=sub["nombre"],
            textposition="top center",
            textfont=dict(size=7, color=P["text_lo"],
                          family="JetBrains Mono, monospace"),
            name=tipo,
            customdata=sub[["estado","capacidad_mw",
                            "inversion_musd","empleos","departamento"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Departamento: %{customdata[4]}<br>"
                "Capacidad: <b>%{customdata[1]:,.0f} MW</b><br>"
                "Estado: %{customdata[0]}<br>"
                "Inversión: USD %{customdata[2]:,.0f}M<br>"
                "Empleos: %{customdata[3]:,}"
                "<extra></extra>"
            ),
        ))

    # Capa ZNI
    if mostrar_zni:
        fig_map.add_trace(go.Scattergeo(
            lat=df_zni["lat"], lon=df_zni["lon"],
            mode="markers",
            marker=dict(
                size=df_zni["poblacion"].apply(
                    lambda x: max(7, min(18, x / 3000))),
                color=[P["neon"] if c else P["alert"]
                       for c in df_zni["con_servicio"]],
                symbol="square",
                opacity=0.7,
                line=dict(color=P["void"], width=0.5),
            ),
            name="ZNI",
            customdata=df_zni[["zona","poblacion","horas_dia",
                               "con_servicio","tiene_proyecto"]].values,
            hovertemplate=(
                "<b>ZNI: %{customdata[0]}</b><br>"
                "Población: %{customdata[1]:,}<br>"
                "Horas/día: %{customdata[2]}<br>"
                "Con servicio: %{customdata[3]}<br>"
                "Proyecto asignado: %{customdata[4]}"
                "<extra></extra>"
            ),
        ))

    fig_map.update_layout(
        height=580,
        paper_bgcolor = P["void"],
        plot_bgcolor  = P["void"],
        font=dict(family="JetBrains Mono, monospace",
                  color=P["text_mid"], size=10),
        title=dict(
            text="INFRAESTRUCTURA ENERGÉTICA NACIONAL · COLOMBIA",
            font=dict(size=13, color=P["ice"],
                      family="Barlow Condensed, sans-serif"),
            x=0.01,
        ),
        geo=dict(
            fitbounds="locations",
            visible=False,
            bgcolor=P["void"],
            showframe=False,
            showcoastlines=False,
            showland=True,
            landcolor="#0A1628",
            showocean=True,
            oceancolor="#040810",
            showlakes=True,
            lakecolor="#071220",
            showcountries=True,
            countrycolor=P["rim"],
            showsubunits=True,
            subunitcolor=P["grid"],
            resolution=50,
        ),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(4,8,16,0.88)",
            bordercolor=P["rim"],
            borderwidth=1,
            font=dict(size=10, family="Barlow, sans-serif"),
        ),
        hoverlabel=dict(
            bgcolor="#030810",
            bordercolor=P["neon_dim"],
            font=dict(color=P["text_hi"], size=11),
        ),
        margin=dict(l=0, r=0, t=44, b=0),
        modebar=dict(bgcolor="rgba(0,0,0,0)",
                     color=P["text_lo"], activecolor=P["neon"]),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Estadísticas del mapa ─────────────────────────────────────────────────
    mc_s1, mc_s2, mc_s3, mc_s4 = st.columns(4)
    mc_s1.markdown(
        f'<div style="background:{P["surface"]};border:1px solid {P["rim"]};'
        f'border-top:2px solid {P["amber"]};border-radius:8px;padding:12px;'
        f'text-align:center;">'
        f'<div style="color:{P["amber"]};font-family:Barlow Condensed,sans-serif;'
        f'font-size:22px;font-weight:800;">'
        f'{len(df_p_map[df_p_map["tipo"]=="Solar"])}</div>'
        f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;'
        f'font-size:9px;letter-spacing:1px;">PARQUES SOLARES</div></div>',
        unsafe_allow_html=True)
    mc_s2.markdown(
        f'<div style="background:{P["surface"]};border:1px solid {P["rim"]};'
        f'border-top:2px solid {P["ice"]};border-radius:8px;padding:12px;'
        f'text-align:center;">'
        f'<div style="color:{P["ice"]};font-family:Barlow Condensed,sans-serif;'
        f'font-size:22px;font-weight:800;">'
        f'{len(df_p_map[df_p_map["tipo"]=="Eólica"])}</div>'
        f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;'
        f'font-size:9px;letter-spacing:1px;">PARQUES EÓLICOS</div></div>',
        unsafe_allow_html=True)
    mc_s3.markdown(
        f'<div style="background:{P["surface"]};border:1px solid {P["rim"]};'
        f'border-top:2px solid {P["neon"]};border-radius:8px;padding:12px;'
        f'text-align:center;">'
        f'<div style="color:{P["neon"]};font-family:Barlow Condensed,sans-serif;'
        f'font-size:22px;font-weight:800;">{len(df_zni)}</div>'
        f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;'
        f'font-size:9px;letter-spacing:1px;">ZONAS ZNI</div></div>',
        unsafe_allow_html=True)
    mc_s4.markdown(
        f'<div style="background:{P["surface"]};border:1px solid {P["rim"]};'
        f'border-top:2px solid {P["alert"]};border-radius:8px;padding:12px;'
        f'text-align:center;">'
        f'<div style="color:{P["alert"]};font-family:Barlow Condensed,sans-serif;'
        f'font-size:22px;font-weight:800;">'
        f'{int((df_zni["con_servicio"] == False).sum())}</div>'
        f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;'
        f'font-size:9px;letter-spacing:1px;">SIN PROYECTO</div></div>',
        unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 · PROYECTOS
# ──────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown(neon_header(
        "🏗", "Pipeline de Proyectos ERNC",
        subtitle="estado · capacidad · inversión · empleo",
        badge="PLAN 6GW+",
    ), unsafe_allow_html=True)

    df_p_fil = df_proy[
        (df_proy["tipo"].isin(sel_tipos)) &
        (df_proy["estado"].isin(sel_estados))
    ].copy()

    # KPIs rápidos de proyectos
    pq1, pq2, pq3, pq4, pq5 = st.columns(5)
    pq1.metric("Proyectos",     len(df_p_fil))
    pq2.metric("Capacidad",     f"{df_p_fil['capacidad_mw'].sum():,.0f} MW")
    pq3.metric("Inversión",     f"USD {df_p_fil['inversion_musd'].sum():,.0f}M")
    pq4.metric("Empleos",       f"{int(df_p_fil['empleos'].sum()):,}")
    pq5.metric("USD/MW prom.",
        f"{df_p_fil['inversion_musd'].sum()/df_p_fil['capacidad_mw'].sum()*1000:.0f}K"
        if df_p_fil["capacidad_mw"].sum() > 0 else "N/D")

    p_l, p_r = st.columns(2)

    with p_l:
        # Scatter capacidad vs inversión
        fig_scat = px.scatter(
            df_p_fil,
            x="capacidad_mw", y="inversion_musd",
            size="empleos", color="tipo",
            text="nombre",
            size_max=45,
            color_discrete_map=ENERGY_COLORS,
            labels={"capacidad_mw":"Capacidad (MW)",
                    "inversion_musd":"Inversión (MUSD)",
                    "tipo":"Tipo"},
            template="plotly_dark",
        )
        fig_scat.update_traces(
            textposition="top center",
            textfont=dict(size=7, color=P["text_lo"]),
            marker=dict(line=dict(color=P["void"], width=0.5)),
        )
        fig_scat.update_layout(**plotly_base(
            height=380,
            title_text="CAPACIDAD (MW) vs INVERSIÓN (MUSD) · TAMAÑO = EMPLEOS",
            xaxis_title="CAPACIDAD (MW)",
            yaxis_title="INVERSIÓN (MUSD)",
        ))
        st.plotly_chart(fig_scat, use_container_width=True)

    with p_r:
        # Funnel de estado
        estado_agg = (df_p_fil.groupby("estado")
                      .agg(n=("nombre","count"),
                           cap=("capacidad_mw","sum"))
                      .reset_index())
        estado_order = {"Operativo":0,"En Constr.":1,"Radicado":2}
        estado_agg["ord"] = estado_agg["estado"].map(estado_order)
        estado_agg = estado_agg.sort_values("ord")

        fig_funnel = go.Figure(go.Funnel(
            y=estado_agg["estado"],
            x=estado_agg["n"],
            textinfo="value+percent initial",
            marker=dict(color=[P["neon"], P["amber"], P["ice"]]),
            connector=dict(line=dict(color=P["rim"], width=1)),
            textfont=dict(family="JetBrains Mono, monospace",
                          size=11, color=P["text_hi"]),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Proyectos: %{x}<br>"
                "<extra></extra>"
            ),
        ))
        fig_funnel.update_layout(**plotly_base(
            height=380,
            title_text="EMBUDO DE MADUREZ · PROYECTOS ERNC",
            plot_bgcolor=P["surface"],
        ))
        st.plotly_chart(fig_funnel, use_container_width=True)

    # Barras apiladas inversión por región y tipo
    inv_rt = (df_p_fil.groupby(["region","tipo"])["inversion_musd"]
              .sum().reset_index())
    fig_inv = go.Figure()
    for tipo in inv_rt["tipo"].unique():
        sub = inv_rt[inv_rt["tipo"] == tipo]
        fig_inv.add_trace(go.Bar(
            x=sub["region"], y=sub["inversion_musd"],
            name=tipo,
            marker_color=ENERGY_COLORS.get(tipo, P["text_lo"]),
            hovertemplate=(
                f"<b>{tipo}</b><br>"
                f"%{{x}}: USD %{{y:,.1f}}M<extra></extra>"
            ),
        ))
    fig_inv.update_layout(**plotly_base(
        barmode="stack", height=280,
        title_text="INVERSIÓN ERNC POR REGIÓN Y TIPO (MUSD)",
        xaxis_title="REGIÓN",
        yaxis_title="MUSD",
    ))
    st.plotly_chart(fig_inv, use_container_width=True)

    # Tabla de proyectos
    with st.expander(f"📋 TABLA DE PROYECTOS ({len(df_p_fil)} registros)"):
        show_cols = ["nombre","tipo","departamento","estado",
                     "capacidad_mw","inversion_musd","empleos","anio_fpo"]
        st.dataframe(
            df_p_fil[show_cols].sort_values("capacidad_mw", ascending=False),
            use_container_width=True, hide_index=True,
        )


    # ── Empleos por departamento y tipo ───────────────────────────────────────
    st.markdown(section_rule("IMPACTO EN EMPLEO VERDE"), unsafe_allow_html=True)
    emp_l, emp_r = st.columns([1.3, 0.7])
    with emp_l:
        emp_dep = (df_p_fil.groupby(["departamento","tipo"])["empleos"]
                   .sum().reset_index())
        fig_emp = go.Figure()
        for tip in emp_dep["tipo"].unique():
            sub = emp_dep[emp_dep["tipo"]==tip]
            fig_emp.add_trace(go.Bar(
                x=sub["departamento"], y=sub["empleos"], name=tip,
                marker_color=ENERGY_COLORS.get(tip, P["text_lo"]),
                hovertemplate=f"<b>{tip}</b><br>%{{x}}: %{{y:,}} empleos<extra></extra>",
            ))
        fig_emp.update_layout(**plotly_base(
            barmode="stack", height=300,
            title_text="EMPLEOS VERDES POR DEPARTAMENTO Y TIPO DE ENERGÍA",
            xaxis_tickangle=-30, yaxis_title="EMPLEOS",
        ))
        st.plotly_chart(fig_emp, use_container_width=True)

    with emp_r:
        # Donut empleos por tipo
        emp_tipo = (df_p_fil.groupby("tipo")["empleos"].sum()
                    .reset_index().sort_values("empleos", ascending=False))
        fig_emp_d = go.Figure(go.Pie(
            labels=emp_tipo["tipo"], values=emp_tipo["empleos"],
            hole=0.60,
            marker=dict(colors=[ENERGY_COLORS.get(t, P["text_lo"])
                                  for t in emp_tipo["tipo"]],
                        line=dict(color=P["void"], width=2)),
            textinfo="percent", textfont=dict(size=9),
            hovertemplate="<b>%{label}</b><br>%{value:,} empleos · %{percent}<extra></extra>",
        ))
        fig_emp_d.add_annotation(
            text=f"<b>{int(df_p_fil['empleos'].sum()):,}</b>",
            x=0.5, y=0.56, showarrow=False,
            font=dict(size=20, color=P["neon"], family="Barlow Condensed,sans-serif"),
        )
        fig_emp_d.add_annotation(
            text="EMPLEOS", x=0.5, y=0.42, showarrow=False,
            font=dict(size=9, color=P["text_lo"], family="JetBrains Mono,monospace"),
        )
        fig_emp_d.update_layout(**plotly_base(
            height=300, title_text="MIX DE EMPLEO POR FUENTE",
        ))
        st.plotly_chart(fig_emp_d, use_container_width=True)

    # ── Tabla de proyectos ─────────────────────────────────────────────────────
    with st.expander(f"📋  TABLA COMPLETA DE PROYECTOS ({len(df_p_fil)} registros)"):
        show_cols = ["nombre","tipo","departamento","estado",
                     "capacidad_mw","inversion_musd","empleos","anio_fpo"]
        show_cols = [c for c in show_cols if c in df_p_fil.columns]
        st.dataframe(
            df_p_fil[show_cols].sort_values("capacidad_mw", ascending=False)
                .rename(columns={"nombre":"Proyecto","tipo":"Tipo",
                                  "departamento":"Departamento",
                                  "estado":"Estado","capacidad_mw":"MW",
                                  "inversion_musd":"MUSD","empleos":"Empleos",
                                  "anio_fpo":"FPO"}),
            use_container_width=True, hide_index=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 · EMISIONES CO₂
# ──────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown(neon_header(
        "🌿", "Monitoreo de Emisiones CO₂ y Meta NDC",
        subtitle="inventario GEI · tendencias sectoriales · compromisos climáticos",
        badge="META NDC −51%",
        badge_col=P["neon"],
    ), unsafe_allow_html=True)

    em_l, em_r = st.columns([1.3, 0.7])

    with em_l:
        # Líneas por sector
        fig_em = go.Figure()
        for sec in df_emis["sector"].unique():
            sub = df_emis[df_emis["sector"] == sec].sort_values("anio")
            fig_em.add_trace(go.Scatter(
                x=sub["anio"], y=sub["mt_co2"],
                name=sec,
                mode="lines+markers",
                line=dict(width=2.5),
                marker=dict(size=7),
                hovertemplate=(
                    f"<b>{sec}</b><br>"
                    f"%{{x}}: %{{y:.2f}} Mt CO₂<extra></extra>"
                ),
            ))

        # Meta NDC para sector eléctrico
        base_elec = float(
            df_emis[df_emis["sector"]=="Energía Eléctrica"]
            .sort_values("anio")["mt_co2"].iloc[0])
        meta_elec = base_elec * 0.49

        fig_em.add_hline(
            y=meta_elec, line_dash="dash",
            line_color=P["neon"], line_width=2,
            annotation_text=f"META NDC SECTOR ELÉCTRICO: {meta_elec:.1f} Mt",
            annotation_font=dict(color=P["neon"], size=10),
        )

        fig_em.update_layout(**plotly_base(
            height=380, hovermode="x unified",
            title_text="EMISIONES CO₂ POR SECTOR · MT CO₂/AÑO",
            xaxis_title="AÑO", yaxis_title="Mt CO₂",
        ))
        st.plotly_chart(fig_em, use_container_width=True)

    with em_r:
        # Gauge de avance NDC
        emis_2018 = df_emis.groupby("anio")["mt_co2"].sum().loc[2018]
        emis_act  = df_emis.groupby("anio")["mt_co2"].sum().loc[
            min(anio_sel, 2026)]
        reduccion_real = (emis_2018 - emis_act) / emis_2018 * 100

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=reduccion_real,
            delta={"reference": 51, "valueformat": ".1f",
                   "suffix": "%",
                   "font": {"size": 14, "color": P["text_mid"]}},
            number={"suffix": "%",
                    "font": {"size": 36, "color": P["neon"],
                             "family": "Barlow Condensed"}},
            title={"text": "REDUCCIÓN GEI<br>vs LÍNEA BASE 2018",
                   "font": {"size": 11, "color": P["text_lo"],
                            "family": "JetBrains Mono"}},
            gauge={
                "axis": {
                    "range": [0, 51],
                    "tickfont": {"size": 9, "color": P["text_lo"]},
                    "tickcolor": P["rim"],
                },
                "bar": {
                    "color": P["neon"],
                    "thickness": 0.22,
                },
                "bgcolor": P["surface"],
                "borderwidth": 1,
                "bordercolor": P["rim"],
                "steps": [
                    {"range": [0, 20],
                     "color": P["alert_glow"]},
                    {"range": [20, 40],
                     "color": P["amber_glow"]},
                    {"range": [40, 51],
                     "color": P["neon_glow"]},
                ],
                "threshold": {
                    "line": {"color": P["alert"], "width": 3},
                    "thickness": 0.85,
                    "value": 51,
                },
            },
        ))
        fig_gauge.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=P["text_mid"]),
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Barras de progreso NDC por sector
        st.markdown(
            f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,'
            f'monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">'
            f'REDUCCIÓN POR SECTOR</div>',
            unsafe_allow_html=True)
        emis_por_sector = (df_emis
                           .groupby(["anio","sector"])["mt_co2"]
                           .sum().unstack().fillna(0))
        if len(emis_por_sector) >= 2:
            base_s  = emis_por_sector.iloc[0]
            last_s  = emis_por_sector.iloc[-1]
            red_s   = ((base_s - last_s) / base_s * 100).fillna(0)
            for sec, red in red_s.items():
                pct = min(max(red / 51 * 100, 0), 100)
                col = (P["neon"] if red >= 20
                       else P["amber"] if red >= 0 else P["alert"])
                st.markdown(f"""
<div style="margin:4px 0;">
  <div style="display:flex;justify-content:space-between;
              margin-bottom:3px;">
    <span style="color:{P['text_mid']};font-size:10px;
                 font-family:Barlow,sans-serif;">{sec}</span>
    <span style="color:{col};font-family:JetBrains Mono,monospace;
                 font-size:9px;font-weight:600;">{red:+.1f}%</span>
  </div>
  <div style="background:{P['surface']};border-radius:3px;height:5px;
              border:1px solid {P['rim']};overflow:hidden;">
    <div style="width:{pct:.1f}%;height:100%;
                background:linear-gradient(90deg,{_ca(col,'88')},{col});
                border-radius:3px;"></div>
  </div>
</div>""", unsafe_allow_html=True)

    # Heatmap emisiones
    piv_em = (df_emis.groupby(["anio","sector"])["mt_co2"]
              .sum().unstack().fillna(0))
    fig_hm = go.Figure(go.Heatmap(
        z=piv_em.values,
        x=[s for s in piv_em.columns],
        y=[str(int(a)) for a in piv_em.index],
        colorscale=[
            [0.0,  P["surface"]],
            [0.25, "#1A3A2A"],
            [0.5,  P["neon_dim"]],
            [0.75, P["amber"]],
            [1.0,  P["alert"]],
        ],
        text=[[f"{v:.1f}" for v in row] for row in piv_em.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color=P["void"],
                      family="JetBrains Mono, monospace"),
        hovertemplate="Año: %{y}<br>Sector: %{x}<br>%{z:.2f} Mt CO₂<extra></extra>",
        colorbar=dict(
            title=dict(text="Mt CO₂",
                       font=dict(color=P["text_mid"], size=10)),
            tickfont=dict(color=P["text_lo"], size=9),
            bgcolor=P["surface"],
            bordercolor=P["rim"],
            thickness=12,
        ),
    ))
    fig_hm.update_layout(**plotly_base(
        height=280,
        title_text="HEATMAP EMISIONES CO₂ (Mt) · AÑO vs SECTOR",
        xaxis_tickangle=-20,
    ))
    st.plotly_chart(fig_hm, use_container_width=True)


    # ── Barras apiladas ────────────────────────────────────────────────────────
    st.markdown(section_rule("EMISIONES TOTALES POR SECTOR Y AÑO"), unsafe_allow_html=True)
    em3_l, em3_r = st.columns(2)
    with em3_l:
        agg_ap = df_emis.groupby(["anio","sector"])["mt_co2"].sum().reset_index()
        fig_em3 = go.Figure()
        SECT_COLORS = {
            "Energía Eléctrica": P["neon"], "Transporte": P["alert"],
            "Industria": P["amber"], "Agropecuario": "#66BB6A",
            "Residencial": P["ice"],
        }
        for s in agg_ap["sector"].unique():
            sub = agg_ap[agg_ap["sector"]==s].sort_values("anio")
            fig_em3.add_trace(go.Bar(
                x=sub["anio"], y=sub["mt_co2"], name=s,
                marker_color=SECT_COLORS.get(s, P["text_lo"]),
                hovertemplate=f"<b>{s}</b><br>%{{x}}: %{{y:.2f}} Mt<extra></extra>",
            ))
        fig_em3.update_layout(**plotly_base(
            barmode="stack", height=320,
            title_text="EMISIONES CO₂ APILADAS POR SECTOR (Mt)",
            xaxis_title="AÑO", yaxis_title="Mt CO₂",
        ))
        st.plotly_chart(fig_em3, use_container_width=True)

    with em3_r:
        # Emisiones por departamento (barra horizontal)
        em_dept = (df_emis.groupby("sector")["mt_co2"].sum()
                   .reset_index().sort_values("mt_co2", ascending=True))
        fig_em4 = go.Figure(go.Bar(
            x=em_dept["mt_co2"], y=em_dept["sector"],
            orientation="h",
            marker=dict(
                color=[SECT_COLORS.get(s, P["text_lo"]) for s in em_dept["sector"]],
                opacity=0.88, line=dict(color=P["void"], width=0.5),
            ),
            text=[f"{v:.1f} Mt" for v in em_dept["mt_co2"]],
            textposition="outside",
            textfont=dict(size=10, color=P["text_mid"]),
            hovertemplate="<b>%{y}</b><br>%{x:.2f} Mt CO₂<extra></extra>",
        ))
        fig_em4.update_layout(**plotly_base(
            height=320,
            title_text="TOTAL EMISIONES POR SECTOR (Mt acumulado)",
            xaxis_title="Mt CO₂", yaxis=dict(automargin=True),
        ))
        st.plotly_chart(fig_em4, use_container_width=True)

    # ── Barras de progreso NDC ─────────────────────────────────────────────────
    st.markdown(section_rule("PROGRESO HACIA META NDC −51% POR SECTOR"), unsafe_allow_html=True)
    ndcr = df_emis.groupby(["anio","sector"])["mt_co2"].sum().unstack().fillna(0)
    if len(ndcr) >= 2:
        base_s = ndcr.iloc[0]
        last_s = ndcr.iloc[-1]
        red_s  = ((base_s - last_s) / base_s * 100).fillna(0)
        for sec_n, red in red_s.items():
            pct   = min(max(red / 51 * 100, 0), 100)
            col_n = P["neon"] if red >= 20 else (P["amber"] if red >= 0 else P["alert"])
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:12px;margin:5px 0;'>"
                f"<div style='color:{P['text_mid']};font-size:11px;width:180px;"
                f"font-family:Barlow,sans-serif;'>{sec_n}</div>"
                f"<div style='flex:1;background:{P['surface']};border-radius:3px;"
                f"height:6px;overflow:hidden;border:1px solid {P['rim']};'>"
                f"<div style='width:{pct:.1f}%;height:100%;"
                f"background:linear-gradient(90deg,{_ca(col_n,'88')},{col_n});border-radius:3px;'>"
                f"</div></div>"
                f"<div style='color:{col_n};font-size:11px;width:130px;text-align:right;"
                f"font-family:JetBrains Mono,monospace;font-weight:600;'>"
                f"{red:+.1f}% de &minus;51%</div></div>",
                unsafe_allow_html=True,
            )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 · CONSUMO ENERGÉTICO
# ──────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown(neon_header(
        "💡", "Consumo Energético Nacional",
        subtitle="demanda · tendencias · distribución regional",
        badge="UPME · SIN",
    ), unsafe_allow_html=True)

    cons_l, cons_r = st.columns(2)

    with cons_l:
        # Consumo nacional acumulado por año
        cons_nat = df_cons.groupby("anio")["consumo_gwh"].sum().reset_index()
        fig_cons = go.Figure()
        fig_cons.add_trace(go.Scatter(
            x=cons_nat["anio"], y=cons_nat["consumo_gwh"],
            mode="lines+markers",
            line=dict(color=P["ice"], width=3),
            marker=dict(size=9, color=P["void"],
                        line=dict(color=P["ice"], width=2.5)),
            fill="tozeroy",
            fillcolor=P["ice_glow"],
            hovertemplate="<b>%{x}</b>: %{y:,.0f} GWh<extra></extra>",
            name="Consumo Nacional",
        ))
        fig_cons.update_layout(**plotly_base(
            height=340,
            title_text="DEMANDA ENERGÉTICA NACIONAL · GWh/AÑO",
            xaxis_title="AÑO", yaxis_title="GWh",
        ))
        st.plotly_chart(fig_cons, use_container_width=True)

    with cons_r:
        # Treemap consumo por región y departamento
        cons_tree = df_cons[df_cons["anio"] == anio_sel].copy()
        fig_tree = px.treemap(
            cons_tree,
            path=["region","departamento"],
            values="consumo_gwh",
            color="consumo_gwh",
            color_continuous_scale=[
                [0.0, P["surface"]],
                [0.5, P["ice_mid"]],
                [1.0, P["neon"]],
            ],
        )
        fig_tree.update_layout(**plotly_base(
            height=340,
            title_text=f"CONSUMO POR REGIÓN Y DEPARTAMENTO · {anio_sel}",
        ))
        fig_tree.update_traces(
            textfont=dict(size=10, family="Barlow, sans-serif"),
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    # Heatmap consumo departamento x año
    cons_hm = (df_cons[df_cons["departamento"].isin(
                   df_cons.groupby("departamento")["consumo_gwh"]
                   .mean().nlargest(16).index)]
               .pivot(index="departamento", columns="anio",
                      values="consumo_gwh").fillna(0))

    fig_cons_hm = go.Figure(go.Heatmap(
        z=cons_hm.values,
        x=[str(int(a)) for a in cons_hm.columns],
        y=cons_hm.index.tolist(),
        colorscale=[
            [0.0, P["deep"]],
            [0.4, "rgba(0,184,212,0.4)"],
            [0.7, P["ice"]],
            [1.0, P["neon"]],
        ],
        text=[[f"{v:,.0f}" for v in row] for row in cons_hm.values],
        texttemplate="%{text}",
        textfont=dict(size=8, color=P["void"],
                      family="JetBrains Mono, monospace"),
        hovertemplate=(
            "Depto: %{y}<br>Año: %{x}<br>"
            "%{z:,.0f} GWh<extra></extra>"
        ),
        colorbar=dict(
            tickfont=dict(color=P["text_lo"], size=9),
            title=dict(text="GWh",
                       font=dict(color=P["text_mid"], size=10)),
        ),
    ))
    fig_cons_hm.update_layout(**plotly_base(
        height=440,
        title_text="HEATMAP CONSUMO (GWh) · DEPARTAMENTOS vs AÑO",
        xaxis_title="AÑO", yaxis_title="DEPARTAMENTO",
    ))
    st.plotly_chart(fig_cons_hm, use_container_width=True)


    # ── Box plot y evolución trimestral ───────────────────────────────────────
    st.markdown(section_rule("ANÁLISIS DE VARIABILIDAD Y TENDENCIA"), unsafe_allow_html=True)
    box_l, box_r = st.columns(2)

    with box_l:
        # Box plot consumo por región
        fig_box = go.Figure()
        for reg in sorted(df_cons["region"].unique()):
            vals = df_cons[df_cons["region"]==reg]["consumo_gwh"].dropna()
            if vals.empty: continue
            fig_box.add_trace(go.Box(
                y=vals, name=reg, boxmean=True,
                marker_color=REGION_COLORS.get(reg, P["text_lo"]),
                line=dict(width=1.5),
                hovertemplate=f"<b>{reg}</b><br>%{{y:,.0f}} GWh<extra></extra>",
            ))
        fig_box.update_layout(**plotly_base(
            height=320, title_text="DISTRIBUCIÓN DE CONSUMO POR REGIÓN (GWh)",
            yaxis_title="GWh",
        ))
        st.plotly_chart(fig_box, use_container_width=True)

    with box_r:
        # Crecimiento interanual por región
        cons_growth = (df_cons.groupby(["anio","region"])["consumo_gwh"]
                       .sum().reset_index())
        fig_grow = go.Figure()
        for reg in cons_growth["region"].unique():
            sub = cons_growth[cons_growth["region"]==reg].sort_values("anio").copy()
            sub["yoy"] = sub["consumo_gwh"].pct_change() * 100
            sub = sub.dropna()
            fig_grow.add_trace(go.Scatter(
                x=sub["anio"], y=sub["yoy"], name=reg,
                mode="lines+markers",
                line=dict(color=REGION_COLORS.get(reg, P["text_lo"]), width=2),
                marker=dict(size=7),
                hovertemplate=f"<b>{reg}</b><br>%{{x}}: %{{y:+.1f}}% YoY<extra></extra>",
            ))
        fig_grow.add_hline(y=0, line_dash="dot",
                            line_color=P["text_lo"],
                            line_width=1)
        fig_grow.update_layout(**plotly_base(
            height=320, hovermode="x unified",
            title_text="CRECIMIENTO INTERANUAL DEL CONSUMO POR REGIÓN (%)",
            xaxis_title="AÑO", yaxis_title="YoY %",
        ))
        st.plotly_chart(fig_grow, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 · PANEL DE ALERTAS
# ──────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown(neon_header(
        "🛡", "Panel de Alertas Estratégicas del Sistema",
        subtitle="riesgos · oportunidades · estado de la infraestructura",
        badge="TIEMPO REAL",
        badge_col=P["alert"],
    ), unsafe_allow_html=True)

    al_l, al_r = st.columns(2)

    with al_l:
        st.markdown(
            f'<div style="color:{P["alert"]};'
            f'font-family:Barlow Condensed,sans-serif;'
            f'font-size:13px;font-weight:700;letter-spacing:1px;'
            f'margin-bottom:8px;">🔴 ALERTAS CRÍTICAS</div>',
            unsafe_allow_html=True)
        alertas_crit = [
            ("DEPENDENCIA HÍDRICA CRÍTICA",
             "El 66% de la generación depende de hidroeléctricas. "
             "Con El Niño proyectado Q3 2026, el riesgo de déficit "
             "supera el 35%. Embalses al 58% de capacidad promedio.",
             "crit"),
            ("REZAGO TRANSMISIÓN LA GUAJIRA",
             "Misión Transmisión presenta retraso de 14 meses. "
             "1.752 MW eólicos listos NO PUEDEN conectarse al SIN "
             "por falta de infraestructura de evacuación.",
             "crit"),
        ]
        for t, b, lvl in alertas_crit:
            st.markdown(alert_chip(t, b, lvl), unsafe_allow_html=True)

        st.markdown(
            f'<div style="color:{P["amber"]};'
            f'font-family:Barlow Condensed,sans-serif;'
            f'font-size:13px;font-weight:700;letter-spacing:1px;'
            f'margin:14px 0 8px;">🟡 ALERTAS DE ATENCIÓN</div>',
            unsafe_allow_html=True)
        alertas_warn = [
            ("META NDC EN RIESGO",
             "Colombia avanza al 38% de la reducción requerida. "
             "Para cumplir el compromiso 2030, el ritmo de instalación "
             "debe triplicarse en los próximos 18 meses.",
             "warn"),
            ("CONCENTRACIÓN GEOGRÁFICA",
             "Antioquia acumula el 47% de la capacidad renovable. "
             "La transición es geográficamente inequitativa y aumenta "
             "la vulnerabilidad sistémica.",
             "warn"),
            ("COSTOS ZNI EXTREMOS",
             "Generación diésel en ZNI supera $1.250 COP/kWh. "
             "12 municipios amazónicos sin proyecto de hibridización "
             "asignado para 2026.",
             "warn"),
        ]
        for t, b, lvl in alertas_warn:
            st.markdown(alert_chip(t, b, lvl), unsafe_allow_html=True)

    with al_r:
        st.markdown(
            f'<div style="color:{P["neon"]};'
            f'font-family:Barlow Condensed,sans-serif;'
            f'font-size:13px;font-weight:700;letter-spacing:1px;'
            f'margin-bottom:8px;">🟢 SEÑALES POSITIVAS</div>',
            unsafe_allow_html=True)
        alertas_good = [
            ("CRECIMIENTO SOLAR HISTÓRICO",
             "+187% en 2024 — el mayor año de la historia del país. "
             "1.348 MW en operación con pipeline de 3.200 MW radicados "
             "y en proceso de aprobación ambiental.",
             "good"),
            ("FINANCIACIÓN VERDE EN AUMENTO",
             "IFC y BID certificaron USD 1.2B en bonos verdes en 2025. "
             "TRM favorable y riesgo país en mínimos históricos "
             "posicionan a Colombia como destino premium LATAM.",
             "good"),
            ("AVANCE ITUANGO",
             "Proyecto Ituango (2.400 MW) alcanzó el 87% de avance. "
             "Primer grupo generador previsto Q2 2026. "
             "Energía suficiente para 8 millones de hogares.",
             "good"),
        ]
        for t, b, lvl in alertas_good:
            st.markdown(alert_chip(t, b, lvl), unsafe_allow_html=True)

        st.markdown(
            f'<div style="color:{P["ice"]};'
            f'font-family:Barlow Condensed,sans-serif;'
            f'font-size:13px;font-weight:700;letter-spacing:1px;'
            f'margin:14px 0 8px;">🔵 INFORMACIÓN DEL SISTEMA</div>',
            unsafe_allow_html=True)
        alertas_info = [
            ("REFORMA TARIFARIA EN REVISIÓN",
             "El CREG analiza ajuste de cargos por capacidad. "
             "Impacto esperado en tarifa de usuarios regulados: "
             "+8% promedio. Resolución pendiente CREG 2026.",
             "info"),
            ("NUEVA SUBASTA UPME 2026",
             "Convocatoria abierta para 800 MW adicionales FNCER. "
             "Cierre de propuestas: agosto 2026. "
             "Primer contrato estimado a 15 años.",
             "info"),
        ]
        for t, b, lvl in alertas_info:
            st.markdown(alert_chip(t, b, lvl), unsafe_allow_html=True)

    # Semáforo sistémico
    st.markdown(section_rule("SEMÁFORO DEL SISTEMA ENERGÉTICO"), unsafe_allow_html=True)
    indicadores = [
        ("Abastecimiento SIN",    "ESTABLE",   P["neon"],   "97.8% cobertura nacional"),
        ("Reserva Hídrica",       "ALERTA",    P["alert"],  "Embalses al 58% promedio"),
        ("Pipeline Renovable",    "ÓPTIMO",    P["neon"],   "82 proyectos en ejecución"),
        ("Precios Mayorista",     "ATENCIÓN",  P["amber"],  "$280 COP/kWh prom. bolsa"),
        ("Avance NDC 2030",       "REZAGADO",  P["amber"],  "38% de meta cumplida"),
        ("Infraestructura TX",    "CRÍTICO",   P["alert"],  "Retraso Misión Transmisión"),
    ]
    sem_cols = st.columns(6)
    for col_s, (ind, estado, color, detalle) in zip(sem_cols, indicadores):
        col_s.markdown(f"""
<div style="
    background:linear-gradient(145deg,{P['raised']},{P['surface']});
    border:1px solid {_ca(color,'30')};border-top:3px solid {color};
    border-radius:8px;padding:12px 10px;text-align:center;">
  <div style="
      width:10px;height:10px;border-radius:50%;
      background:{color};box-shadow:0 0 10px {color};
      margin:0 auto 8px;"></div>
  <div style="color:{P['text_mid']};font-size:10px;
              font-weight:600;margin-bottom:4px;">{ind}</div>
  <div style="color:{color};font-family:JetBrains Mono,monospace;
              font-size:9px;font-weight:700;letter-spacing:.5px;
              margin-bottom:6px;">{estado}</div>
  <div style="color:{P['text_lo']};font-size:9px;line-height:1.4;">{detalle}</div>
</div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────

# TAB 6 · IA PREDICTIVA
# ──────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown(neon_header(
        "🧠", "Analítica Predictiva e Inteligencia Energética",
        subtitle="regresión exponencial · polinomial · suavizado · correlaciones · escenarios",
        badge="IA · MODELOS ML",
        badge_col=P["amber"],
    ), unsafe_allow_html=True)

    # ── Funciones de modelado ──────────────────────────────────────────────────
    def fit_exponencial(x, y):
        """Ajuste exponencial y = a * e^(b*x). Retorna (a, b, y_pred, r2, rmse)."""
        log_y = np.log(np.maximum(y, 0.1))
        coeffs = np.polyfit(x, log_y, 1)
        b, log_a = coeffs
        a = np.exp(log_a)
        y_pred = a * np.exp(b * x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / max(ss_tot, 1e-9)
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        return a, b, y_pred, r2, rmse

    def fit_polinomial(x, y, deg=2):
        """Ajuste polinomial de grado deg. Retorna (coeffs, y_pred, r2, rmse)."""
        coeffs = np.polyfit(x, y, deg)
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / max(ss_tot, 1e-9)
        rmse = np.sqrt(np.mean((y - y_pred) ** 2))
        return coeffs, y_pred, r2, rmse

    def suavizado_exponencial(y, alpha=0.3):
        """Suavizado exponencial simple (EMA)."""
        s = np.zeros(len(y))
        s[0] = y[0]
        for i in range(1, len(y)):
            s[i] = alpha * y[i] + (1 - alpha) * s[i - 1]
        return s

    def holt_winters_simple(y, alpha=0.35, beta=0.25, n_forecast=5):
        """Suavizado Holt (tendencia) con proyección."""
        n = len(y)
        l = np.zeros(n)
        b = np.zeros(n)
        l[0] = y[0]
        b[0] = y[1] - y[0] if n > 1 else 0
        for t in range(1, n):
            l[t] = alpha * y[t] + (1 - alpha) * (l[t - 1] + b[t - 1])
            b[t] = beta * (l[t] - l[t - 1]) + (1 - beta) * b[t - 1]
        forecast = [l[-1] + i * b[-1] for i in range(1, n_forecast + 1)]
        return l, forecast

    # ── Selector de fuente energética ─────────────────────────────────────────
    st.markdown(
        f'<div style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;'
        f'font-size:9px;letter-spacing:2px;margin-bottom:6px;">'
        f'SELECCIONAR FUENTE PARA MODELADO</div>',
        unsafe_allow_html=True)

    ia_ctrl1, ia_ctrl2, ia_ctrl3 = st.columns([1, 1, 1])
    with ia_ctrl1:
        fuente_ia = st.selectbox(
            "Fuente energética",
            ["Solar", "Eólica", "Hidroeléctrica", "Gas Natural", "Carbón", "Biomasa"],
            index=0, key="ia_fuente")
    with ia_ctrl2:
        horizonte = st.slider("Horizonte de proyección (años)", 2, 10, 5, key="ia_horiz")
    with ia_ctrl3:
        grado_poly = st.selectbox("Grado polinomial", [2, 3, 4], index=0, key="ia_grado")

    # ── Datos de la fuente seleccionada ───────────────────────────────────────
    src = df_cap[df_cap["fuente"] == fuente_ia].sort_values("anio").copy()
    y_hist = src["capacidad_mw"].values.astype(float)
    x_hist = np.arange(len(y_hist))
    anios_hist = src["anio"].tolist()
    n = len(y_hist)

    # Años futuros para proyección
    anios_fut = list(range(anios_hist[-1] + 1, anios_hist[-1] + horizonte + 1))
    x_fut = np.arange(n, n + horizonte)
    x_full = np.concatenate([x_hist, x_fut])
    anios_full = anios_hist + anios_fut

    # ── Ajustar modelos ────────────────────────────────────────────────────────
    a_exp, b_exp, y_exp_hist, r2_exp, rmse_exp = fit_exponencial(x_hist, y_hist)
    y_exp_fut  = a_exp * np.exp(b_exp * x_fut)
    y_exp_full = a_exp * np.exp(b_exp * x_full)

    coeffs_p, y_poly_hist, r2_poly, rmse_poly = fit_polinomial(x_hist, y_hist, grado_poly)
    y_poly_fut  = np.polyval(coeffs_p, x_fut)
    y_poly_full = np.polyval(coeffs_p, x_full)

    ema_hist     = suavizado_exponencial(y_hist, alpha=0.35)
    l_holt, fc_holt = holt_winters_simple(y_hist, alpha=0.35, beta=0.25, n_forecast=horizonte)
    y_holt_full = list(l_holt) + fc_holt

    # Bandas de confianza (±1.5σ residuales)
    resid_exp  = y_hist - y_exp_hist
    sigma_exp  = np.std(resid_exp)
    ci_factor  = np.linspace(1.0, 1.8, horizonte)
    y_exp_hi   = y_exp_fut + sigma_exp * 1.5 * ci_factor
    y_exp_lo   = np.maximum(y_exp_fut - sigma_exp * 1.2 * ci_factor, y_exp_fut * 0.6)

    # ── GRÁFICO PRINCIPAL — comparativo de modelos ────────────────────────────
    ia_g1, ia_g2 = st.columns([1.55, 0.45])
    with ia_g1:
        color_fuente = ENERGY_COLORS.get(fuente_ia, P["neon"])
        fig_ia = go.Figure()

        # Banda de confianza exponencial
        fig_ia.add_trace(go.Scatter(
            x=anios_fut + anios_fut[::-1],
            y=list(y_exp_hi) + list(y_exp_lo[::-1]),
            fill="toself",
            fillcolor=_ca(color_fuente, "18"),
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
            name="IC Exponencial",
        ))

        # Modelo exponencial — proyección
        fig_ia.add_trace(go.Scatter(
            x=anios_fut,
            y=y_exp_fut,
            mode="lines",
            line=dict(color=color_fuente, width=2.5, dash="dash"),
            name=f"Exp. Proyección",
            hovertemplate="%{x}: %{y:,.0f} MW<extra></extra>",
        ))

        # Modelo polinomial — proyección
        fig_ia.add_trace(go.Scatter(
            x=anios_fut,
            y=y_poly_fut,
            mode="lines",
            line=dict(color=P["ice"], width=2, dash="dot"),
            name=f"Poly. Grado {grado_poly}",
            hovertemplate="%{x}: %{y:,.0f} MW<extra></extra>",
        ))

        # Modelo Holt-Winters — proyección
        fig_ia.add_trace(go.Scatter(
            x=anios_fut,
            y=fc_holt,
            mode="lines",
            line=dict(color=P["amber"], width=2, dash="longdash"),
            name="Holt-Winters",
            hovertemplate="%{x}: %{y:,.0f} MW<extra></extra>",
        ))

        # EMA histórica
        fig_ia.add_trace(go.Scatter(
            x=anios_hist,
            y=ema_hist,
            mode="lines",
            line=dict(color=P["neon_dim"], width=1.5, dash="dot"),
            name="EMA (α=0.35)",
            hovertemplate="%{x}: %{y:,.0f} MW<extra></extra>",
        ))

        # Datos históricos reales (encima de todo)
        fig_ia.add_trace(go.Scatter(
            x=anios_hist,
            y=y_hist,
            mode="lines+markers",
            line=dict(color=color_fuente, width=3),
            marker=dict(size=9, color=P["void"],
                        line=dict(color=color_fuente, width=2.5)),
            fill="tozeroy",
            fillcolor=_ca(color_fuente, "10"),
            name="Histórico Real",
            hovertemplate="%{x}: %{y:,.0f} MW<extra></extra>",
        ))

        # Línea divisoria hist/pred
        fig_ia.add_vline(
            x=anios_hist[-1], line_dash="dot",
            line_color=P["text_lo"], line_width=1.5,
            annotation_text="HOY",
            annotation_font=dict(color=P["text_lo"], size=9,
                                 family="JetBrains Mono, monospace"),
        )

        title_cagr = b_exp * 100
        fig_ia.update_layout(**plotly_base(
            height=400,
            title_text=f"MODELOS PREDICTIVOS · {fuente_ia.upper()} · CAGR EXPONENCIAL: {title_cagr:+.1f}%/AÑO",
            xaxis_title="AÑO", yaxis_title="MW",
            hovermode="x unified",
        ))
        st.plotly_chart(fig_ia, use_container_width=True)

    with ia_g2:
        # Panel de métricas de modelos
        cagr_real = ((y_hist[-1] / y_hist[0]) ** (1 / (n - 1)) - 1) * 100 if n > 1 else 0.0
        r2_holt   = 1 - np.sum((y_hist - l_holt) ** 2) / max(np.sum((y_hist - np.mean(y_hist)) ** 2), 1e-9)
        rmse_holt = float(np.sqrt(np.mean((y_hist - l_holt) ** 2)))

        metricas = [
            ("Regresión Exponencial", r2_exp,  rmse_exp,  color_fuente, b_exp * 100),
            (f"Polinomial Grado {grado_poly}",  r2_poly, rmse_poly, P["ice"],    None),
            ("Holt-Winters",          r2_holt, rmse_holt, P["amber"],  None),
        ]

        st.markdown(
            f'<div style="background:linear-gradient(135deg,{P["surface"]},{P["raised"]});'
            f'border:1px solid {P["rimhi"]};border-radius:10px;padding:16px;height:400px;overflow:auto;">',
            unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:{P["amber"]};font-family:Barlow Condensed,sans-serif;'
            f'font-size:13px;font-weight:700;letter-spacing:1px;margin-bottom:12px;'
            f'border-bottom:1px solid {P["rim"]};padding-bottom:8px;">'
            f'📊 MÉTRICAS DE MODELOS</div>',
            unsafe_allow_html=True)

        for nombre, r2, rmse_v, col, cagr_m in metricas:
            r2_pct  = max(0, min(r2 * 100, 100))
            r2_col  = P["neon"] if r2 > 0.92 else (P["amber"] if r2 > 0.75 else P["alert"])
            extra   = ""
            if cagr_m is not None:
                extra = (f'<span style="color:{P["text_lo"]};font-size:9px;'
                         f'font-family:JetBrains Mono,monospace;"> · CAGR: '
                         f'<span style="color:{col};">{cagr_m:+.1f}%</span></span>')
            st.markdown(f"""
<div style="margin-bottom:14px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
    <span style="color:{P['text_mid']};font-size:11px;font-weight:600;">{nombre}</span>
    {extra}
  </div>
  <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
    <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;">R² · BONDAD DE AJUSTE</span>
    <span style="color:{r2_col};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:600;">{r2:.4f}</span>
  </div>
  <div style="background:{P['surface']};border-radius:3px;height:4px;overflow:hidden;border:1px solid {P['rim']};margin-bottom:6px;">
    <div style="width:{r2_pct:.1f}%;height:100%;background:linear-gradient(90deg,{_ca(r2_col,'66')},{r2_col});border-radius:3px;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;">
    <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;">RMSE (MW)</span>
    <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;font-weight:500;">{rmse_v:,.1f}</span>
  </div>
</div>""", unsafe_allow_html=True)

        # CAGR real
        st.markdown(
            f'<div style="border-top:1px solid {P["rim"]};padding-top:10px;margin-top:6px;">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<span style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;font-size:9px;">CAGR REAL (PERÍODO)</span>'
            f'<span style="color:{color_fuente};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:700;">{cagr_real:+.2f}%</span>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:4px;">'
            f'<span style="color:{P["text_lo"]};font-family:JetBrains Mono,monospace;font-size:9px;">MW PROYECTADOS {anios_fut[-1]}</span>'
            f'<span style="color:{color_fuente};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:700;">{y_exp_fut[-1]:,.0f} MW</span>'
            f'</div></div>',
            unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tabla comparativa de proyecciones ─────────────────────────────────────
    st.markdown(section_rule("TABLA COMPARATIVA DE PROYECCIONES (MW)"), unsafe_allow_html=True)
    tabla_rows = []
    for i, anio in enumerate(anios_full):
        if anio in anios_hist:
            idx_h = anios_hist.index(anio)
            tabla_rows.append({
                "Año": anio,
                "Real (MW)": f"{y_hist[idx_h]:,.0f}",
                "Exp. (MW)": f"{y_exp_full[i]:,.0f}",
                f"Poly.G{grado_poly} (MW)": f"{max(0, y_poly_full[i]):,.0f}",
                "Holt-W. (MW)": f"{y_holt_full[i]:,.0f}" if i < len(y_holt_full) else "–",
                "Tipo": "HISTÓRICO",
            })
        else:
            i_fut = i - n
            tabla_rows.append({
                "Año": anio,
                "Real (MW)": "–",
                "Exp. (MW)": f"{y_exp_fut[i_fut]:,.0f}",
                f"Poly.G{grado_poly} (MW)": f"{max(0, y_poly_fut[i_fut]):,.0f}",
                "Holt-W. (MW)": f"{fc_holt[i_fut]:,.0f}" if i_fut < len(fc_holt) else "–",
                "Tipo": "PROYECCIÓN",
            })
    df_tabla_ia = pd.DataFrame(tabla_rows)
    st.dataframe(df_tabla_ia, use_container_width=True, hide_index=True, height=220)

    # ── Sección 2: Modelado de Emisiones CO₂ ─────────────────────────────────
    st.markdown(section_rule("MODELO DE DECAIMIENTO DE EMISIONES · SECTOR ELÉCTRICO"), unsafe_allow_html=True)
    em2_l, em2_r = st.columns([1.4, 0.6])

    with em2_l:
        emis_elec = (df_emis[df_emis["sector"] == "Energía Eléctrica"]
                     .sort_values("anio").copy())
        ye = emis_elec["mt_co2"].values.astype(float)
        xe = np.arange(len(ye))
        anios_e = emis_elec["anio"].tolist()

        # Ajuste exponencial de decaimiento
        a_e, b_e, ye_pred, r2_e, rmse_e = fit_exponencial(xe, ye)
        # Proyección al 2030
        anios_e_fut = list(range(anios_e[-1] + 1, 2031))
        xe_fut = np.arange(len(ye), len(ye) + len(anios_e_fut))
        ye_fut = a_e * np.exp(b_e * xe_fut)
        meta_ndc_e = ye[0] * 0.49  # -51% de la línea base

        fig_em_ia = go.Figure()
        # Banda meta
        fig_em_ia.add_hrect(
            y0=0, y1=meta_ndc_e,
            fillcolor=_ca(P["neon"], "0A"),
            line_width=0,
            annotation_text="ZONA META NDC",
            annotation_font=dict(color=P["neon"], size=9),
        )
        # Datos históricos
        fig_em_ia.add_trace(go.Scatter(
            x=anios_e, y=ye,
            mode="lines+markers",
            line=dict(color=P["alert"], width=3),
            marker=dict(size=8, color=P["void"],
                        line=dict(color=P["alert"], width=2.5)),
            fill="tozeroy", fillcolor=_ca(P["alert"], "10"),
            name="Histórico Real",
            hovertemplate="%{x}: %{y:.2f} Mt CO₂<extra></extra>",
        ))
        # Modelo exponencial ajustado
        fig_em_ia.add_trace(go.Scatter(
            x=anios_e, y=ye_pred,
            mode="lines",
            line=dict(color=P["amber"], width=2, dash="dot"),
            name=f"Exp. Ajustado (R²={r2_e:.3f})",
            hovertemplate="%{x}: %{y:.2f} Mt CO₂<extra></extra>",
        ))
        # Proyección
        fig_em_ia.add_trace(go.Scatter(
            x=anios_e_fut, y=ye_fut,
            mode="lines",
            line=dict(color=P["amber"], width=2.5, dash="dash"),
            name="Proyección exp.",
            hovertemplate="%{x}: %{y:.2f} Mt CO₂<extra></extra>",
        ))
        # Línea meta NDC
        fig_em_ia.add_hline(
            y=meta_ndc_e, line_dash="dash", line_color=P["neon"], line_width=2,
            annotation_text=f"META NDC: {meta_ndc_e:.1f} Mt",
            annotation_font=dict(color=P["neon"], size=10),
        )
        # ¿Cuándo se alcanza la meta?
        if b_e < 0:
            anio_meta_idx = None
            for i_f, yf in enumerate(ye_fut):
                if yf <= meta_ndc_e:
                    anio_meta_idx = i_f
                    break
            if anio_meta_idx is not None:
                anio_meta = anios_e_fut[anio_meta_idx]
                fig_em_ia.add_vline(
                    x=anio_meta, line_dash="dot",
                    line_color=P["neon"], line_width=1.5,
                    annotation_text=f"META: {anio_meta}",
                    annotation_font=dict(color=P["neon"], size=9),
                )

        fig_em_ia.update_layout(**plotly_base(
            height=360,
            title_text="EMISIONES SECTOR ELÉCTRICO · MODELO DE DECAIMIENTO EXPONENCIAL",
            xaxis_title="AÑO", yaxis_title="Mt CO₂",
        ))
        st.plotly_chart(fig_em_ia, use_container_width=True)

    with em2_r:
        # Resumen del modelo de emisiones
        reduccion_proyectada = ((ye[-1] - ye_fut[-1]) / ye[0] * 100) if len(ye_fut) > 0 else 0
        anio_meta_lbl = "N/A"
        if b_e < 0:
            for i_f, yf in enumerate(ye_fut):
                if yf <= meta_ndc_e:
                    anio_meta_lbl = str(anios_e_fut[i_f])
                    break

        st.markdown(f"""
<div style="background:linear-gradient(135deg,{P['surface']},{P['raised']});
border:1px solid {P['rimhi']};border-radius:10px;padding:16px;height:360px;overflow:auto;">
  <div style="color:{P['neon']};font-family:Barlow Condensed,sans-serif;
font-size:13px;font-weight:700;letter-spacing:1px;margin-bottom:12px;
border-bottom:1px solid {P['rim']};padding-bottom:8px;">
    🌿 ANÁLISIS DECAIMIENTO CO₂
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
    <div style="background:{P['glass']};border:1px solid {P['rim']};border-radius:6px;padding:10px;text-align:center;">
      <div style="color:{P['neon']};font-family:Barlow Condensed,sans-serif;font-size:20px;font-weight:800;">{r2_e:.4f}</div>
      <div style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;">R² AJUSTE</div>
    </div>
    <div style="background:{P['glass']};border:1px solid {P['rim']};border-radius:6px;padding:10px;text-align:center;">
      <div style="color:{P['alert']};font-family:Barlow Condensed,sans-serif;font-size:20px;font-weight:800;">{rmse_e:.3f}</div>
      <div style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;">RMSE (Mt)</div>
    </div>
  </div>

  <div style="margin-bottom:10px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
      <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;">TASA DECAIM. (b)</span>
      <span style="color:{P['amber']};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:600;">{b_e*100:.2f}%/año</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
      <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;">META NDC (−51%)</span>
      <span style="color:{P['neon']};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:600;">{meta_ndc_e:.2f} Mt</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
      <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;">AÑO ALCANCE META</span>
      <span style="color:{P['neon']};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:600;">{anio_meta_lbl}</span>
    </div>
    <div style="display:flex;justify-content:space-between;">
      <span style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:9px;">REDUC. PROY. 2030</span>
      <span style="color:{P['ice']};font-family:JetBrains Mono,monospace;font-size:10px;font-weight:600;">{reduccion_proyectada:.1f}%</span>
    </div>
  </div>

  <div style="background:{P['glass']};border:1px solid {P['rim']};border-radius:6px;padding:10px;margin-top:8px;">
    <div style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:1px;margin-bottom:6px;">FÓRMULA DEL MODELO</div>
    <div style="color:{P['neon']};font-family:JetBrains Mono,monospace;font-size:11px;font-weight:500;">
      y = {a_e:.3f} × e^({b_e:.4f} × t)
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Sección 3: Correlación de Pearson ─────────────────────────────────────
    st.markdown(section_rule("MATRIZ DE CORRELACIÓN DE PEARSON · VARIABLES ENERGÉTICAS"), unsafe_allow_html=True)
    corr_l, corr_r = st.columns([1, 1])

    with corr_l:
        # Construir dataset para correlación
        cap_pivot = df_cap.pivot(index="anio", columns="fuente", values="capacidad_mw").fillna(0)
        emis_pivot = df_emis.groupby("anio")["mt_co2"].sum().rename("Emisiones_Total")
        cons_pivot  = df_cons.groupby("anio")["consumo_gwh"].sum().rename("Consumo_GWh")

        df_corr = cap_pivot.join(emis_pivot, how="inner").join(cons_pivot, how="inner")
        df_corr.columns = [c.replace(" ", "_") for c in df_corr.columns]

        corr_matrix = df_corr.corr()

        # Heatmap de correlación con anotaciones
        fig_corr_ia = go.Figure(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns.tolist(),
            y=corr_matrix.index.tolist(),
            colorscale=[
                [0.0,  P["alert"]],
                [0.25, _ca(P["alert"], "66")],
                [0.5,  P["surface"]],
                [0.75, _ca(P["neon"], "88")],
                [1.0,  P["neon"]],
            ],
            zmin=-1, zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in corr_matrix.values],
            texttemplate="%{text}",
            textfont=dict(size=9, color=P["text_hi"],
                          family="JetBrains Mono, monospace"),
            hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.3f}<extra></extra>",
            colorbar=dict(
                title=dict(text="r Pearson",
                           font=dict(color=P["text_mid"], size=10)),
                tickfont=dict(color=P["text_lo"], size=9),
                bgcolor=P["surface"], bordercolor=P["rim"], thickness=12,
            ),
        ))
        fig_corr_ia.update_layout(**plotly_base(
            height=380,
            title_text="CORRELACIÓN PEARSON · CAPACIDAD (MW), EMISIONES y CONSUMO",
            xaxis=dict(tickangle=-25, automargin=True),
            yaxis=dict(automargin=True),
        ))
        st.plotly_chart(fig_corr_ia, use_container_width=True)

    with corr_r:
        # Scatter correlación inversión vs emisiones evitadas
        df_co2_corr = df_proy[df_proy["estado"].isin(["Operativo", "En Constr."])].copy()
        FACTORES_CF = {"Solar": 0.22, "Eólica": 0.35, "Hidroeléctrica": 0.45,
                       "Biomasa": 0.60, "Gas Natural": 0.00, "Carbón": 0.00, "Geotérmica": 0.90}
        df_co2_corr["co2_kt"] = (df_co2_corr["capacidad_mw"]
                                  * df_co2_corr["tipo"].map(FACTORES_CF).fillna(0)
                                  * 8760 / 1000 * 160 / 1e3)
        dept_corr = (df_co2_corr.groupby("departamento")
                     .agg(inv=("inversion_musd", "sum"),
                          co2=("co2_kt", "sum"),
                          emp=("empleos", "sum"))
                     .reset_index())

        if len(dept_corr) > 1:
            r_inv_co2 = np.corrcoef(dept_corr["inv"], dept_corr["co2"])[0, 1]
        else:
            r_inv_co2 = 0.0

        fig_sc_ia = go.Figure()
        fig_sc_ia.add_trace(go.Scatter(
            x=dept_corr["inv"], y=dept_corr["co2"],
            mode="markers+text",
            marker=dict(
                size=dept_corr["emp"].apply(lambda v: max(8, min(30, v / 120))),
                color=dept_corr["inv"],
                colorscale=[[0, P["surface"]], [0.5, P["ice_mid"]], [1, P["neon"]]],
                line=dict(color=P["void"], width=1),
                showscale=False,
            ),
            text=dept_corr["departamento"],
            textposition="top center",
            textfont=dict(size=7, color=P["text_lo"]),
            hovertemplate="<b>%{text}</b><br>Inversión: USD %{x:,.1f}M<br>CO₂ evitado: %{y:,.0f} kt<extra></extra>",
            name="Departamentos",
        ))

        # Línea de tendencia (si hay suficientes puntos)
        if len(dept_corr) > 2:
            z_trend = np.polyfit(dept_corr["inv"], dept_corr["co2"], 1)
            x_trend = np.linspace(dept_corr["inv"].min(), dept_corr["inv"].max(), 50)
            y_trend = np.polyval(z_trend, x_trend)
            fig_sc_ia.add_trace(go.Scatter(
                x=x_trend, y=y_trend,
                mode="lines",
                line=dict(color=P["amber"], width=2, dash="dot"),
                name=f"Tendencia (r={r_inv_co2:.2f})",
                hoverinfo="skip",
            ))

        fig_sc_ia.update_layout(**plotly_base(
            height=380,
            title_text=f"INVERSIÓN vs CO₂ EVITADO · r = {r_inv_co2:.2f} · TAMAÑO = EMPLEOS",
            xaxis_title="INVERSIÓN (MUSD)",
            yaxis_title="CO₂ EVITADO (kt/año)",
        ))
        st.plotly_chart(fig_sc_ia, use_container_width=True)

    # ── Sección 4: Pronóstico demanda nacional ────────────────────────────────
    st.markdown(section_rule("PRONÓSTICO DE DEMANDA ENERGÉTICA NACIONAL · 2026-2035"), unsafe_allow_html=True)
    dem_l, dem_r = st.columns([1.5, 0.5])

    with dem_l:
        cons_nac = df_cons.groupby("anio")["consumo_gwh"].sum().reset_index().sort_values("anio")
        yd = cons_nac["consumo_gwh"].values.astype(float)
        xd = np.arange(len(yd))
        anios_d = cons_nac["anio"].tolist()
        n_d = len(yd)
        n_fc = 9  # proyectar hasta 2035

        # Modelo exponencial demanda
        a_d, b_d, yd_pred, r2_d, rmse_d = fit_exponencial(xd, yd)
        # Modelo polinomial grado 2 demanda
        _, yd_poly, r2_dp, _ = fit_polinomial(xd, yd, 2)
        # Holt demanda
        l_d, fc_d = holt_winters_simple(yd, alpha=0.4, beta=0.3, n_forecast=n_fc)

        anios_d_fut = list(range(anios_d[-1] + 1, anios_d[-1] + n_fc + 1))
        xd_fut = np.arange(n_d, n_d + n_fc)
        yd_fut_exp  = a_d * np.exp(b_d * xd_fut)
        yd_fut_poly = np.maximum(np.polyval(np.polyfit(xd, yd, 2), xd_fut), 0)

        # Bandas
        res_d = yd - yd_pred
        sig_d = np.std(res_d)
        ci_d  = np.linspace(1.0, 2.0, n_fc)
        yd_hi = yd_fut_exp + sig_d * 1.5 * ci_d
        yd_lo = np.maximum(yd_fut_exp - sig_d * 1.2 * ci_d, yd_fut_exp * 0.85)

        fig_dem = go.Figure()
        fig_dem.add_trace(go.Scatter(
            x=anios_d_fut + anios_d_fut[::-1],
            y=list(yd_hi) + list(yd_lo[::-1]),
            fill="toself", fillcolor=_ca(P["ice"], "12"),
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ))
        fig_dem.add_trace(go.Scatter(
            x=anios_d, y=yd,
            mode="lines+markers",
            line=dict(color=P["ice"], width=3),
            marker=dict(size=8, color=P["void"],
                        line=dict(color=P["ice"], width=2.5)),
            fill="tozeroy", fillcolor=_ca(P["ice"], "0A"),
            name="Histórico Real",
            hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>",
        ))
        fig_dem.add_trace(go.Scatter(
            x=anios_d, y=yd_pred,
            mode="lines",
            line=dict(color=P["amber"], width=1.5, dash="dot"),
            name=f"Exp. Ajustado (R²={r2_d:.3f})",
            hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>",
        ))
        fig_dem.add_trace(go.Scatter(
            x=anios_d_fut, y=yd_fut_exp,
            mode="lines",
            line=dict(color=P["amber"], width=2.5, dash="dash"),
            name="Proyección Exponencial",
            hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>",
        ))
        fig_dem.add_trace(go.Scatter(
            x=anios_d_fut, y=fc_d,
            mode="lines",
            line=dict(color=P["neon"], width=2, dash="longdash"),
            name="Holt-Winters",
            hovertemplate="%{x}: %{y:,.0f} GWh<extra></extra>",
        ))
        fig_dem.add_vline(
            x=anios_d[-1], line_dash="dot",
            line_color=P["text_lo"], line_width=1.5,
        )
        fig_dem.update_layout(**plotly_base(
            height=340,
            title_text=f"DEMANDA ENERGÉTICA NACIONAL (GWh) · PROYECCIÓN 2026-2035 · CAGR: {b_d*100:.2f}%/AÑO",
            xaxis_title="AÑO", yaxis_title="GWh",
            hovermode="x unified",
        ))
        st.plotly_chart(fig_dem, use_container_width=True)

    with dem_r:
        # KPIs demanda
        gwh_2025 = float(yd[-1])
        gwh_2030 = float(yd_fut_exp[min(4, len(yd_fut_exp)-1)])
        gwh_2035 = float(yd_fut_exp[-1])
        crec_2030 = (gwh_2030 / gwh_2025 - 1) * 100
        crec_2035 = (gwh_2035 / gwh_2025 - 1) * 100

        dem_kpis = [
            ("GWh 2025 (real)", f"{gwh_2025:,.0f}", P["ice"]),
            ("GWh 2030 (proy.)", f"{gwh_2030:,.0f}", P["amber"]),
            ("GWh 2035 (proy.)", f"{gwh_2035:,.0f}", P["neon"]),
            ("Crecimiento 2030", f"+{crec_2030:.1f}%", P["amber"]),
            ("Crecimiento 2035", f"+{crec_2035:.1f}%", P["neon"]),
            (f"R² Exp.", f"{r2_d:.4f}", P["ice"]),
        ]
        for lbl_k, val_k, col_k in dem_kpis:
            h_k = col_k.lstrip("#")
            r_k, g_k, b_k = int(h_k[0:2], 16), int(h_k[2:4], 16), int(h_k[4:6], 16)
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:7px 10px;margin-bottom:4px;background:{P['surface']};"
                f"border:1px solid rgba({r_k},{g_k},{b_k},0.2);border-left:2px solid {col_k};"
                f"border-radius:5px;'>"
                f"<span style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
                f"font-size:9px;letter-spacing:.5px;'>{lbl_k}</span>"
                f"<span style='color:{col_k};font-family:Barlow Condensed,sans-serif;"
                f"font-size:14px;font-weight:700;'>{val_k}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Sección 5: Escenarios 2030 ────────────────────────────────────────────
    st.markdown(section_rule("ESCENARIOS ESTRATÉGICOS CAPACIDAD SOLAR · 2030"), unsafe_allow_html=True)
    escenarios = {
        "Conservador (CAGR 30%)": [1348, 1753, 2279, 2963, 3851],
        "Base (CAGR 50%)":        [1348, 2022, 3033, 4550, 6824],
        "Optimista (CAGR 70%)":   [1348, 2292, 3896, 6623, 11259],
    }
    anios_esc = [2025, 2026, 2027, 2028, 2030]
    colores_esc = [P["text_lo"], P["neon"], P["amber"]]

    fig_esc = go.Figure()
    for (nombre, vals), col_s in zip(escenarios.items(), colores_esc):
        linestyle = "dot" if "Conservador" in nombre else (
            "solid" if "Base" in nombre else "dash")
        fig_esc.add_trace(go.Scatter(
            x=anios_esc, y=vals, name=nombre,
            mode="lines+markers",
            line=dict(color=col_s, width=3 if "Base" in nombre else 2, dash=linestyle),
            marker=dict(size=9, color=P["void"], line=dict(color=col_s, width=2.5)),
            hovertemplate=f"<b>{nombre}</b><br>%{{x}}: %{{y:,.0f}} MW<extra></extra>",
        ))

    fig_esc.add_hline(
        y=6000, line_dash="dash", line_color=P["neon"], line_width=1.5,
        annotation_text="OBJETIVO PLAN 6GW+",
        annotation_font=dict(color=P["neon"], size=10),
    )
    fig_esc.update_layout(**plotly_base(
        height=280,
        title_text="ESCENARIOS CAPACIDAD SOLAR 2025-2030 (MW) · CAGR DIFERENCIAL",
        hovermode="x unified",
        xaxis_title="AÑO", yaxis_title="MW SOLAR",
    ))
    st.plotly_chart(fig_esc, use_container_width=True)

    # ── Resumen de indicadores predictivos ────────────────────────────────────
    st.markdown(section_rule("INDICADORES PREDICTIVOS 2026-2030"), unsafe_allow_html=True)
    ip_cols = st.columns(4)
    ip_data = [
        ("Prob. déficit generación 2026",  "34%",         P["alert"], "Riesgo alto por El Niño"),
        ("LCOE Solar proyectado 2027",      "38 USD/MWh",  P["neon"],  "vs 42 USD/MWh actual"),
        ("Empleos verdes adicionales 2028", "48.200",      P["ice"],   "Escenario base UPME"),
        ("CO₂ evitado acumulado 2030",      "85 Mt",       P["neon"],  "Sector eléctrico"),
    ]
    for col_ip, (lbl_i, val_i, col_i, desc_i) in zip(ip_cols, ip_data):
        h_i = col_i.lstrip("#")
        r_i, g_i, b_i = int(h_i[0:2], 16), int(h_i[2:4], 16), int(h_i[4:6], 16)
        col_ip.markdown(
            f"<div style='background:linear-gradient(145deg,{P['raised']},{P['surface']});"
            f"border:1px solid rgba({r_i},{g_i},{b_i},0.2);border-top:2px solid {col_i};"
            f"border-radius:8px;padding:14px;text-align:center;'>"
            f"<div style='color:{col_i};font-family:Barlow Condensed,sans-serif;"
            f"font-size:24px;font-weight:800;'>{val_i}</div>"
            f"<div style='color:{P['text_mid']};font-size:11px;margin:5px 0 4px;font-weight:600;'>{lbl_i}</div>"
            f"<div style='color:{P['text_lo']};font-size:10px;font-family:JetBrains Mono,monospace;'>{desc_i}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 7 · ZONAS NO INTERCONECTADAS (ZNI)
# ──────────────────────────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown(neon_header(
        "🗺", "Zonas No Interconectadas — Cobertura Eléctrica",
        subtitle="diagnóstico de acceso energético en territorios alejados del SIN",
        badge="IPSE · ZNI",
    ), unsafe_allow_html=True)

    # KPIs ZNI
    zk = st.columns(5)
    _con_srv  = df_zni[df_zni["con_servicio"] == True]["horas_dia"]
    _avg_h    = float(_con_srv.mean()) if len(_con_srv) > 0 else float("nan")
    _avg_h_lbl = f"{_avg_h:.1f}h" if not (pd.isna(_avg_h) or _avg_h != _avg_h) else "N/D"
    _sin_proy = int((df_zni["tiene_proyecto"] == False).sum())
    zk[0].metric("Total ZNI",       len(df_zni))
    zk[1].metric("Sin Servicio",    int((df_zni["con_servicio"] == False).sum()))
    zk[2].metric("Población Total", f"{int(df_zni['poblacion'].sum()):,}")
    zk[3].metric("Horas Prom/día",  _avg_h_lbl)
    zk[4].metric("Sin Proyecto",    _sin_proy)

    z1, z2 = st.columns(2)
    with z1:
        df_zs = df_zni.sort_values("horas_dia", ascending=False)
        fig_z1 = go.Figure()
        fig_z1.add_trace(go.Bar(
            x=df_zs["zona"], y=df_zs["horas_dia"],
            marker_color=[P["neon"] if c else P["alert"] for c in df_zs["con_servicio"]],
            customdata=df_zs[["departamento","poblacion","con_servicio","tiene_proyecto"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>Depto: %{customdata[0]}<br>"
                "Población: %{customdata[1]:,}<br>"
                "Con servicio: %{customdata[2]}<br>"
                "Con proyecto: %{customdata[3]}<br>"
                "Horas/día: <b>%{y}</b><extra></extra>"
            ),
        ))
        fig_z1.add_hline(y=24, line_dash="dot", line_color=P["text_lo"],
                          annotation_text="24h ideal")
        fig_z1.add_hline(y=12, line_dash="dash", line_color=P["amber"],
                          line_width=1.5, annotation_text="12h mínimo",
                          annotation_font=dict(color=P["amber"]))
        fig_z1.update_layout(**plotly_base(
            height=360, title_text="HORAS DE SERVICIO POR ZONA ZNI",
            xaxis_tickangle=-30, yaxis_title="Horas / día",
        ))
        st.plotly_chart(fig_z1, use_container_width=True)

    with z2:
        con_s = int(df_zni["con_servicio"].sum())
        sin_s = int((df_zni["con_servicio"]==False).sum())
        fig_z2 = go.Figure(go.Pie(
            labels=["Con Servicio","Sin Servicio"],
            values=[con_s, sin_s], hole=0.62,
            marker=dict(colors=[P["neon"], P["alert"]],
                        line=dict(color=P["void"], width=2)),
            textinfo="label+value+percent", textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>%{value} zonas<extra></extra>",
        ))
        fig_z2.add_annotation(
            text=f"<b>{len(df_zni)}</b>", x=0.5, y=0.56, showarrow=False,
            font=dict(size=24, color=P["neon"], family="Barlow Condensed,sans-serif"),
        )
        fig_z2.add_annotation(
            text="ZONAS ZNI", x=0.5, y=0.42, showarrow=False,
            font=dict(size=9, color=P["text_lo"], family="JetBrains Mono,monospace"),
        )
        fig_z2.update_layout(**plotly_base(
            height=360, title_text="COBERTURA ELÉCTRICA ZNI",
        ))
        st.plotly_chart(fig_z2, use_container_width=True)

    z3, z4 = st.columns(2)
    with z3:
        # Población por departamento y cobertura
        pop_dept = (df_zni.groupby(["departamento","con_servicio"])["poblacion"]
                    .sum().reset_index())
        fig_z3 = go.Figure()
        for cs, nom, col in [(True,"Con Servicio",P["neon"]),(False,"Sin Servicio",P["alert"])]:
            sub = pop_dept[pop_dept["con_servicio"]==cs]
            fig_z3.add_trace(go.Bar(
                x=sub["departamento"], y=sub["poblacion"],
                name=nom, marker_color=col,
                hovertemplate=f"<b>{nom}</b><br>%{{x}}: %{{y:,}} hab<extra></extra>",
            ))
        fig_z3.update_layout(**plotly_base(
            barmode="stack", height=300,
            title_text="POBLACIÓN ZNI POR DEPARTAMENTO Y COBERTURA",
            xaxis_tickangle=-25, yaxis_title="Personas",
        ))
        st.plotly_chart(fig_z3, use_container_width=True)

    with z4:
        # Asignación de proyectos
        df_zni2 = df_zni.copy()
        cnt = (df_zni2.groupby(["departamento","tiene_proyecto"])
               .size().reset_index(name="zonas"))
        fig_z4 = go.Figure()
        for tp, nom, col in [(True,"Con Proyecto",P["neon"]),(False,"Sin Proyecto",P["alert"])]:
            sub = cnt[cnt["tiene_proyecto"]==tp]
            fig_z4.add_trace(go.Bar(
                x=sub["departamento"], y=sub["zonas"],
                name=nom, marker_color=col,
                hovertemplate=f"<b>{nom}</b><br>%{{x}}: %{{y}} zonas<extra></extra>",
            ))
        fig_z4.update_layout(**plotly_base(
            barmode="group", height=300,
            title_text="ASIGNACIÓN DE PROYECTOS EN ZONAS ZNI",
            xaxis_tickangle=-25, yaxis_title="Zonas",
        ))
        st.plotly_chart(fig_z4, use_container_width=True)

    with st.expander("📋  TABLA DETALLADA ZNI"):
        st.dataframe(
            df_zni[["zona","departamento","region","poblacion",
                    "con_servicio","horas_dia","tiene_proyecto"]]
            .sort_values("horas_dia"),
            use_container_width=True, hide_index=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 8 · ANÁLISIS COMPARATIVO
# ──────────────────────────────────────────────────────────────────────────────
with tabs[8]:
    st.markdown(neon_header(
        "📊", "Análisis Comparativo y Correlaciones",
        subtitle="índice de transición · radar regional · correlaciones multivariable",
    ), unsafe_allow_html=True)

    an1, an2 = st.columns(2)
    with an1:
        # df_proy tiene departamento + capacidad_mw + region (df_cap NO los tiene)
        _renov = (df_proy[df_proy["tipo"].isin(["Solar","Eólica","Biomasa"])]
                  .groupby("departamento")["capacidad_mw"].sum().reset_index()
                  .rename(columns={"capacidad_mw":"mw_renov"}))
        _total = (df_proy.groupby("departamento")["capacidad_mw"].sum().reset_index()
                  .rename(columns={"capacidad_mw":"mw_total"}))
        idx_df = _renov.merge(_total, on="departamento", how="outer").fillna(0)
        idx_df["pct"] = (idx_df["mw_renov"] /
                         idx_df["mw_total"].replace(0, 1) * 100).round(1)
        idx_df = idx_df.merge(
            df_proy.groupby("departamento")["empleos"].sum().reset_index(),
            on="departamento", how="left").fillna(0)
        idx_df = idx_df.merge(
            df_proy.groupby("departamento")["inversion_musd"].sum().reset_index(),
            on="departamento", how="left").fillna(0)
        idx_df = idx_df.sort_values("mw_renov", ascending=False)
        _reg_map = (df_proy.drop_duplicates("departamento")
                    .set_index("departamento")["region"].to_dict())
        idx_df["region"] = idx_df["departamento"].map(
            lambda d: _reg_map.get(d, "Otra"))

        fig_an1 = go.Figure(go.Bar(
            x=idx_df["departamento"], y=idx_df["mw_renov"],
            marker=dict(
                color=[REGION_COLORS.get(r, P["text_lo"]) for r in idx_df["region"]],
                opacity=0.88, line=dict(color=P["void"], width=0.5),
            ),
            text=[f"{v:,.0f}" for v in idx_df["mw_renov"]],
            textposition="outside",
            textfont=dict(size=8, color=P["text_lo"]),
            customdata=idx_df[["mw_total","pct","empleos","inversion_musd"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>MW Renovable: <b>%{y:,.0f}</b><br>"
                "MW Total: %{customdata[0]:,.0f}<br>"
                "%% Renovable: %{customdata[1]:.1f}%%<br>"
                "Empleos: %{customdata[2]:,.0f}<br>"
                "Inversión: USD %{customdata[3]:,.0f}M<extra></extra>"
            ),
            name="MW Renovable",
        ))
        fig_an1.update_layout(**plotly_base(
            height=380, title_text=f"MW RENOVABLES POR DEPARTAMENTO · {anio_sel}",
            xaxis_tickangle=-35, yaxis_title="MW",
        ))
        st.plotly_chart(fig_an1, use_container_width=True)

    with an2:
        # Radar comparativo por región
        cats = ["Capacidad","Inversión","Empleo","Diversif."]
        fig_radar = go.Figure()
        for reg in REGION_COLORS:
            # df_cap no tiene region — usar df_proy para todo lo regional
            dp = df_proy[df_proy["region"]==reg]
            dc_cons = df_cons[(df_cons["region"]==reg) & (df_cons["anio"]==anio_sel)]
            vals = [
                dp["capacidad_mw"].sum(),
                dp["inversion_musd"].sum(),
                dp["empleos"].sum(),
                dp["tipo"].nunique() * 10,
            ]
            mx = [max(v,1) for v in vals]
            # normalizar por max global
            vals_n = vals
            col_r = REGION_COLORS[reg]
            h = col_r.lstrip("#")
            r_v,g_v,b_v = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_n + vals_n[:1],
                theta=cats + cats[:1],
                fill="toself",
                fillcolor=f"rgba({r_v},{g_v},{b_v},0.12)",
                line=dict(color=col_r, width=2),
                name=reg,
                hovertemplate=f"<b>{reg}</b><br>%{{theta}}: %{{r:,.0f}}<extra></extra>",
            ))
        fig_radar.update_layout(**plotly_base(
            height=380, title_text="ÍNDICE COMPARATIVO POR REGIÓN",
            polar=dict(
                bgcolor=P["surface"],
                radialaxis=dict(visible=True, gridcolor=P["grid"],
                                tickfont=dict(size=8)),
                angularaxis=dict(gridcolor=P["grid"]),
            ),
        ))
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Correlación capacidad vs inversión vs empleos ──────────────────────────
    st.markdown(section_rule("CORRELACIÓN MULTIVARIABLE"), unsafe_allow_html=True)
    corr_df = (df_proy.groupby("departamento")
               .agg(cap=("capacidad_mw","sum"),
                    inv=("inversion_musd","sum"),
                    emp=("empleos","sum"),
                    n=("nombre","count"))
               .reset_index())

    fig_corr = px.scatter(
        corr_df, x="cap", y="inv", size="emp", color="n",
        text="departamento", size_max=50,
        color_continuous_scale=[[0,P["surface"]],[0.5,P["ice"]],[1,P["neon"]]],
        labels={"cap":"Capacidad MW","inv":"Inversión MUSD","n":"N° Proyectos"},
        template="plotly_dark",
    )
    fig_corr.update_traces(
        textposition="top center",
        textfont=dict(size=8, color=P["text_lo"]),
        marker=dict(line=dict(color=P["void"], width=1)),
    )
    fig_corr.update_layout(**plotly_base(
        height=380,
        title_text="CORRELACIÓN: CAPACIDAD (MW) vs INVERSIÓN (MUSD) — TAMAÑO = EMPLEOS",
        xaxis_title="CAPACIDAD (MW)", yaxis_title="INVERSIÓN (MUSD)",
    ))
    st.plotly_chart(fig_corr, use_container_width=True)

    # ── Heatmap mix energético por región ─────────────────────────────────────
    st.markdown(section_rule("HEATMAP MIX ENERGÉTICO POR REGIÓN"), unsafe_allow_html=True)
    hm_l, hm_r = st.columns(2)
    with hm_l:
        # df_proy tiene region + tipo (fuente) + capacidad_mw
        piv_rf = (df_proy[df_proy["estado"].isin(["Operativo","En Constr."])]
                  .groupby(["region","tipo"])["capacidad_mw"]
                  .sum().unstack(fill_value=0))
        fig_hm1 = go.Figure(go.Heatmap(
            z=piv_rf.values, x=piv_rf.columns.tolist(), y=piv_rf.index.tolist(),
            colorscale=[[0,P["deep"]],[0.3,P["ice_mid"]],[0.7,P["neon"]],[1,P["amber"]]],
            text=[[f"{v:,.0f}" for v in row] for row in piv_rf.values],
            texttemplate="%{text}", textfont=dict(size=9, color=P["void"]),
            hovertemplate="Región: %{y}<br>Tipo: %{x}<br>%{z:,.0f} MW<extra></extra>",
            colorbar=dict(tickfont=dict(color=P["text_lo"],size=9),thickness=12),
        ))
        fig_hm1.update_layout(**plotly_base(
            height=300, title_text=f"CAPACIDAD (MW) POR REGIÓN Y FUENTE · {anio_sel}",
            xaxis_tickangle=-20,
        ))
        st.plotly_chart(fig_hm1, use_container_width=True)

    with hm_r:
        # Consumo GWh por región y año (df_cons tiene region)
        piv_cons_year = (df_cons.groupby(["region","anio"])["consumo_gwh"]
                         .sum().unstack(fill_value=0))
        fig_hm2 = go.Figure(go.Heatmap(
            z=piv_cons_year.values,
            x=[str(int(a)) for a in piv_cons_year.columns],
            y=piv_cons_year.index.tolist(),
            colorscale=[[0,P["deep"]],[0.4,P["raised"]],[0.7,P["ice"]],[1,P["neon"]]],
            text=[[f"{v:,.0f}" for v in row] for row in piv_cons_year.values],
            texttemplate="%{text}", textfont=dict(size=9, color=P["void"]),
            hovertemplate="Región: %{y}<br>Año: %{x}<br>%{z:,.0f} GWh<extra></extra>",
            colorbar=dict(tickfont=dict(color=P["text_lo"],size=9),thickness=12),
        ))
        fig_hm2.update_layout(**plotly_base(
            height=300, title_text="CONSUMO ENERGÉTICO (GWh) POR REGIÓN Y AÑO",
            xaxis_title="AÑO", yaxis_title="REGIÓN",
        ))
        st.plotly_chart(fig_hm2, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 9 · FNCER 2025 — Datos.gov.co en tiempo real
# ──────────────────────────────────────────────────────────────────────────────
with tabs[9]:
    st.markdown(neon_header(
        "🔋", "FNCER 2024-2025 — Contexto y Proyectos Destacados",
        subtitle="datos UPME · Plan 6GW+ · proyectos en operación y construcción",
        badge="UPME · PLAN 6GW+",
        badge_col=P["neon"],
    ), unsafe_allow_html=True)

    # KPIs contexto 2024
    ctx_data = [
        ("Capacidad Solar Operativa", "1.348 MW", P["amber"], "☀"),
        ("Total FNCER Operativo",     "2.079 MW", P["neon"],  "⚡"),
        ("Crecimiento Solar 2024",    "+187%",    P["amber"],  "📈"),
        ("Avance Meta PND 2026",      "80%",      P["ice"],   "🎯"),
        ("Proyectos Activos 6GW+",    "82",       P["neon"],  "🏗"),
        ("Factor Emisión SIN",        "160 gCO₂/kWh", P["neon"], "🌿"),
    ]
    ctx_cols = st.columns(6)
    for col_c, (lbl, val, col, ico) in zip(ctx_cols, ctx_data):
        h = col.lstrip("#")
        r_c, g_c, b_c = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        col_c.markdown(
            f"<div style='background:linear-gradient(145deg,{P['raised']},{P['surface']});"
            f"border:1px solid {col};border-top:2px solid {col};"
            f"border-radius:10px;padding:14px;text-align:center;'>"
            f"<div style='font-size:22px;margin-bottom:6px;'>{ico}</div>"
            f"<div style='color:{col};font-family:Barlow Condensed,sans-serif;"
            f"font-size:22px;font-weight:800;'>{val}</div>"
            f"<div style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
            f"font-size:8px;letter-spacing:1.5px;margin-top:4px;'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)

    # Proyectos destacados 2024
    st.markdown(section_rule("PROYECTOS ESTRELLA 2024 — UPME"), unsafe_allow_html=True)
    proyectos_2024 = [
        ("LATAM Solar La Loma",    150, "Cesar",      "Solar Fotovoltaica", P["amber"]),
        ("Portón del Sol",         102, "Caldas",     "Solar Fotovoltaica", P["amber"]),
        ("Solar La Unión",         100, "Córdoba",    "Solar Fotovoltaica", P["amber"]),
        ("Guajira 1 Wind Farm",    198, "La Guajira", "Eólica",             P["ice"]),
        ("Jepírachi II",           204, "La Guajira", "Eólica",             P["ice"]),
    ]
    pd_cols = st.columns(5)
    for col_pd, (nom, mw, dept, tipo, col) in zip(pd_cols, proyectos_2024):
        h = col.lstrip("#")
        r_c,g_c,b_c = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
        col_pd.markdown(
            f"<div style='background:linear-gradient(145deg,{P['raised']},{P['surface']});"
            f"border:1px solid rgba({r_c},{g_c},{b_c},0.3);border-top:2px solid {col};"
            f"border-radius:10px;padding:14px;text-align:center;'>"
            f"<div style='color:{col};font-family:Barlow Condensed,sans-serif;"
            f"font-size:26px;font-weight:800;'>{mw} MW</div>"
            f"<div style='color:{P['text_hi']};font-size:11px;font-weight:600;"
            f"margin:6px 0 4px;line-height:1.3;'>{nom}</div>"
            f"<div style='color:{P['text_lo']};font-size:10px;'>{dept}</div>"
            f"<div style='color:{col};font-size:9px;margin-top:5px;"
            f"font-family:JetBrains Mono,monospace;letter-spacing:.5px;'>{tipo}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)

    # Evolución capacidad solar + proyección
    st.markdown(section_rule("EVOLUCIÓN Y PROYECCIÓN CAPACIDAD SOLAR"), unsafe_allow_html=True)
    fn1, fn2 = st.columns([1.4, 0.6])
    with fn1:
        solar_h = df_cap[df_cap["fuente"]=="Solar"].sort_values("anio")
        anios_p = list(range(2018, 2031))
        mw_h    = solar_h["capacidad_mw"].tolist()
        # Proyección simple exponencial
        import math as _math
        gr = (mw_h[-1]/mw_h[0]) ** (1/(len(mw_h)-1))
        mw_proj = [mw_h[-1] * gr**(i) for i in range(1, len(anios_p)-len(mw_h)+1)]

        fig_fn1 = go.Figure()
        # Área histórica
        fig_fn1.add_trace(go.Scatter(
            x=solar_h["anio"].tolist(), y=mw_h,
            mode="lines+markers", name="Histórico",
            line=dict(color=P["amber"], width=3),
            marker=dict(size=8, color=P["void"], line=dict(color=P["amber"],width=2.5)),
            fill="tozeroy", fillcolor=f"rgba(255,176,32,0.12)",
        ))
        # Proyección
        fig_fn1.add_trace(go.Scatter(
            x=anios_p[len(mw_h)-1:], y=[mw_h[-1]]+mw_proj,
            mode="lines", name="Proyección",
            line=dict(color=P["amber"], width=2.5, dash="dot"),
        ))
        fig_fn1.add_hline(y=6000, line_dash="dash",
                           line_color=P["neon"], line_width=1.5,
                           annotation_text="OBJETIVO 6GW+",
                           annotation_font=dict(color=P["neon"],size=10))
        fig_fn1.add_vline(x=2026, line_dash="dot",
                           line_color=P["text_lo"], line_width=1)
        fig_fn1.update_layout(**plotly_base(
            height=340,
            title_text="CAPACIDAD SOLAR INSTALADA Y PROYECCIÓN 2026-2030 (MW)",
            xaxis_title="AÑO", yaxis_title="MW",
        ))
        st.plotly_chart(fig_fn1, use_container_width=True)

    with fn2:
        # Donut FNCER vs convencional
        fncer_mw  = df_cap[(df_cap["fuente"].isin(["Solar","Eólica","Biomasa"])) &
                            (df_cap["anio"]==anio_sel)]["capacidad_mw"].sum()
        hidro_mw  = df_cap[(df_cap["fuente"]=="Hidroeléctrica") &
                            (df_cap["anio"]==anio_sel)]["capacidad_mw"].sum()
        conv_mw   = df_cap[(df_cap["fuente"].isin(["Gas Natural","Carbón"])) &
                            (df_cap["anio"]==anio_sel)]["capacidad_mw"].sum()
        fig_fn2 = go.Figure(go.Pie(
            labels=["FNCER","Hídrica","Convencional"],
            values=[fncer_mw, hidro_mw, conv_mw],
            hole=0.60,
            marker=dict(colors=[P["neon"], P["ice"], "#78909C"],
                        line=dict(color=P["void"], width=2)),
            textinfo="percent+label", textfont=dict(size=10),
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} MW · %{percent}<extra></extra>",
        ))
        fig_fn2.add_annotation(
            text=f"<b>{fncer_mw:,.0f}</b>",
            x=0.5, y=0.58, showarrow=False,
            font=dict(size=20, color=P["neon"], family="Barlow Condensed,sans-serif"),
        )
        fig_fn2.add_annotation(
            text="MW FNCER",
            x=0.5, y=0.42, showarrow=False,
            font=dict(size=9, color=P["text_lo"], family="JetBrains Mono,monospace"),
        )
        fig_fn2.update_layout(**plotly_base(
            height=340, title_text=f"MATRIZ POR CATEGORÍA · {anio_sel}",
        ))
        st.plotly_chart(fig_fn2, use_container_width=True)

    # CO2 evitado por proyecto
    st.markdown(section_rule("ESTIMACIÓN CO₂ EVITADO POR PROYECTO"), unsafe_allow_html=True)
    # Factor emisión SIN: 160 gCO2/kWh = 0.00016 tCO2/kWh
    # Capacidad × factor planta × horas → energía × factor emisión
    FACTORES = {"Solar":0.22,"Eólica":0.35,"Hidroeléctrica":0.45,
                "Biomasa":0.60,"Gas Natural":0.00,"Carbón":0.00,"Geotérmica":0.90}
    df_co2 = df_proy[df_proy["estado"].isin(["Operativo","En Constr."])].copy()
    df_co2["energia_gwh_anio"] = (df_co2["capacidad_mw"] *
                                   df_co2["tipo"].map(FACTORES).fillna(0) * 8760 / 1000)
    df_co2["co2_evitado_kt"]   = df_co2["energia_gwh_anio"] * 160 / 1e6 * 1000
    co2_dept = (df_co2.groupby("departamento")["co2_evitado_kt"]
                .sum().reset_index()
                .sort_values("co2_evitado_kt", ascending=False).head(12))

    fig_co2 = go.Figure(go.Bar(
        x=co2_dept["departamento"], y=co2_dept["co2_evitado_kt"],
        marker=dict(
            color=co2_dept["co2_evitado_kt"],
            colorscale=[[0,P["surface"]],[0.5,P["neon_dim"]],[1,P["neon"]]],
            showscale=False,
            line=dict(color=P["void"], width=0.5),
        ),
        text=[f"{v:,.0f} kt" for v in co2_dept["co2_evitado_kt"]],
        textposition="outside",
        textfont=dict(size=9, color=P["text_lo"]),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} kt CO₂/año evitadas<extra></extra>",
    ))
    fig_co2.update_layout(**plotly_base(
        height=300,
        title_text="CO₂ EVITADO POR DEPARTAMENTO (kt/año estimado)",
        xaxis_tickangle=-30, yaxis_title="kt CO₂/año",
    ))
    st.plotly_chart(fig_co2, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 10 · EXPLORADOR DE DATOS Y EXPORTACIÓN
# ──────────────────────────────────────────────────────────────────────────────
with tabs[10]:
    st.markdown(neon_header(
        "📂", "Explorador de Datos y Exportación",
        subtitle="consulta, filtra y descarga los conjuntos de datos del sistema",
    ), unsafe_allow_html=True)

    datasets = {
        "Capacidad Instalada": df_cap,
        "Emisiones CO₂":       df_emis,
        "Consumo Energético":  df_cons,
        "Proyectos ERNC":      df_proy,
        "Zonas ZNI":           df_zni,
    }

    ds_sel = st.selectbox("Seleccionar dataset", list(datasets.keys()), key="ds_sel")
    df_sel = datasets[ds_sel].copy()

    search = st.text_input("🔍 Búsqueda libre (filtra todas las columnas)", "", key="ds_search")
    if search:
        mask = df_sel.apply(
            lambda c: c.astype(str).str.contains(search, case=False, na=False)
        ).any(axis=1)
        df_sel = df_sel[mask]

    st.markdown(
        f"<p style='color:{P['text_lo']};font-family:JetBrains Mono,monospace;"
        f"font-size:11px;'>{len(df_sel):,} registros &nbsp;·&nbsp; "
        f"{len(df_sel.columns)} columnas</p>",
        unsafe_allow_html=True,
    )

    st_l, st_r = st.columns([1, 2])
    with st_l:
        num_cols = df_sel.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            st.markdown(
                f"<b style='color:{P['amber']};font-family:Barlow Condensed,sans-serif;"
                f"font-size:13px;'>ESTADÍSTICAS</b>",
                unsafe_allow_html=True,
            )
            st.dataframe(df_sel[num_cols].describe().round(2),
                         use_container_width=True)
    with st_r:
        st.markdown(
            f"<b style='color:{P['amber']};font-family:Barlow Condensed,sans-serif;"
            f"font-size:13px;'>VISTA DE DATOS</b>",
            unsafe_allow_html=True,
        )
        st.dataframe(df_sel, use_container_width=True, hide_index=True, height=320)

    # Gráfico rápido contextual
    if "capacidad_mw" in df_sel.columns and "departamento" in df_sel.columns:
        quick = (df_sel.groupby("departamento")["capacidad_mw"]
                 .sum().sort_values(ascending=False).head(10))
        fig_q = go.Figure(go.Bar(
            x=quick.index, y=quick.values,
            marker_color=P["neon"],
            hovertemplate="<b>%{x}</b><br>%{y:,.1f} MW<extra></extra>",
        ))
        fig_q.update_layout(**plotly_base(
            height=260, title_text="TOP 10 POR CAPACIDAD MW",
            xaxis_tickangle=-30,
        ))
        st.plotly_chart(fig_q, use_container_width=True)
    elif "consumo_gwh" in df_sel.columns:
        quick2 = df_sel.groupby("region")["consumo_gwh"].sum().sort_values(ascending=False)
        fig_q2 = go.Figure(go.Bar(
            x=quick2.index, y=quick2.values,
            marker_color=[REGION_COLORS.get(r, P["text_lo"]) for r in quick2.index],
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} GWh<extra></extra>",
        ))
        fig_q2.update_layout(**plotly_base(
            height=260, title_text="CONSUMO POR REGIÓN (GWh)",
        ))
        st.plotly_chart(fig_q2, use_container_width=True)
    elif "mt_co2" in df_sel.columns:
        quick3 = df_sel.groupby("sector")["mt_co2"].sum().sort_values(ascending=False)
        fig_q3 = go.Figure(go.Bar(
            x=quick3.index, y=quick3.values,
            marker=dict(
                color=quick3.values,
                colorscale=[[0,P["surface"]],[0.5,P["amber"]],[1,P["alert"]]],
                showscale=False,
            ),
            hovertemplate="<b>%{x}</b><br>%{y:.3f} Mt CO₂<extra></extra>",
        ))
        fig_q3.update_layout(**plotly_base(
            height=260, title_text="EMISIONES POR SECTOR (Mt CO₂)",
        ))
        st.plotly_chart(fig_q3, use_container_width=True)

    # Descarga CSV
    csv_data = df_sel.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"⬇  Descargar {ds_sel} como CSV",
        data=csv_data,
        file_name=f"siten_colombia_{ds_sel.lower().replace(' ','_')}_{anio_sel}.csv",
        mime="text/csv",
    )



# ══════════════════════════════════════════════════════════════════════════════
# 8 · FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="
    margin-top:32px;
    padding:18px 26px;
    background:linear-gradient(135deg,{P['deep']},{P['surface']},{P['deep']});
    border-radius:10px;
    border:1px solid {P['rim']};
    position:relative;overflow:hidden;">
  <div style="
      position:absolute;top:0;left:0;right:0;height:1px;
      background:linear-gradient(90deg,
          transparent,rgba(0,255,157,0.25),rgba(0,229,255,0.25),transparent);"></div>
  <div style="display:flex;justify-content:space-between;
              flex-wrap:wrap;gap:12px;align-items:center;">
    <div>
      <div style="color:{P['neon']};
          font-family:Barlow Condensed,sans-serif;
          font-size:12px;font-weight:700;letter-spacing:2px;
          margin-bottom:6px;">SITEN · SISTEMA INTELIGENCIA ENERGÉTICA NACIONAL</div>
      <div style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;
          font-size:9px;letter-spacing:.5px;line-height:1.9;">
        📡 UPME — Plan 6GW+ / Meta FNCER (vy9n-w6hc) &nbsp;·&nbsp;
        📡 IPSE — Cobertura ZNI &nbsp;·&nbsp;
        📡 IDEAM — Inventario GEI<br>
        📡 DANE — DIVIPOLA &nbsp;·&nbsp;
        📡 XM — Despacho SIN &nbsp;·&nbsp;
        📡 CREG — Resoluciones tarifarias
      </div>
    </div>
    <div style="text-align:right;">
      <div style="color:{P['text_lo']};font-family:JetBrains Mono,monospace;
          font-size:9px;line-height:2;">
        🛠 Python 3 · Streamlit · Plotly · PyDeck · Pandas<br>
        🎓 Bootcamp Talento Tech · Nivel Integrador 2025<br>
        🌐 <a href="https://dashboard-energia-dqn2cld55x2mawyjlgqund.streamlit.app/"
              style="color:{P['neon']};text-decoration:none;">Dashboard Live ↗</a>
            &nbsp;·&nbsp;
            <a href="https://github.com/eliasibjuliogarcia/dashboard-energia"
              style="color:{P['ice']};text-decoration:none;">GitHub ↗</a>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
