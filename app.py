# app.py — Dashboard Transición Energética Colombia v4
# Streamlit · Plotly · MySQL | Bootcamp Talento Tech — Nivel Integrador

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from database import (load_capacidad, load_consumo, load_emisiones,
                      load_proyectos, load_zni)
from theme import (C, FUENTE_COLORES, REGION_COLORES, SECTOR_COLORES,
                   ESTADO_COLORES, base_layout, title_html, kpi_card, divider)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Transicion Energetica Colombia",
    page_icon="🔋", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600&display=swap');
  html, body, [class*="css"] {{ font-family:'Source Sans 3',sans-serif; background:{C['bg']}; }}
  h1,h2,h3,h4 {{ font-family:'Playfair Display',serif; }}
  [data-testid="stSidebar"] {{ background:linear-gradient(180deg,{C['bg3']},{C['bg2']}); border-right:1px solid {C['border']}; }}
  [data-testid="metric-container"] {{ background:linear-gradient(135deg,{C['bg2']},{C['bg3']}); border:1px solid {C['border']}; border-radius:10px; padding:14px 16px; }}
  [data-testid="metric-container"] label {{ color:{C['subtext']} !important; font-size:11px !important; letter-spacing:1px; }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{ color:{C['accent']} !important; font-family:'Playfair Display',serif !important; font-size:22px !important; }}
  .stTabs [data-baseweb="tab-list"] {{ background:{C['bg3']}; border-radius:10px; padding:4px; gap:3px; border:1px solid {C['border']}; }}
  .stTabs [data-baseweb="tab"] {{ color:{C['subtext']}; border-radius:8px; padding:8px 14px; font-size:12px; }}
  .stTabs [aria-selected="true"] {{ background:{C['bg2']} !important; color:{C['accent']} !important; border-bottom:2px solid {C['accent']} !important; }}
  .stButton > button {{ background:linear-gradient(135deg,{C['bg2']},{C['bg3']}); border:1px solid {C['accent']}; color:{C['accent']}; border-radius:8px; transition:all 0.2s; }}
  .stButton > button:hover {{ background:{C['accent']}; color:{C['bg']}; }}
  ::-webkit-scrollbar {{ width:5px; height:5px; }}
  ::-webkit-scrollbar-track {{ background:{C['bg3']}; }}
  ::-webkit-scrollbar-thumb {{ background:{C['border']}; border-radius:4px; }}
  .insight-box {{ background:linear-gradient(135deg,{C['bg2']},{C['bg3']}); border:1px solid {C['border']}; border-left:3px solid {C['accent']}; border-radius:8px; padding:14px 18px; margin:8px 0; }}
  .alert-box {{ background:linear-gradient(135deg,#1a0d0d,#2a1212); border-left:3px solid {C['red']}; border-radius:8px; padding:12px 16px; margin:5px 0; }}
  .solution-box {{ background:linear-gradient(135deg,#0a1f12,#0d2a1a); border-left:3px solid {C['green']}; border-radius:8px; padding:12px 16px; margin:5px 0; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def cargar_todo():
    return (load_capacidad(), load_consumo(), load_emisiones(),
            load_proyectos(), load_zni())

with st.spinner("Conectando con la base de datos..."):
    df_cap, df_consumo, df_emis, df_proy, df_zni = cargar_todo()

ANIOS    = sorted(df_cap["anio"].unique().tolist())
REGIONES = sorted(df_cap["region"].unique().tolist())
FUENTES  = sorted(df_cap["fuente"].unique().tolist())
DEPTOS   = sorted(df_cap["departamento"].unique().tolist())
SECTORES = sorted(df_consumo["sector"].unique().tolist())

def calc_cagr(df, fuente):
    sub = df[df["fuente"] == fuente].sort_values("anio")
    if len(sub) < 2: return None
    v0, vn = sub["capacidad_mw"].iloc[0], sub["capacidad_mw"].iloc[-1]
    n = sub["anio"].iloc[-1] - sub["anio"].iloc[0]
    return round((vn/v0)**(1/n)-1, 4)*100 if v0 > 0 and n > 0 else None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:14px 0 8px;">
      <div style="font-size:36px;">🔋</div>
      <div style="color:{C['accent']};font-family:'Playfair Display',serif;font-size:15px;font-weight:700;line-height:1.3;">
        Transicion Energetica<br>Colombia
      </div>
      <div style="color:{C['subtext']};font-size:10px;letter-spacing:2px;margin-top:4px;">DASHBOARD ANALITICO</div>
    </div>
    <hr style="border-color:{C['border']};margin:10px 0;">
    """, unsafe_allow_html=True)

    g_anio = st.select_slider("Ano de analisis", options=ANIOS, value=max(ANIOS))
    g_regiones = st.multiselect("Regiones", options=REGIONES, default=REGIONES)
    g_tipo = st.multiselect("Tipo de fuente",
        options=["renovable","no_renovable","alternativa"],
        default=["renovable","alternativa"])

    st.markdown(f"<hr style='border-color:{C['border']};margin:10px 0;'>", unsafe_allow_html=True)
    st.caption("datos.gov.co — IPSE / UPME / IDEAM / DANE")
    cr, cg = st.columns(2)
    cr.metric("Registros", f"{len(df_cap)+len(df_consumo)+len(df_emis)+len(df_proy)+len(df_zni):,}")
    cg.metric("Tablas BD", "7")

# ══════════════════════════════════════════════════════════════════════════════
# HEADER + KPIs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:linear-gradient(135deg,{C['bg3']},{C['bg2']},{C['bg3']});
            padding:22px 26px;border-radius:14px;border:1px solid {C['border']};
            margin-bottom:18px;border-left:5px solid {C['accent']};">
  <h1 style="color:{C['accent']};font-family:'Playfair Display',serif;margin:0;font-size:24px;">
    Analisis de la Transicion Energetica en Colombia
  </h1>
  <p style="color:{C['subtext']};margin:4px 0 0;font-size:12px;letter-spacing:1px;">
    datos.gov.co  |  Python / MySQL / Streamlit / Plotly  |  Bootcamp Talento Tech - Nivel Integrador 2025
  </p>
</div>
""", unsafe_allow_html=True)

cap_f = df_cap[(df_cap["anio"]==g_anio)&(df_cap["region"].isin(g_regiones))&(df_cap["tipo"].isin(g_tipo))]
con_f = df_consumo[(df_consumo["anio"]==g_anio)&(df_consumo["region"].isin(g_regiones))]
emi_f = df_emis[(df_emis["anio"]==g_anio)&(df_emis["region"].isin(g_regiones))]

k = st.columns(7)
k[0].metric("Cap. Renovable",  f"{cap_f['capacidad_mw'].sum():,.0f} MW")
k[1].metric("Proy. Activos",   f"{int(cap_f['proyectos_activos'].sum()):,}")
k[2].metric("En Construccion", f"{int(cap_f['proyectos_en_construccion'].sum()):,}")
k[3].metric("Consumo",         f"{con_f['consumo_gwh'].sum():,.0f} GWh")
k[4].metric("Emisiones CO2",   f"{emi_f['mt_co2'].sum():.2f} Mt")
k[5].metric("Empleos ERNC",    f"{int(df_proy['empleos_generados'].sum()):,}")
k[6].metric("Inversion ERNC",  f"USD {df_proy['inversion_musd'].sum():,.0f}M")

st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "Problematica y Solucion",
    "Capacidad Renovable",
    "Evolucion Temporal",
    "Mapas de Calor",
    "Consumo y Costos",
    "Emisiones CO2",
    "Proyectos ERNC",
    "Zonas ZNI",
    "Analisis Comparativo",
    "Datos y Exportar",
])

# ── TAB 0: PROBLEMATICA Y SOLUCION ────────────────────────────────────────────
with tabs[0]:
    st.markdown(f"<h2 style='color:{C['accent']};font-family:Playfair Display,serif;'>Problematica y Solucion Integrada</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C['subtext']};'>Transicion energetica justa · Democratizacion · Comunidades energeticas</p>", unsafe_allow_html=True)

    col_prob, col_sol = st.columns(2, gap="large")
    with col_prob:
        st.markdown(f"<h3 style='color:{C['red']};'>La Problematica</h3>", unsafe_allow_html=True)
        problemas = [
            ("Dependencia hidrica", C["hidro"],
             "El 70% de la generacion depende de hidroelectricas, vulnerable a sequias por El Nino."),
            ("Inequidad tarifaria", C["red"],
             "El costo en ZNI supera $1.250 COP/kWh, 2x mas que en ciudades (~$600)."),
            ("Meta NDC en riesgo", C["solar"],
             "Colombia se comprometio a reducir 51% de GEI al 2030. Transporte e industria siguen creciendo."),
            ("Brecha territorial", C["geot"],
             "Choco, Amazonas y Vaupes tienen 8-10h/dia de servicio electrico con generacion diesel costosa."),
            ("Concentracion regional", C["neutral"],
             "Antioquia concentra mas del 45% de capacidad renovable. La transicion es geograficamente desigual."),
        ]
        for titulo, color, desc in problemas:
            st.markdown(f"""
            <div class="alert-box" style="border-left:3px solid {color};">
              <b style="color:{color};">{titulo}</b>
              <p style="color:{C['subtext']};font-size:12px;margin:3px 0 0;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    with col_sol:
        st.markdown(f"<h3 style='color:{C['green']};'>La Solucion Integrada</h3>", unsafe_allow_html=True)
        soluciones = [
            ("Integracion de datos", C["green"],
             "Base de datos relacional MySQL que unifica IPSE + UPME + IDEAM + DANE en 7 tablas normalizadas con mas de 200 registros."),
            ("Analisis multidimensional", C["accent"],
             "8 consultas SQL complejas con JOINs multiples, ventanas temporales LAG() y KPIs derivados con Pandas."),
            ("Georreferenciacion ZNI", C["eolica"],
             "Identificacion de zonas sin servicio y cuantificacion de la poblacion afectada por region y departamento."),
            ("Monitoreo NDC", C["solar"],
             "Seguimiento de emisiones CO2 vs meta de reduccion del 51% comprometida ante la ONU al 2030."),
            ("Pipeline de inversion", C["green"],
             "Analisis del pipeline ERNC: USD 9.800M y proyectos que generaran mas de 4.000 empleos directos."),
            ("Recomendaciones basadas en datos", C["accent"],
             "Indice de transicion por departamento para priorizar donde intervenir primero con politica publica."),
        ]
        for titulo, color, desc in soluciones:
            st.markdown(f"""
            <div class="solution-box" style="border-left:3px solid {color};">
              <b style="color:{color};">{titulo}</b>
              <p style="color:{C['subtext']};font-size:12px;margin:3px 0 0;">{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{C['accent']};font-family:Playfair Display,serif;'>Impacto Esperado de las Recomendaciones</h3>", unsafe_allow_html=True)
    i1,i2,i3,i4 = st.columns(4)
    impactos = [
        (i1,"Hibridizacion ZNI","Reemplazar diesel por solar+bateria en zonas sin servicio",C["green"],"~$650 COP/kWh de ahorro"),
        (i2,"Aceleracion Solar","La Guajira puede triplicar su cap. solar al 2027",C["solar"],"CAGR sostenido >60%"),
        (i3,"Hub Eolico Caribe","Atlantico+Guajira: hub eolico regional",C["eolica"],">800 MW proyectados a 2025"),
        (i4,"Meta NDC","El sector electrico puede llegar a la meta con el pipeline actual",C["red"],"51% de reduccion al 2030"),
    ]
    for col_i,titulo,desc,color,resultado in impactos:
        col_i.markdown(f"""
        <div style="background:{C['bg2']};border:1px solid {color};border-top:3px solid {color};
                    border-radius:10px;padding:14px;min-height:140px;">
          <div style="color:{color};font-size:13px;font-weight:bold;margin-bottom:6px;">{titulo}</div>
          <div style="color:{C['text']};font-size:11px;line-height:1.6;margin-bottom:8px;">{desc}</div>
          <div style="color:{color};font-size:10px;font-weight:bold;border-top:1px solid {C['border']};padding-top:6px;">
            {resultado}
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{C['accent']};font-family:Playfair Display,serif;'>Flujo Metodologico</h3>", unsafe_allow_html=True)
    pasos = ["1. Identificacion\nProblematica","2. Recoleccion\ndatos.gov.co","3. Diseno BD\nMySQL 3FN",
             "4. ETL\nPython/Pandas","5. Analisis SQL\nComplejo","6. Visualizacion\nStreamlit","7. Recomendaciones\nbasadas en datos"]
    colores_p = [C["neutral"],C["eolica"],C["hidro"],C["biomasa"],C["solar"],C["accent"],C["green"]]
    pcols = st.columns(len(pasos))
    for col_p, paso, cp in zip(pcols, pasos, colores_p):
        col_p.markdown(f"""
        <div style="background:{C['bg2']};border:1px solid {cp};border-top:3px solid {cp};
                    border-radius:8px;padding:10px 6px;text-align:center;">
          <div style="color:{cp};font-size:10px;font-weight:bold;white-space:pre-line;line-height:1.5;">{paso}</div>
        </div>""", unsafe_allow_html=True)

# ── TAB 1: CAPACIDAD RENOVABLE ────────────────────────────────────────────────
with tabs[1]:
    st.markdown(f"<h2 style='color:{C['accent']};'>"
                f"Capacidad Instalada de Energias Renovables — {g_anio}</h2>",
                unsafe_allow_html=True)

    # ── Filtros ───────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1, 1, 0.8])
    with c1:
        top_n = st.slider("Top departamentos", 3, 17, 10, key="cap_top")
    with c2:
        cap_fuentes_sel = st.multiselect("Fuentes", FUENTES, default=FUENTES, key="cap_f")
    with c3:
        cap_orden = st.radio("Ordenar por",
                             ["Capacidad MW", "Inversion", "Proyectos"],
                             horizontal=True, key="cap_ord")

    # ── Dataset filtrado (usa TODO df_cap, no solo cap_f del año) ─────────────
    df_c = df_cap[
        (df_cap["anio"] == g_anio) &
        (df_cap["region"].isin(g_regiones)) &
        (df_cap["tipo"].isin(g_tipo))
    ]
    if cap_fuentes_sel:
        df_c = df_c[df_c["fuente"].isin(cap_fuentes_sel)]

    orden_col = {"Capacidad MW": "cap_mw", "Inversion": "inversion",
                 "Proyectos": "proyectos"}[cap_orden]

    rank = (df_c.groupby(["departamento", "region"])
            .agg(cap_mw=("capacidad_mw","sum"),
                 proyectos=("proyectos_activos","sum"),
                 en_constr=("proyectos_en_construccion","sum"),
                 inversion=("inversion_bill_cop","sum"))
            .reset_index()
            .sort_values(orden_col, ascending=False)
            .head(top_n))

    if rank.empty:
        st.warning("Sin datos para los filtros seleccionados.")
    else:
        rank["pct"] = (rank["cap_mw"] / rank["cap_mw"].sum() * 100).round(1)

    por_fuente = (df_c.groupby("fuente")["capacidad_mw"].sum()
                  .reset_index()
                  .sort_values("capacidad_mw", ascending=False))

    # ── Fila 1: Barras horizontales + Donut ───────────────────────────────────
    col_bar, col_pie = st.columns([0.58, 0.42])

    with col_bar:
        if rank.empty:
            st.info("Sin datos de ranking.")
        else:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=rank["cap_mw"],
                y=rank["departamento"],
                orientation="h",
                marker_color=[REGION_COLORES.get(r, C["neutral"]) for r in rank["region"]],
                text=[f"{v:,.0f} MW ({p}%)"
                      for v, p in zip(rank["cap_mw"], rank["pct"])],
                textposition="outside",
                textfont=dict(size=9, color=C["subtext"]),
                customdata=rank[["region","proyectos","en_constr","inversion"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>Region: %{customdata[0]}<br>"
                    "Capacidad: %{x:,.0f} MW<br>"
                    "Proy. activos: %{customdata[1]}<br>"
                    "En construccion: %{customdata[2]}<br>"
                    "Inversion: %{customdata[3]:.2f} B.COP<extra></extra>"
                ),
                showlegend=False,
            ))
            for reg, rc in REGION_COLORES.items():
                fig_bar.add_trace(go.Bar(
                    x=[None], y=[None], name=reg,
                    marker_color=rc, showlegend=True))
            fig_bar.update_layout(**base_layout(
                height=440,
                title_text=f"🏆 Top {top_n} Departamentos por {cap_orden}",
                legend=dict(x=0.60, y=0.02),
                xaxis=dict(gridcolor=C["grid"]),
                yaxis=dict(categoryorder="total ascending", gridcolor=C["grid"]),
            ))
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_pie:
        if por_fuente.empty:
            st.info("Sin datos.")
        else:
            fig_pie = go.Figure(go.Pie(
                labels=por_fuente["fuente"],
                values=por_fuente["capacidad_mw"],
                hole=0.55,
                marker=dict(
                    colors=[FUENTE_COLORES.get(f, C["neutral"])
                            for f in por_fuente["fuente"]],
                    line=dict(color=C["bg"], width=2),
                ),
                textinfo="label+percent",
                textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>%{value:,.1f} MW · %{percent}<extra></extra>",
            ))
            total_mw = por_fuente["capacidad_mw"].sum()
            fig_pie.update_layout(**base_layout(
                height=440,
                title_text="🔋 Mix por Fuente Energetica",
                annotations=[dict(
                    text=f"<b>{total_mw:,.0f}</b><br>MW total",
                    x=0.5, y=0.5,
                    font=dict(size=13, color=C["accent"]),
                    showarrow=False,
                )],
            ))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── Fila 2: Mapa de Colombia + Inversión por región ───────────────────────
    st.markdown(
        f"<h3 style='color:{C['accent2']};margin-top:8px;'>"
        "🗺️ Mapa de Capacidad Renovable por Departamento — Colombia</h3>",
        unsafe_allow_html=True,
    )

    col_mapa, col_inv = st.columns([1.1, 0.9])

    with col_mapa:
        # Coordenadas aproximadas de capitales de departamentos colombianos
        COORDS = {
            "Antioquia":           (6.2518,  -75.5636),
            "Atlantico":           (10.9685, -74.7813),
            "Bogota D.C.":         (4.7110,  -74.0721),
            "Bolivar":             (8.6462,  -74.0346),
            "Boyaca":              (5.5353,  -73.3678),
            "Caldas":              (5.0703,  -75.5138),
            "Caqueta":             (1.6144,  -75.6062),
            "Cauca":               (2.4448,  -76.6147),
            "Cesar":               (10.4631, -73.2532),
            "Choco":               (5.6919,  -76.6583),
            "Cordoba":             (8.7479,  -75.8814),
            "Cundinamarca":        (4.9987,  -74.0041),
            "Huila":               (2.5359,  -75.5277),
            "La Guajira":          (11.5444, -72.9072),
            "Magdalena":           (10.4113, -74.4057),
            "Meta":                (4.1533,  -73.6350),
            "Narino":              (1.2136,  -77.2811),
            "Norte de Santander":  (7.8939,  -72.5078),
            "Quindio":             (4.4610,  -75.6674),
            "Risaralda":           (4.8133,  -75.6961),
            "Santander":           (7.1193,  -73.1227),
            "Sucre":               (8.8112,  -74.7233),
            "Tolima":              (4.4389,  -75.2322),
            "Valle del Cauca":     (3.8010,  -76.6413),
            "Casanare":            (5.3389,  -72.3947),
            "Amazonas":            (-1.4436, -71.5724),
            "Guainia":             (2.5854,  -68.5247),
            "Guaviare":            (2.0836,  -72.6406),
            "Vaupes":              (0.8554,  -70.8119),
            "Vichada":             (4.4236,  -69.2879),
        }

        # Construir dataframe del mapa
        df_mapa = (df_cap[
                       (df_cap["anio"] == g_anio) &
                       (df_cap["tipo"].isin(["renovable","alternativa"]))
                   ]
                   .groupby("departamento")["capacidad_mw"]
                   .sum()
                   .reset_index())
        df_mapa["lat"] = df_mapa["departamento"].map(
            lambda d: COORDS.get(d, (4.5, -74.0))[0])
        df_mapa["lon"] = df_mapa["departamento"].map(
            lambda d: COORDS.get(d, (4.5, -74.0))[1])
        df_mapa["size"] = (df_mapa["capacidad_mw"] / df_mapa["capacidad_mw"].max() * 50 + 5).fillna(5)

        # Proyectos del pipeline
        df_proy_mapa = (df_proy
                        .groupby("departamento")
                        .agg(n_proy=("nombre_proyecto","count"),
                             inv=("inversion_musd","sum"))
                        .reset_index())
        df_mapa = df_mapa.merge(df_proy_mapa, on="departamento", how="left").fillna(0)

        fig_mapa = go.Figure()

        # Burbujas de capacidad instalada
        fig_mapa.add_trace(go.Scattergeo(
            lat=df_mapa["lat"],
            lon=df_mapa["lon"],
            mode="markers+text",
            marker=dict(
                size=df_mapa["size"],
                color=df_mapa["capacidad_mw"],
                colorscale=[[0, C["bg2"]], [0.3, C["eolica"]],
                            [0.7, C["solar"]], [1, C["green"]]],
                showscale=True,
                colorbar=dict(
                    title="MW Renovable",
                    tickfont=dict(color=C["text"], size=10),
                    bgcolor=C["bg2"],
                    bordercolor=C["border"],
                    x=1.02,
                ),
                line=dict(color=C["bg"], width=1),
                opacity=0.85,
            ),
            text=df_mapa["departamento"],
            textposition="top center",
            textfont=dict(size=8, color=C["text"]),
            customdata=df_mapa[["capacidad_mw","n_proy","inv"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Capacidad: %{customdata[0]:,.0f} MW<br>"
                "Proyectos ERNC: %{customdata[1]:.0f}<br>"
                "Inversion: USD %{customdata[2]:,.0f}M<extra></extra>"
            ),
            name="Capacidad renovable",
        ))

        # Marcadores especiales para proyectos Mision Transmision
        mision_pts = [
            (11.5444, -72.9072, "La Guajira — Hub Eolico/Solar", "★ 850 MW eolica + 498 MW solar"),
            (10.9685, -74.7813, "Atlantico — Solar Caribe",       "★ 280 MW solar en operacion"),
            (2.4448,  -76.6147, "Cauca — Hidroelectrica",          "★ 1.100 MW instalados"),
            (6.2518,  -75.5636, "Antioquia — Ituango",             "★ 2.400 MW en construccion"),
            (4.4389,  -75.2322, "Tolima — Solar Central",          "★ 196 MW operativo"),
        ]
        fig_mapa.add_trace(go.Scattergeo(
            lat=[p[0] for p in mision_pts],
            lon=[p[1] for p in mision_pts],
            mode="markers",
            marker=dict(
                size=16, symbol="star",
                color=C["solar"],
                line=dict(color="white", width=1),
            ),
            text=[p[2] for p in mision_pts],
            customdata=[[p[3]] for p in mision_pts],
            hovertemplate="<b>%{text}</b><br>%{customdata[0]}<extra></extra>",
            name="Mision Transmision ★",
        ))

        fig_mapa.update_layout(
            height=480,
            paper_bgcolor=C["bg"],
            plot_bgcolor=C["bg"],
            font=dict(family="Georgia, serif", color=C["text"], size=11),
            title=dict(
                text="Capacidad Renovable Instalada por Departamento",
                font=dict(size=14, color=C["accent"], family="Georgia, serif"),
                x=0.01,
            ),
            geo=dict(
                scope="south america",
                center=dict(lat=4.5, lon=-74.5),
                projection_scale=5.5,
                showland=True,
                landcolor="#1a2744",
                showocean=True,
                oceancolor="#0a1628",
                showcountries=True,
                countrycolor="#2D3250",
                showlakes=False,
                bgcolor=C["bg"],
                resolution=50,
                lataxis=dict(range=[-5, 15]),
                lonaxis=dict(range=[-82, -65]),
            ),
            legend=dict(
                x=0.01, y=0.99,
                bgcolor="rgba(13,27,42,0.85)",
                bordercolor=C["border"],
                borderwidth=1,
                font=dict(size=10),
            ),
            hoverlabel=dict(
                bgcolor=C["bg3"], bordercolor=C["accent"],
                font=dict(color=C["text"], size=12),
            ),
            margin=dict(l=0, r=0, t=50, b=0),
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

        st.markdown(
            f"<p style='color:{C['subtext']};font-size:11px;'>"
            "★ Proyectos prioritarios Mision Transmision UPME · "
            "Tamaño = Capacidad instalada · Color = MW renovables</p>",
            unsafe_allow_html=True,
        )

    with col_inv:
        # Inversión apilada por región y fuente
        inv_reg = df_c.groupby(["region", "fuente"])["inversion_bill_cop"].sum().reset_index()
        fig_inv = go.Figure()
        for fuente in inv_reg["fuente"].unique():
            sub = inv_reg[inv_reg["fuente"] == fuente]
            fig_inv.add_trace(go.Bar(
                x=sub["region"], y=sub["inversion_bill_cop"],
                name=fuente,
                marker_color=FUENTE_COLORES.get(fuente, C["neutral"]),
                hovertemplate=f"<b>{fuente}</b><br>%{{x}}: %{{y:.2f}} B.COP<extra></extra>",
            ))
        fig_inv.update_layout(**base_layout(
            barmode="stack", height=220,
            title_text="💰 Inversion por Region y Fuente (Billones COP)",
            xaxis_title="Region", yaxis_title="B.COP",
        ))
        st.plotly_chart(fig_inv, use_container_width=True)

        # Diversificación de fuentes
        div_df = (df_c.groupby("departamento")["fuente"]
                  .nunique()
                  .reset_index(name="n_fuentes")
                  .sort_values("n_fuentes", ascending=False)
                  .head(12))
        fig_div = go.Figure(go.Bar(
            x=div_df["departamento"],
            y=div_df["n_fuentes"],
            marker=dict(
                color=div_df["n_fuentes"],
                colorscale=[[0, C["bg2"]], [0.5, C["eolica"]], [1, C["green"]]],
                showscale=False,
            ),
            text=div_df["n_fuentes"],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y} tipos de fuente<extra></extra>",
        ))
        fig_div.update_layout(**base_layout(
            height=230,
            title_text="🌈 Diversificacion de Fuentes por Depto",
            xaxis_tickangle=-30,
            yaxis_title="N° tipos",
        ))
        st.plotly_chart(fig_div, use_container_width=True)

    with st.expander("📋 Ver tabla completa"):
        if not rank.empty:
            st.dataframe(
                rank.rename(columns={
                    "cap_mw": "MW", "proyectos": "Activos",
                    "en_constr": "En Constr.", "inversion": "B.COP",
                }),
                use_container_width=True, hide_index=True,
            )

# ── TAB 2: EVOLUCION TEMPORAL ─────────────────────────────────────────────────
with tabs[2]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Evolucion Historica por Fuente 2019-2023</h2>", unsafe_allow_html=True)
    e1,e2,e3,e4 = st.columns([1.4,1.4,1,1])
    with e1: ev_fuentes = st.multiselect("Fuentes",FUENTES,default=FUENTES[:3],key="ev_f")
    with e2: ev_deptos = st.multiselect("Departamento",["Todos"]+DEPTOS,default=["Todos"],key="ev_d")
    with e3:
        EV_M = {"Capacidad (MW)":"capacidad_mw","Proyectos activos":"proyectos_activos",
                "En construccion":"proyectos_en_construccion","Inversion (B.COP)":"inversion_bill_cop"}
        ev_m_label = st.selectbox("Metrica",list(EV_M.keys()),key="ev_m")
    with e4: ev_chart = st.radio("Grafico",["Area","Lineas","Barras"],horizontal=True,key="ev_c")

    df_ev = df_cap.copy()
    if "Todos" not in ev_deptos and ev_deptos: df_ev=df_ev[df_ev["departamento"].isin(ev_deptos)]
    if ev_fuentes: df_ev=df_ev[df_ev["fuente"].isin(ev_fuentes)]
    col_m = EV_M[ev_m_label]

    agg_ev = df_ev.groupby(["anio","fuente"])[col_m].sum().reset_index()
    fig_ev = go.Figure()
    for fuente in (ev_fuentes or FUENTES):
        sub = agg_ev[agg_ev["fuente"]==fuente].sort_values("anio")
        if sub.empty: continue
        color = FUENTE_COLORES.get(fuente,C["neutral"])
        kw = dict(x=sub["anio"],y=sub[col_m],name=fuente,
            line=dict(color=color,width=2.5),
            marker=dict(size=8,color=C["bg"],line=dict(color=color,width=2.5)),
            hovertemplate=f"<b>{fuente}</b><br>%{{x}}: %{{y:,.1f}}<extra></extra>")
        if ev_chart=="Area":
            try:
                r,g,b = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)
                fc = f"rgba({r},{g},{b},0.1)"
            except:
                fc = "rgba(100,100,100,0.1)"
            fig_ev.add_trace(go.Scatter(mode="lines+markers",fill="tozeroy",fillcolor=fc,**kw))
        elif ev_chart=="Lineas":
            fig_ev.add_trace(go.Scatter(mode="lines+markers+text",
                text=[f"{v:,.0f}" for v in sub[col_m]],
                textposition="top center",textfont=dict(size=8,color=color),**kw))
        else:
            fig_ev.add_trace(go.Bar(x=sub["anio"],y=sub[col_m],name=fuente,marker_color=color,
                hovertemplate=f"<b>{fuente}</b><br>%{{x}}: %{{y:,.1f}}<extra></extra>"))

    if ev_chart=="Barras": fig_ev.update_layout(barmode="group")
    for fuente in (ev_fuentes or []):
        cv = calc_cagr(df_ev,fuente)
        if cv:
            sub = agg_ev[agg_ev["fuente"]==fuente].sort_values("anio")
            if not sub.empty:
                color = FUENTE_COLORES.get(fuente,C["neutral"])
                fig_ev.add_annotation(x=sub["anio"].iloc[-1],y=sub[col_m].iloc[-1],
                    text=f"CAGR {cv:+.1f}%",font=dict(size=10,color=color),
                    bgcolor=C["bg2"],bordercolor=color,borderwidth=1,borderpad=3,
                    showarrow=True,arrowhead=2,arrowcolor=color,ax=30,ay=-25)

    fig_ev.update_layout(**base_layout(height=420,hovermode="x unified",
        title_text=f"Evolucion — {ev_m_label}",
        xaxis=dict(tickmode="array",tickvals=ANIOS,gridcolor=C["grid"]),
        yaxis=dict(title=ev_m_label,gridcolor=C["grid"])))
    st.plotly_chart(fig_ev, use_container_width=True)

    col_var, col_cagr_t = st.columns([1.5,1])
    with col_var:
        agg_all = df_cap.groupby(["anio","fuente"])["capacidad_mw"].sum().reset_index().sort_values(["fuente","anio"])
        agg_all["yoy"] = agg_all.groupby("fuente")["capacidad_mw"].pct_change()*100
        agg_yoy = agg_all.dropna(subset=["yoy"])
        fig_yoy = go.Figure()
        for fuente in agg_yoy["fuente"].unique():
            sub = agg_yoy[agg_yoy["fuente"]==fuente]
            fig_yoy.add_trace(go.Scatter(x=sub["anio"],y=sub["yoy"],name=fuente,
                mode="lines+markers",line=dict(color=FUENTE_COLORES.get(fuente,C["neutral"]),width=2),marker=dict(size=7),
                hovertemplate=f"<b>{fuente}</b><br>%{{x}}: %{{y:+.1f}}% YoY<extra></extra>"))
        fig_yoy.add_hline(y=0,line_color=C["subtext"],line_dash="dash",line_width=1)
        fig_yoy.update_layout(**base_layout(height=300,hovermode="x unified",
            title_text="Variacion Anual % por Fuente (YoY)",xaxis_title="Ano",yaxis_title="Variacion %"))
        st.plotly_chart(fig_yoy, use_container_width=True)

    with col_cagr_t:
        cagr_data = [(f,calc_cagr(df_cap,f)) for f in FUENTES]
        cagr_df = pd.DataFrame(
            [(f,f"{c:+.1f}%" if c else "N/D","↑" if c and c>0 else "↓") for f,c in cagr_data],
            columns=["Fuente","CAGR 2019-2023","Tendencia"])
        st.markdown(f"<br><b style='color:{C['accent']}'>CAGR por Fuente (2019-2023)</b>", unsafe_allow_html=True)
        st.dataframe(cagr_df,use_container_width=True,hide_index=True,height=300)

# ── TAB 3: MAPAS DE CALOR ─────────────────────────────────────────────────────
with tabs[3]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Mapas de Calor — Analisis Multidimensional</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{C['subtext']};'>Capacidad / Costos / Emisiones / Inversion / Evolucion por departamento</p>", unsafe_allow_html=True)

    hm1, hm2 = st.columns(2)
    with hm1:
        piv1 = df_cap[df_cap["anio"]==g_anio].groupby(["region","fuente"])["capacidad_mw"].sum().unstack().fillna(0)
        fig_h1 = go.Figure(go.Heatmap(
            z=piv1.values,x=piv1.columns.tolist(),y=piv1.index.tolist(),
            colorscale=[[0,C["bg3"]],[0.3,C["eolica"]],[0.7,C["solar"]],[1,C["green"]]],
            text=[[f"{v:,.0f}" for v in row] for row in piv1.values],
            texttemplate="%{text}",textfont=dict(size=10,color="white"),
            hovertemplate="Region: %{y}<br>Fuente: %{x}<br>%{z:,.1f} MW<extra></extra>",
            colorbar=dict(title="MW",tickfont=dict(color=C["text"]))))
        fig_h1.update_layout(**base_layout(height=340,xaxis_tickangle=-25,
            title_text=f"Capacidad Instalada (MW) — {g_anio}",xaxis_title="Fuente",yaxis_title="Region"))
        st.plotly_chart(fig_h1, use_container_width=True)

    with hm2:
        piv2 = df_consumo[df_consumo["anio"]==g_anio].groupby(["region","sector"])["costo_promedio_kwh"].mean().unstack().fillna(0)
        fig_h2 = go.Figure(go.Heatmap(
            z=piv2.values,
            x=[c.replace("_"," ").title() for c in piv2.columns],
            y=piv2.index.tolist(),
            colorscale=[[0,C["bg3"]],[0.3,C["hidro"]],[0.7,C["solar"]],[1,C["red"]]],
            text=[[f"${v:,.0f}" for v in row] for row in piv2.values],
            texttemplate="%{text}",textfont=dict(size=10,color="white"),
            hovertemplate="Region: %{y}<br>Sector: %{x}<br>${%z:,.0f} COP/kWh<extra></extra>",
            colorbar=dict(title="COP/kWh",tickfont=dict(color=C["text"]))))
        fig_h2.update_layout(**base_layout(height=340,xaxis_tickangle=-25,
            title_text=f"Costo Energetico $/kWh COP — {g_anio}",xaxis_title="Sector",yaxis_title="Region"))
        st.plotly_chart(fig_h2, use_container_width=True)

    hm3, hm4 = st.columns(2)
    with hm3:
        piv3 = df_emis.groupby(["anio","sector"])["mt_co2"].sum().unstack().fillna(0)
        fig_h3 = go.Figure(go.Heatmap(
            z=piv3.values,
            x=[c.replace("_"," ").title() for c in piv3.columns],
            y=[str(int(a)) for a in piv3.index],
            colorscale=[[0,C["bg3"]],[0.4,C["gas"]],[0.8,C["red"]],[1,"#8B0000"]],
            text=[[f"{v:.2f}" for v in row] for row in piv3.values],
            texttemplate="%{text}",textfont=dict(size=10,color="white"),
            hovertemplate="Ano: %{y}<br>Sector: %{x}<br>%{z:.3f} Mt CO2<extra></extra>",
            colorbar=dict(title="Mt CO2",tickfont=dict(color=C["text"]))))
        fig_h3.update_layout(**base_layout(height=300,xaxis_tickangle=-20,
            title_text="Emisiones CO2 (Mt) por Ano y Sector",xaxis_title="Sector",yaxis_title="Ano"))
        st.plotly_chart(fig_h3, use_container_width=True)

    with hm4:
        piv4 = df_proy.groupby(["departamento","tipo_energia"])["inversion_musd"].sum().unstack().fillna(0)
        fig_h4 = go.Figure(go.Heatmap(
            z=piv4.values,x=piv4.columns.tolist(),y=piv4.index.tolist(),
            colorscale=[[0,C["bg3"]],[0.3,C["neutral"]],[0.7,C["accent"]],[1,C["solar"]]],
            text=[[f"${v:,.0f}M" if v>0 else "" for v in row] for row in piv4.values],
            texttemplate="%{text}",textfont=dict(size=9,color="white"),
            hovertemplate="Depto: %{y}<br>Energia: %{x}<br>USD %{z:,.1f}M<extra></extra>",
            colorbar=dict(title="MUSD",tickfont=dict(color=C["text"]))))
        fig_h4.update_layout(**base_layout(height=300,xaxis_tickangle=-20,
            title_text="Inversion ERNC (MUSD) por Departamento y Tipo",
            xaxis_title="Tipo Energia",yaxis_title="Departamento"))
        st.plotly_chart(fig_h4, use_container_width=True)

    # Heatmap grande: evolucion capacidad renovable departamento x año
    cap_da = df_cap[df_cap["tipo"].isin(["renovable","alternativa"])].groupby(["departamento","anio"])["capacidad_mw"].sum().unstack().fillna(0)
    fig_h5 = go.Figure(go.Heatmap(
        z=cap_da.values,
        x=[str(int(a)) for a in cap_da.columns],
        y=cap_da.index.tolist(),
        colorscale=[[0,C["bg3"]],[0.2,C["bg2"]],[0.5,C["eolica"]],[0.8,C["solar"]],[1,C["green"]]],
        text=[[f"{v:,.0f}" if v>0 else "" for v in row] for row in cap_da.values],
        texttemplate="%{text}",textfont=dict(size=9,color="white"),
        hovertemplate="Departamento: %{y}<br>Ano: %{x}<br>%{z:,.1f} MW<extra></extra>",
        colorbar=dict(title="MW Renovable",tickfont=dict(color=C["text"]))))
    fig_h5.update_layout(**base_layout(height=480,
        title_text="Evolucion de Capacidad Renovable (MW) por Departamento y Ano — Estilo Mision Transmision",
        xaxis_title="Ano",yaxis_title="Departamento"))
    st.plotly_chart(fig_h5, use_container_width=True)

# ── TAB 4: CONSUMO Y COSTOS ───────────────────────────────────────────────────
with tabs[4]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Consumo Energetico y Costos por Sector</h2>", unsafe_allow_html=True)
    cc1,cc2,cc3 = st.columns([1,1.2,1])
    with cc1: cc_reg = st.multiselect("Regiones",REGIONES,default=REGIONES,key="cc_r")
    with cc2: cc_sec = st.multiselect("Sectores",SECTORES,default=SECTORES,key="cc_s")
    with cc3: cc_anio_r = st.slider("Rango anos",min(ANIOS),max(ANIOS),(min(ANIOS),max(ANIOS)),key="cc_a")

    CC_M = {"Consumo (GWh)":"consumo_gwh","Costo COP/kWh":"costo_promedio_kwh","Usuarios":"usuarios"}
    cc_m_label = st.radio("Metrica",list(CC_M.keys()),horizontal=True,key="cc_m")
    col_cc = CC_M[cc_m_label]

    df_cc = df_consumo[(df_consumo["anio"]>=cc_anio_r[0])&(df_consumo["anio"]<=cc_anio_r[1])
                       &(df_consumo["region"].isin(cc_reg))&(df_consumo["sector"].isin(cc_sec))]

    col_a,col_b = st.columns(2)
    with col_a:
        agg_rs = df_cc.groupby(["region","sector"])[col_cc].sum().reset_index()
        fig_cc1 = go.Figure()
        for sec in df_cc["sector"].unique():
            sub = agg_rs[agg_rs["sector"]==sec]
            fig_cc1.add_trace(go.Bar(x=sub["region"],y=sub[col_cc],
                name=sec.replace("_"," ").title(),marker_color=SECTOR_COLORES.get(sec,C["neutral"]),
                hovertemplate=f"<b>{sec}</b><br>%{{x}}: %{{y:,.1f}}<extra></extra>"))
        fig_cc1.update_layout(**base_layout(barmode="stack",height=360,
            title_text=f"{cc_m_label} por Region y Sector",xaxis_title="Region",yaxis_title=cc_m_label))
        st.plotly_chart(fig_cc1, use_container_width=True)

    with col_b:
        agg_a2 = df_cc.groupby(["anio","sector"])[col_cc].sum().reset_index()
        fig_cc2 = go.Figure()
        for sec in df_cc["sector"].unique():
            sub = agg_a2[agg_a2["sector"]==sec].sort_values("anio")
            fig_cc2.add_trace(go.Scatter(x=sub["anio"],y=sub[col_cc],
                name=sec.replace("_"," ").title(),mode="lines+markers",
                line=dict(color=SECTOR_COLORES.get(sec,C["neutral"]),width=2),marker=dict(size=7),
                hovertemplate=f"<b>{sec}</b><br>%{{x}}: %{{y:,.1f}}<extra></extra>"))
        fig_cc2.update_layout(**base_layout(height=360,hovermode="x unified",
            title_text=f"Tendencia Anual — {cc_m_label}",xaxis_title="Ano",yaxis_title=cc_m_label))
        st.plotly_chart(fig_cc2, use_container_width=True)

    col_c,col_d = st.columns(2)
    with col_c:
        agg_tree = df_cc.groupby(["region","sector"])["consumo_gwh"].sum().reset_index()
        if not agg_tree.empty and agg_tree["consumo_gwh"].sum() > 0:
            fig_tree = px.treemap(agg_tree,path=["region","sector"],values="consumo_gwh",
                color="consumo_gwh",color_continuous_scale=[[0,C["bg2"]],[0.5,C["eolica"]],[1,C["solar"]]])
            fig_tree.update_layout(**base_layout(height=300,title_text="Treemap Consumo GWh por Region y Sector"))
            fig_tree.update_traces(textfont=dict(size=11))
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_d:
        fig_box = go.Figure()
        for sec in df_cc["sector"].unique():
            sub = df_cc[df_cc["sector"]==sec]["costo_promedio_kwh"].dropna()
            if sub.empty: continue
            fig_box.add_trace(go.Box(y=sub,name=sec.replace("_"," ").title(),
                marker_color=SECTOR_COLORES.get(sec,C["neutral"]),boxmean=True,
                hovertemplate=f"<b>{sec}</b><br>${{y:,.0f}} COP/kWh<extra></extra>"))
        fig_box.update_layout(**base_layout(height=300,
            title_text="Distribucion de Costos COP/kWh por Sector",yaxis_title="COP/kWh"))
        st.plotly_chart(fig_box, use_container_width=True)

# ── TAB 5: EMISIONES CO2 ──────────────────────────────────────────────────────
with tabs[5]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Emisiones de CO2 — Colombia 2019-2023</h2>", unsafe_allow_html=True)
    em1,em2 = st.columns(2)
    with em1: em_sec = st.multiselect("Sectores",sorted(df_emis["sector"].unique()),default=sorted(df_emis["sector"].unique()),key="em_s")
    with em2: em_dep = st.multiselect("Departamentos",["Todos"]+sorted(df_emis["departamento"].unique()),default=["Todos"],key="em_d")

    df_em = df_emis.copy()
    if "Todos" not in em_dep and em_dep: df_em=df_em[df_em["departamento"].isin(em_dep)]
    if em_sec: df_em=df_em[df_em["sector"].isin(em_sec)]

    col_em1,col_em2 = st.columns(2)
    with col_em1:
        agg_em = df_em.groupby(["anio","sector"])["mt_co2"].sum().reset_index()
        fig_em1 = go.Figure()
        for s in agg_em["sector"].unique():
            sub = agg_em[agg_em["sector"]==s].sort_values("anio")
            fig_em1.add_trace(go.Scatter(x=sub["anio"],y=sub["mt_co2"],
                name=s.replace("_"," ").title(),mode="lines+markers",
                line=dict(color=SECTOR_COLORES.get(s,C["neutral"]),width=2.5),marker=dict(size=8),
                hovertemplate=f"<b>{s}</b><br>%{{x}}: %{{y:.3f}} Mt<extra></extra>"))
        fig_em1.update_layout(**base_layout(height=360,hovermode="x unified",
            title_text="Tendencia Emisiones por Sector",xaxis_title="Ano",yaxis_title="Mt CO2"))
        st.plotly_chart(fig_em1, use_container_width=True)

    with col_em2:
        agg_elec = df_emis[df_emis["sector"]=="energia_electrica"].groupby("anio")["mt_co2"].sum().reset_index()
        base_v = float(agg_elec["mt_co2"].iloc[0]) if len(agg_elec) else 1
        meta = base_v*0.49
        fig_em2 = go.Figure()
        fig_em2.add_trace(go.Scatter(x=agg_elec["anio"],y=agg_elec["mt_co2"],name="Emisiones reales",
            mode="lines+markers",line=dict(color=C["solar"],width=3),
            marker=dict(size=10,color=C["bg"],line=dict(color=C["solar"],width=2.5)),
            fill="tozeroy",fillcolor="rgba(255,183,0,0.08)"))
        fig_em2.add_hline(y=meta,line_dash="dash",line_color=C["green"],line_width=2,
            annotation_text=f"Meta NDC 2030: {meta:.3f} Mt",annotation_font=dict(color=C["green"],size=11))
        fig_em2.update_layout(**base_layout(height=360,
            title_text="Sector Electrico vs Meta NDC (-51%)",xaxis_title="Ano",yaxis_title="Mt CO2"))
        st.plotly_chart(fig_em2, use_container_width=True)

    col_em3,col_em4 = st.columns(2)
    with col_em3:
        agg_ap = df_em.groupby(["anio","sector"])["mt_co2"].sum().reset_index()
        fig_em3 = go.Figure()
        for s in agg_ap["sector"].unique():
            sub = agg_ap[agg_ap["sector"]==s].sort_values("anio")
            fig_em3.add_trace(go.Bar(x=sub["anio"],y=sub["mt_co2"],
                name=s.replace("_"," ").title(),marker_color=SECTOR_COLORES.get(s,C["neutral"])))
        fig_em3.update_layout(**base_layout(barmode="stack",height=300,
            title_text="Emisiones Apiladas por Sector",xaxis_title="Ano",yaxis_title="Mt CO2"))
        st.plotly_chart(fig_em3, use_container_width=True)

    with col_em4:
        agg_dep_em = df_em.groupby("departamento")["mt_co2"].sum().reset_index().sort_values("mt_co2",ascending=False)
        fig_em4 = go.Figure(go.Bar(
            x=agg_dep_em["departamento"],y=agg_dep_em["mt_co2"],
            marker=dict(color=agg_dep_em["mt_co2"],
                colorscale=[[0,C["bg2"]],[0.5,C["gas"]],[1,C["red"]]],showscale=True,
                colorbar=dict(title="Mt CO2",tickfont=dict(color=C["text"]))),
            hovertemplate="<b>%{x}</b><br>%{y:.3f} Mt CO2<extra></extra>"))
        fig_em4.update_layout(**base_layout(height=300,
            title_text="Emisiones Totales por Departamento",
            xaxis_tickangle=-35,xaxis_title="Departamento",yaxis_title="Mt CO2"))
        st.plotly_chart(fig_em4, use_container_width=True)

    # Barras de progreso NDC
    st.markdown(f"<b style='color:{C['accent']}'>Progreso hacia Meta NDC por Sector</b>", unsafe_allow_html=True)
    ndcr = df_emis.groupby(["anio","sector"])["mt_co2"].sum().unstack().fillna(0)
    if len(ndcr) >= 2:
        base_ndc = ndcr.iloc[0]
        last_ndc = ndcr.iloc[-1]
        reduccion = ((base_ndc-last_ndc)/base_ndc*100).fillna(0)
        for sec, red in reduccion.items():
            meta_pct = min(max(red/51*100,0),100)
            color = C["green"] if red>=20 else (C["solar"] if red>=0 else C["red"])
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:4px 0;">
              <div style="color:{C['subtext']};font-size:11px;width:160px;">{sec.replace("_"," ").title()}</div>
              <div style="flex:1;background:{C['bg2']};border-radius:20px;height:14px;overflow:hidden;border:1px solid {C['border']};">
                <div style="width:{meta_pct:.1f}%;background:{color};height:100%;border-radius:20px;"></div>
              </div>
              <div style="color:{color};font-size:11px;width:120px;text-align:right;">{red:+.1f}% de -51% meta</div>
            </div>""", unsafe_allow_html=True)

# ── TAB 6: PROYECTOS ERNC ─────────────────────────────────────────────────────
with tabs[6]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Pipeline de Proyectos ERNC</h2>", unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3)
    with p1: p_est = st.multiselect("Estado",sorted(df_proy["estado"].unique()),default=sorted(df_proy["estado"].unique()),key="p_e")
    with p2: p_tip = st.multiselect("Tipo",sorted(df_proy["tipo_energia"].unique()),default=sorted(df_proy["tipo_energia"].unique()),key="p_t")
    with p3: p_dep = st.multiselect("Departamento",["Todos"]+sorted(df_proy["departamento"].unique()),default=["Todos"],key="p_d")

    df_p = df_proy.copy()
    if p_est: df_p=df_p[df_p["estado"].isin(p_est)]
    if p_tip: df_p=df_p[df_p["tipo_energia"].isin(p_tip)]
    if "Todos" not in p_dep and p_dep: df_p=df_p[df_p["departamento"].isin(p_dep)]

    pk = st.columns(5)
    pk[0].metric("Proyectos",len(df_p))
    pk[1].metric("Capacidad",f"{df_p['capacidad_mw'].sum():,.0f} MW")
    pk[2].metric("Inversion",f"USD {df_p['inversion_musd'].sum():,.0f}M")
    pk[3].metric("Empleos",f"{int(df_p['empleos_generados'].sum()):,}")
    denom = df_p['capacidad_mw'].sum()
    pk[4].metric("USD/MW",f"{df_p['inversion_musd'].sum()/denom*1000:,.0f}K" if denom>0 else "N/D")

    col_p1,col_p2 = st.columns(2)
    with col_p1:
        agg_inv = df_p.groupby(["tipo_energia","estado"]).agg(inv=("inversion_musd","sum"),n=("nombre_proyecto","count")).reset_index()
        fig_p1 = go.Figure()
        for est in agg_inv["estado"].unique():
            sub = agg_inv[agg_inv["estado"]==est]
            fig_p1.add_trace(go.Bar(x=sub["tipo_energia"],y=sub["inv"],
                name=est.replace("_"," ").title(),marker_color=ESTADO_COLORES.get(est,C["neutral"]),
                customdata=sub["n"],
                hovertemplate="<b>%{x}</b><br>USD %{y:,.1f}M<br>Proyectos: %{customdata}<extra></extra>"))
        fig_p1.update_layout(**base_layout(barmode="stack",height=360,
            title_text="Inversion por Tipo y Estado",xaxis_tickangle=-20,yaxis_title="MUSD"))
        st.plotly_chart(fig_p1, use_container_width=True)

    with col_p2:
        fig_p2 = px.scatter(df_p,x="capacidad_mw",y="inversion_musd",
            color="tipo_energia",symbol="estado",size="empleos_generados",size_max=40,
            color_discrete_map=FUENTE_COLORES,hover_name="nombre_proyecto",
            hover_data={"empresa":True,"departamento":True,"capacidad_mw":":.1f","inversion_musd":":.1f"},
            labels={"capacidad_mw":"Capacidad (MW)","inversion_musd":"Inversion (MUSD)","tipo_energia":"Tipo"},
            template="plotly_dark")
        fig_p2.update_layout(**base_layout(height=360,title_text="MW vs Inversion — Tamanio = Empleos"))
        st.plotly_chart(fig_p2, use_container_width=True)

    col_p3,col_p4 = st.columns(2)
    with col_p3:
        emp_dep = df_p.groupby(["departamento","tipo_energia"])["empleos_generados"].sum().reset_index()
        fig_p3 = go.Figure()
        for tip in emp_dep["tipo_energia"].unique():
            sub = emp_dep[emp_dep["tipo_energia"]==tip]
            fig_p3.add_trace(go.Bar(x=sub["departamento"],y=sub["empleos_generados"],
                name=tip,marker_color=FUENTE_COLORES.get(tip,C["neutral"])))
        fig_p3.update_layout(**base_layout(barmode="stack",height=300,
            title_text="Empleos por Departamento y Tipo",xaxis_tickangle=-30,yaxis_title="Empleos"))
        st.plotly_chart(fig_p3, use_container_width=True)

    with col_p4:
        est_cnt = df_proy.groupby("estado").agg(n=("nombre_proyecto","count"),cap=("capacidad_mw","sum")).reset_index()
        est_cnt["estado_label"] = est_cnt["estado"].str.replace("_"," ").str.title()
        fig_p4 = go.Figure(go.Funnel(
            y=est_cnt["estado_label"],x=est_cnt["n"],
            marker=dict(color=[ESTADO_COLORES.get(e,C["neutral"]) for e in est_cnt["estado"]]),
            textinfo="value+percent initial",
            hovertemplate="<b>%{y}</b><br>%{x} proyectos<extra></extra>"))
        fig_p4.update_layout(**base_layout(height=300,title_text="Funnel de Proyectos por Estado"))
        st.plotly_chart(fig_p4, use_container_width=True)

    with st.expander("Tabla completa de proyectos"):
        cols_show = ["nombre_proyecto","empresa","departamento","tipo_energia","estado","capacidad_mw","inversion_musd","empleos_generados","municipio"]
        st.dataframe(df_p[cols_show].sort_values("inversion_musd",ascending=False)
                     .rename(columns={c:c.replace("_"," ").title() for c in cols_show}),
                     use_container_width=True,hide_index=True)

# ── TAB 7: ZONAS ZNI ──────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Zonas No Interconectadas (ZNI)</h2>", unsafe_allow_html=True)
    z1,z2 = st.columns(2)
    with z1: z_reg = st.multiselect("Regiones",REGIONES,default=REGIONES,key="z_r")
    with z2: z_cob = st.radio("Cobertura",["Todas","Con servicio","Sin servicio"],horizontal=True,key="z_c")

    df_z = df_zni[df_zni["region"].isin(z_reg)].copy()
    if z_cob=="Con servicio": df_z=df_z[df_z["tiene_energia"]==True]
    elif z_cob=="Sin servicio": df_z=df_z[df_z["tiene_energia"]==False]

    zk = st.columns(5)
    zk[0].metric("Total ZNI",len(df_z))
    zk[1].metric("Sin Servicio",int((df_z["tiene_energia"]==False).sum()))
    zk[2].metric("Poblacion Total",f"{int(df_z['poblacion'].sum()):,}")
    avg_h = df_z[df_z["tiene_energia"]==True]["horas_servicio_dia"].mean()
    zk[3].metric("Horas Prom/dia",f"{avg_h:.1f}h" if not np.isnan(avg_h) else "N/D")
    zk[4].metric("Sin Proyecto",int(df_z["proyecto_asignado"].isna().sum()))

    col_z1,col_z2 = st.columns(2)
    with col_z1:
        df_zs = df_z.sort_values("horas_servicio_dia",ascending=False)
        fig_z1 = go.Figure()
        fig_z1.add_trace(go.Bar(x=df_zs["nombre_zona"],y=df_zs["horas_servicio_dia"],
            marker_color=[C["green"] if t else C["red"] for t in df_zs["tiene_energia"]],
            customdata=df_zs[["departamento","municipio","fuente_principal","poblacion"]].values,
            hovertemplate="<b>%{x}</b><br>Depto: %{customdata[0]}<br>Municipio: %{customdata[1]}<br>"
                          "Fuente: %{customdata[2]}<br>Poblacion: %{customdata[3]:,}<br>Horas/dia: %{y}<extra></extra>"))
        fig_z1.add_hline(y=24,line_dash="dot",line_color=C["subtext"],annotation_text="24h ideal")
        fig_z1.add_hline(y=12,line_dash="dash",line_color=C["accent"],
            annotation_text="12h minimo",annotation_font=dict(color=C["accent"]))
        fig_z1.update_layout(**base_layout(height=360,
            title_text="Horas de Servicio por Zona",xaxis_tickangle=-30,yaxis_title="Horas / dia"))
        st.plotly_chart(fig_z1, use_container_width=True)

    with col_z2:
        con_s=int(df_z["tiene_energia"].sum())
        sin_s=int((df_z["tiene_energia"]==False).sum())
        fig_z2 = go.Figure(go.Pie(
            labels=["Con Servicio","Sin Servicio"],values=[con_s,sin_s],hole=0.6,
            marker=dict(colors=[C["green"],C["red"]],line=dict(color=C["bg"],width=2)),
            textinfo="label+value+percent",textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>%{value} zonas<extra></extra>"))
        fig_z2.update_layout(**base_layout(height=360,title_text="Cobertura ZNI",
            annotations=[dict(text=f"<b>{len(df_z)}</b><br>zonas",x=0.5,y=0.5,
                font=dict(size=14,color=C["accent"]),showarrow=False)]))
        st.plotly_chart(fig_z2, use_container_width=True)

    col_z3,col_z4 = st.columns(2)
    with col_z3:
        agg_zp = df_z.groupby(["departamento","tiene_energia"])["poblacion"].sum().reset_index()
        fig_z3 = go.Figure()
        for tiene,nombre,color in [(True,"Con Servicio",C["green"]),(False,"Sin Servicio",C["red"])]:
            sub = agg_zp[agg_zp["tiene_energia"]==tiene]
            fig_z3.add_trace(go.Bar(x=sub["departamento"],y=sub["poblacion"],name=nombre,marker_color=color))
        fig_z3.update_layout(**base_layout(barmode="stack",height=300,
            title_text="Poblacion ZNI por Departamento y Cobertura",
            xaxis_tickangle=-25,yaxis_title="Personas"))
        st.plotly_chart(fig_z3, use_container_width=True)

    with col_z4:
        df_z2c = df_z.copy()
        df_z2c["tiene_proyecto"] = df_z2c["proyecto_asignado"].notna()
        cnt = df_z2c.groupby(["departamento","tiene_proyecto"]).size().reset_index(name="zonas")
        fig_z4 = go.Figure()
        for tp,nombre,color in [(True,"Con Proyecto",C["green"]),(False,"Sin Proyecto",C["red"])]:
            sub = cnt[cnt["tiene_proyecto"]==tp]
            fig_z4.add_trace(go.Bar(x=sub["departamento"],y=sub["zonas"],name=nombre,marker_color=color))
        fig_z4.update_layout(**base_layout(barmode="group",height=300,
            title_text="Asignacion de Proyectos en ZNI",xaxis_tickangle=-25,yaxis_title="Zonas"))
        st.plotly_chart(fig_z4, use_container_width=True)

    with st.expander("Tabla detallada ZNI"):
        st.dataframe(df_z[["nombre_zona","departamento","municipio","poblacion",
                            "tiene_energia","horas_servicio_dia","fuente_principal","proyecto_asignado"]],
                     use_container_width=True,hide_index=True)

# ── TAB 8: ANALISIS COMPARATIVO ───────────────────────────────────────────────
with tabs[8]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Analisis Comparativo y Correlaciones</h2>", unsafe_allow_html=True)

    col_an1,col_an2 = st.columns(2)
    with col_an1:
        cap_23 = df_cap[df_cap["anio"]==g_anio]
        renov = cap_23[cap_23["tipo"].isin(["renovable","alternativa"])].groupby("departamento")["capacidad_mw"].sum()
        total = cap_23.groupby("departamento")["capacidad_mw"].sum()
        pct_df = (renov/total*100).fillna(0).reset_index(name="pct")
        emp_d = df_proy.groupby("departamento")["empleos_generados"].sum().reset_index()
        inv_d2 = df_proy.groupby("departamento")["inversion_musd"].sum().reset_index()
        idx = pct_df.merge(emp_d,on="departamento",how="left").merge(inv_d2,on="departamento",how="left").fillna(0)
        idx = idx.sort_values("pct",ascending=False)
        fig_an1 = go.Figure(go.Bar(
            x=idx["departamento"],y=idx["pct"],
            marker=dict(color=idx["pct"],colorscale=[[0,C["red"]],[0.5,C["solar"]],[1,C["green"]]],
                showscale=True,colorbar=dict(title="%",tickfont=dict(color=C["text"]))),
            text=[f"{v:.0f}%" for v in idx["pct"]],textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:.1f}% renovable<extra></extra>"))
        fig_an1.update_layout(**base_layout(height=380,
            title_text=f"% Capacidad Renovable por Departamento ({g_anio})",
            xaxis_tickangle=-40,yaxis_title="% Renovable"))
        st.plotly_chart(fig_an1, use_container_width=True)

    with col_an2:
        inv_e = df_proy.groupby("departamento")["inversion_musd"].sum().reset_index()
        emi_e = df_emis[df_emis["anio"]==g_anio].groupby("departamento")["mt_co2"].sum().reset_index()
        merged = inv_e.merge(emi_e,on="departamento",how="inner")
        corr_v = merged["inversion_musd"].corr(merged["mt_co2"]) if len(merged)>1 else 0
        fig_an2 = px.scatter(merged,x="inversion_musd",y="mt_co2",text="departamento",
            size="inversion_musd",size_max=40,color="mt_co2",color_continuous_scale="RdYlGn_r",
            labels={"inversion_musd":"Inversion ERNC (MUSD)","mt_co2":"Emisiones CO2 (Mt)"},
            template="plotly_dark")
        fig_an2.update_traces(textposition="top center",textfont=dict(size=8,color=C["subtext"]))
        fig_an2.update_layout(**base_layout(height=380,
            title_text=f"Inversion vs Emisiones — r = {corr_v:.2f}"))
        st.plotly_chart(fig_an2, use_container_width=True)

    col_an3,col_an4 = st.columns(2)
    with col_an3:
        cagrs = [(f,calc_cagr(df_cap,f)) for f in FUENTES]
        cagrs = sorted([(f,c) for f,c in cagrs if c is not None],key=lambda x:x[1],reverse=True)
        fig_an3 = go.Figure(go.Bar(
            x=[x[0] for x in cagrs],y=[x[1] for x in cagrs],
            marker=dict(color=[C["green"] if x[1]>=0 else C["red"] for x in cagrs]),
            text=[f"{x[1]:+.1f}%" for x in cagrs],textposition="outside",
            textfont=dict(size=11,color=C["text"]),
            hovertemplate="<b>%{x}</b><br>CAGR: %{y:+.1f}%<extra></extra>"))
        fig_an3.add_hline(y=0,line_color=C["subtext"],line_width=1)
        fig_an3.update_layout(**base_layout(height=340,
            title_text="CAGR por Fuente Energetica (2019-2023)",
            xaxis_tickangle=-25,yaxis_title="CAGR (%)"))
        st.plotly_chart(fig_an3, use_container_width=True)

    with col_an4:
        # Radar por region
        radar_m = ["capacidad_mw","proyectos_activos","proyectos_en_construccion","inversion_bill_cop"]
        radar_l = ["Capacidad MW","Proy. Activos","En Construccion","Inversion B.COP"]
        df_radar = df_cap[df_cap["anio"]==g_anio].groupby("region")[radar_m].sum()
        df_radar_n = df_radar.div(df_radar.max()).fillna(0)
        fig_radar = go.Figure()
        for reg in df_radar_n.index:
            vals = df_radar_n.loc[reg].tolist()+[df_radar_n.loc[reg].tolist()[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,theta=radar_l+[radar_l[0]],name=reg,fill="toself",
                line=dict(color=REGION_COLORES.get(reg,C["neutral"]),width=2),
                hovertemplate=f"<b>{reg}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>"))
        fig_radar.update_layout(**base_layout(height=340,
            title_text=f"Perfil Energetico por Region — {g_anio}",
            polar=dict(bgcolor=C["bg2"],
                radialaxis=dict(visible=True,gridcolor=C["grid"],tickfont=dict(color=C["subtext"])),
                angularaxis=dict(gridcolor=C["grid"],tickfont=dict(color=C["text"])))))
        st.plotly_chart(fig_radar, use_container_width=True)

# ── TAB 9: DATOS Y EXPORTAR ───────────────────────────────────────────────────
with tabs[9]:
    st.markdown(f"<h2 style='color:{C['accent']};'>Explorador de Datos y Exportacion</h2>", unsafe_allow_html=True)
    datasets = {
        "Capacidad Instalada": df_cap,
        "Consumo Energetico":  df_consumo,
        "Emisiones CO2":       df_emis,
        "Proyectos ERNC":      df_proy,
        "Zonas ZNI":           df_zni,
    }
    ds_sel = st.selectbox("Selecciona el dataset",list(datasets.keys()),key="ds_sel")
    df_sel = datasets[ds_sel].copy()

    search = st.text_input("Busqueda libre (filtra todas las columnas texto)", "", key="ds_search")
    if search:
        mask = df_sel.apply(lambda col: col.astype(str).str.contains(search,case=False,na=False)).any(axis=1)
        df_sel = df_sel[mask]

    st.markdown(f"<p style='color:{C['subtext']};font-size:12px;'>{len(df_sel):,} registros / {len(df_sel.columns)} columnas</p>", unsafe_allow_html=True)

    col_stat,col_tabla = st.columns([1,2])
    with col_stat:
        num_cols = df_sel.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            st.markdown(f"<b style='color:{C['accent']}'>Estadisticas numericas</b>", unsafe_allow_html=True)
            st.dataframe(df_sel[num_cols].describe().round(2),use_container_width=True)
    with col_tabla:
        st.markdown(f"<b style='color:{C['accent']}'>Vista de datos</b>", unsafe_allow_html=True)
        st.dataframe(df_sel,use_container_width=True,hide_index=True,height=320)

    csv = df_sel.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"Descargar {ds_sel} como CSV",
        data=csv,
        file_name=f"energia_colombia_{ds_sel.lower().replace(' ','_')}_{g_anio}.csv",
        mime="text/csv")

    # Grafico rapido del dataset
    if "capacidad_mw" in df_sel.columns and "departamento" in df_sel.columns:
        quick = df_sel.groupby("departamento")["capacidad_mw"].sum().sort_values(ascending=False).head(10)
        fig_q = go.Figure(go.Bar(x=quick.index,y=quick.values,marker_color=C["accent"],
            hovertemplate="<b>%{x}</b><br>%{y:,.1f} MW<extra></extra>"))
        fig_q.update_layout(**base_layout(height=250,title_text="Top 10 por Capacidad MW",xaxis_tickangle=-30))
        st.plotly_chart(fig_q, use_container_width=True)
    elif "consumo_gwh" in df_sel.columns:
        quick2 = df_sel.groupby("sector")["consumo_gwh"].sum().sort_values(ascending=False)
        fig_q2 = go.Figure(go.Bar(x=quick2.index,y=quick2.values,
            marker_color=[SECTOR_COLORES.get(s,C["neutral"]) for s in quick2.index],
            hovertemplate="<b>%{x}</b><br>%{y:,.1f} GWh<extra></extra>"))
        fig_q2.update_layout(**base_layout(height=250,title_text="Consumo por Sector (GWh)"))
        st.plotly_chart(fig_q2, use_container_width=True)
    elif "mt_co2" in df_sel.columns:
        quick3 = df_sel.groupby("sector")["mt_co2"].sum().sort_values(ascending=False)
        fig_q3 = go.Figure(go.Bar(x=quick3.index,y=quick3.values,
            marker=dict(color=quick3.values,colorscale=[[0,C["bg2"]],[1,C["red"]]],showscale=False),
            hovertemplate="<b>%{x}</b><br>%{y:.3f} Mt CO2<extra></extra>"))
        fig_q3.update_layout(**base_layout(height=250,title_text="Emisiones por Sector (Mt CO2)"))
        st.plotly_chart(fig_q3, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:24px;padding:14px 22px;background:linear-gradient(135deg,{C['bg3']},{C['bg2']});
            border-radius:10px;border-top:2px solid {C['border']};
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
  <div style="color:{C['subtext']};font-size:11px;">
    datos.gov.co — IPSE / UPME / IDEAM / DANE  |  Python / MySQL / Streamlit / Plotly
  </div>
  <div style="color:{C['subtext']};font-size:11px;">
    Bootcamp Talento Tech — Analisis de Datos — Nivel Integrador 2025
  </div>
</div>
""", unsafe_allow_html=True)
