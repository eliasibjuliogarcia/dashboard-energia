# app.py — Dashboard Transición Energética Colombia
# Streamlit · Plotly · MySQL
# Bootcamp Talento Tech — Nivel Integrador

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
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Transición Energética Colombia",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Proyecto Final — Bootcamp Talento Tech 2025"},
)

# ── CSS global ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Source Sans 3', sans-serif;
      background-color: {C['bg']};
  }}
  h1,h2,h3,h4 {{ font-family: 'Playfair Display', serif; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
      background: linear-gradient(180deg, {C['bg3']} 0%, {C['bg2']} 100%);
      border-right: 1px solid {C['border']};
  }}
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label,
  [data-testid="stSidebar"] .stSlider label,
  [data-testid="stSidebar"] .stRadio label {{
      color: {C['subtext']} !important;
      font-size: 11px !important;
      letter-spacing: 1px;
      text-transform: uppercase;
  }}

  /* Métricas nativas */
  [data-testid="metric-container"] {{
      background: linear-gradient(135deg, {C['bg2']}, {C['bg3']});
      border: 1px solid {C['border']};
      border-radius: 10px;
      padding: 14px 16px;
  }}
  [data-testid="metric-container"] label {{
      color: {C['subtext']} !important;
      font-size: 11px !important;
      letter-spacing: 1px;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
      color: {C['accent']} !important;
      font-family: 'Playfair Display', serif !important;
      font-size: 24px !important;
  }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
      background: {C['bg3']};
      border-radius: 10px;
      padding: 4px;
      gap: 4px;
      border: 1px solid {C['border']};
  }}
  .stTabs [data-baseweb="tab"] {{
      color: {C['subtext']};
      border-radius: 8px;
      padding: 8px 18px;
      font-size: 13px;
  }}
  .stTabs [aria-selected="true"] {{
      background: {C['bg2']} !important;
      color: {C['accent']} !important;
      border-bottom: 2px solid {C['accent']} !important;
  }}

  /* Botones */
  .stButton > button {{
      background: linear-gradient(135deg, {C['bg2']}, {C['bg3']});
      border: 1px solid {C['accent']};
      color: {C['accent']};
      border-radius: 8px;
      font-family: 'Source Sans 3', sans-serif;
      transition: all 0.2s;
  }}
  .stButton > button:hover {{
      background: {C['accent']};
      color: {C['bg']};
      transform: translateY(-1px);
  }}

  /* Contenedor gráfico */
  .graph-container {{
      background: {C['bg2']};
      border: 1px solid {C['border']};
      border-radius: 12px;
      padding: 4px;
      margin-bottom: 16px;
  }}

  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: {C['bg3']}; }}
  ::-webkit-scrollbar-thumb {{ background: {C['border']}; border-radius: 4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: {C['accent']}; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def cargar_todo():
    return (load_capacidad(), load_consumo(), load_emisiones(),
            load_proyectos(), load_zni())

with st.spinner("⚡ Conectando con la base de datos..."):
    df_cap, df_consumo, df_emis, df_proy, df_zni = cargar_todo()

ANIOS      = sorted(df_cap["anio"].unique().tolist())
REGIONES   = sorted(df_cap["region"].unique().tolist())
FUENTES    = sorted(df_cap["fuente"].unique().tolist())
DEPTOS     = sorted(df_cap["departamento"].unique().tolist())
SECTORES   = sorted(df_consumo["sector"].unique().tolist())


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: CAGR
# ══════════════════════════════════════════════════════════════════════════════
def cagr(df, fuente):
    sub = df[df["fuente"] == fuente].sort_values("anio")
    if len(sub) < 2: return None
    v0, vn = sub["capacidad_mw"].iloc[0], sub["capacidad_mw"].iloc[-1]
    n = sub["anio"].iloc[-1] - sub["anio"].iloc[0]
    return round((vn / v0) ** (1 / n) - 1, 4) * 100 if v0 > 0 and n > 0 else None


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTROS GLOBALES
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 8px;">
      <div style="font-size:40px;">🔋</div>
      <div style="color:{C['accent']};font-family:'Playfair Display',serif;
                  font-size:16px;font-weight:700;line-height:1.3;">
        Transición Energética<br>Colombia
      </div>
      <div style="color:{C['subtext']};font-size:10px;letter-spacing:2px;
                  margin-top:4px;">DASHBOARD ANALÍTICO</div>
    </div>
    <hr style="border-color:{C['border']};margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='color:{C['subtext']};font-size:10px;letter-spacing:2px;'>🎛️ FILTROS GLOBALES</div>", unsafe_allow_html=True)
    st.caption("")

    g_anio = st.select_slider(
        "Año de análisis",
        options=ANIOS, value=max(ANIOS),
    )
    g_regiones = st.multiselect(
        "Regiones",
        options=REGIONES,
        default=REGIONES,
    )
    g_tipo = st.multiselect(
        "Tipo de fuente",
        options=["renovable", "no_renovable", "alternativa"],
        default=["renovable", "alternativa"],
    )

    st.markdown(f"<hr style='border-color:{C['border']};margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{C['subtext']};font-size:10px;letter-spacing:2px;'>📊 FUENTE DE DATOS</div>", unsafe_allow_html=True)
    st.caption("datos.gov.co — IPSE · UPME · IDEAM · DANE")

    st.markdown(f"<hr style='border-color:{C['border']};margin:14px 0;'>", unsafe_allow_html=True)
    col_r, col_g = st.columns(2)
    col_r.metric("Registros", f"{len(df_cap)+len(df_consumo)+len(df_emis)+len(df_proy)+len(df_zni):,}")
    col_g.metric("Tablas BD", "7")


# ══════════════════════════════════════════════════════════════════════════════
# HEADER PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:linear-gradient(135deg,{C['bg3']} 0%,{C['bg2']} 60%,{C['bg3']} 100%);
            padding:28px 32px; border-radius:16px;
            border:1px solid {C['border']}; margin-bottom:24px;
            border-left:5px solid {C['accent']};">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
    <div>
      <h1 style="color:{C['accent']};font-family:'Playfair Display',serif;
                 margin:0;font-size:28px;letter-spacing:.5px;">
        Análisis de la Transición Energética en Colombia
      </h1>
      <p style="color:{C['subtext']};margin:6px 0 0;font-size:13px;letter-spacing:1px;">
        📡 datos.gov.co &nbsp;·&nbsp; 🛠️ Python · MySQL · Streamlit · Plotly
        &nbsp;·&nbsp; 🎓 Bootcamp Talento Tech — Nivel Integrador
      </p>
    </div>
    <div style="text-align:right;">
      <div style="color:{C['green']};font-size:12px;font-weight:600;">🟢 BASE DE DATOS CONECTADA</div>
      <div style="color:{C['subtext']};font-size:11px;">Vigencia: 2019 – 2023</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPIs GLOBALES (siempre visibles)
# ══════════════════════════════════════════════════════════════════════════════
cap_f = df_cap[
    (df_cap["anio"] == g_anio) &
    (df_cap["region"].isin(g_regiones)) &
    (df_cap["tipo"].isin(g_tipo))
]
con_f  = df_consumo[(df_consumo["anio"] == g_anio) & (df_consumo["region"].isin(g_regiones))]
emi_f  = df_emis[(df_emis["anio"] == g_anio) & (df_emis["region"].isin(g_regiones))]

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("⚡ Cap. Renovable", f"{cap_f['capacidad_mw'].sum():,.0f} MW")
k2.metric("🏭 Proy. Activos",  f"{int(cap_f['proyectos_activos'].sum()):,}")
k3.metric("🏗️ En Construcción", f"{int(cap_f['proyectos_en_construccion'].sum()):,}")
k4.metric("💡 Consumo",        f"{con_f['consumo_gwh'].sum():,.0f} GWh")
k5.metric("🌿 Emisiones CO₂",  f"{emi_f['mt_co2'].sum():.2f} Mt")
k6.metric("💼 Empleos ERNC",   f"{int(df_proy['empleos_generados'].sum()):,}")

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "⚡ Capacidad Renovable",
    "📈 Evolución Temporal",
    "💡 Consumo & Costos",
    "🌿 Emisiones CO₂",
    "🏗️ Proyectos ERNC",
    "🗺️ Zonas ZNI",
    "🔬 Análisis Comparativo",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CAPACIDAD RENOVABLE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown(title_html("⚡", f"Capacidad Instalada de Energías Renovables — {g_anio}",
                "Ranking departamental · Mix por fuente · Inversión"), unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.2, 1, 0.8])
    with c1:
        top_n = st.slider("Top departamentos", 3, 17, 10, key="cap_top")
    with c2:
        cap_fuentes = st.multiselect("Fuentes a incluir", FUENTES, default=FUENTES, key="cap_fuentes")
    with c3:
        cap_orden = st.radio("Ordenar por", ["Capacidad MW", "Inversión", "Proyectos"], horizontal=True, key="cap_ord")

    df_c = cap_f[cap_f["fuente"].isin(cap_fuentes)] if cap_fuentes else cap_f

    orden_col = {"Capacidad MW": "cap_mw", "Inversión": "inversion", "Proyectos": "proyectos"}[cap_orden]
    rank = (df_c.groupby(["departamento", "region"])
            .agg(cap_mw=("capacidad_mw", "sum"),
                 proyectos=("proyectos_activos", "sum"),
                 en_constr=("proyectos_en_construccion", "sum"),
                 inversion=("inversion_bill_cop", "sum"))
            .reset_index()
            .sort_values(orden_col, ascending=False)
            .head(top_n))
    rank["pct"] = (rank["cap_mw"] / rank["cap_mw"].sum() * 100).round(1)
    por_fuente = df_c.groupby("fuente")["capacidad_mw"].sum().reset_index().sort_values("capacidad_mw", ascending=False)

    fig1 = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4],
                         subplot_titles=["Ranking Departamental (MW)", "Mix por Fuente"])
    fig1.add_trace(go.Bar(
        x=rank["cap_mw"], y=rank["departamento"], orientation="h",
        marker_color=[REGION_COLORES.get(r, C["neutral"]) for r in rank["region"]],
        text=[f"{v:,.0f} MW" for v in rank["cap_mw"]],
        textposition="outside", textfont=dict(size=10, color=C["subtext"]),
        customdata=rank[["region", "proyectos", "en_constr", "inversion"]].values,
        hovertemplate="<b>%{y}</b><br>Región: %{customdata[0]}<br>"
                      "Capacidad: %{x:,.0f} MW<br>Activos: %{customdata[1]}<br>"
                      "En construcción: %{customdata[2]}<br>"
                      "Inversión: %{customdata[3]:.2f} B.COP<extra></extra>",
        showlegend=False,
    ), row=1, col=1)

    # Leyenda regiones
    for reg, col in REGION_COLORES.items():
        fig1.add_trace(go.Bar(x=[None], y=[None], name=reg, marker_color=col, showlegend=True), row=1, col=1)

    fig1.add_trace(go.Pie(
        labels=por_fuente["fuente"], values=por_fuente["capacidad_mw"], hole=0.55,
        marker=dict(colors=[FUENTE_COLORES.get(f, C["neutral"]) for f in por_fuente["fuente"]],
                    line=dict(color=C["bg"], width=2)),
        textinfo="label+percent", textfont=dict(size=10),
        hovertemplate="<b>%{label}</b><br>%{value:,.1f} MW · %{percent}<extra></extra>",
    ), row=1, col=2)

    fig1.update_layout(**base_layout(height=460, title_text=f"⚡ Energías Renovables — Colombia {g_anio}",
                       legend=dict(x=0.01, y=0.01)))
    fig1.update_yaxes(categoryorder="total ascending", row=1, col=1)
    fig1.update_xaxes(gridcolor=C["grid"])
    fig1.update_yaxes(gridcolor=C["grid"])
    st.plotly_chart(fig1, use_container_width=True)

    # Tabla de datos filtrados
    with st.expander("📋 Ver tabla de datos"):
        st.dataframe(rank.rename(columns={"cap_mw": "Capacidad MW", "proyectos": "Proyectos Activos",
                                          "en_constr": "En Construcción", "inversion": "Inversión B.COP"}),
                     use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EVOLUCIÓN TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown(title_html("📈", "Evolución Histórica por Fuente Energética 2019–2023",
                "Selecciona fuentes, métrica y tipo de visualización"), unsafe_allow_html=True)

    e1, e2, e3, e4 = st.columns([1.4, 1.4, 1, 1])
    with e1:
        ev_fuentes = st.multiselect("Fuentes a graficar",
            FUENTES, default=["Solar Fotovoltaica", "Eólica", "Hidroeléctrica"], key="ev_f")
    with e2:
        ev_deptos = st.multiselect("Filtrar por departamento",
            ["Todos"] + DEPTOS, default=["Todos"], key="ev_d")
    with e3:
        ev_metrica = st.selectbox("Métrica", [
            ("Capacidad (MW)", "capacidad_mw"),
            ("Proyectos activos", "proyectos_activos"),
            ("En construcción", "proyectos_en_construccion"),
            ("Inversión (B.COP)", "inversion_bill_cop"),
        ], format_func=lambda x: x[0], key="ev_m")
    with e4:
        ev_chart = st.radio("Tipo de gráfico", ["Área", "Líneas", "Barras"], horizontal=True, key="ev_c")

    df_ev = df_cap.copy()
    if "Todos" not in ev_deptos and ev_deptos:
        df_ev = df_ev[df_ev["departamento"].isin(ev_deptos)]
    if ev_fuentes:
        df_ev = df_ev[df_ev["fuente"].isin(ev_fuentes)]
    col_m, label_m = ev_metrica

    agg_ev = df_ev.groupby(["anio", "fuente"])[col_m].sum().reset_index()
    fig2 = go.Figure()

    for fuente in (ev_fuentes or FUENTES):
        sub = agg_ev[agg_ev["fuente"] == fuente].sort_values("anio")
        if sub.empty: continue
        color = FUENTE_COLORES.get(fuente, C["neutral"])
        base_kw = dict(
            x=sub["anio"], y=sub[col_m], name=fuente,
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=C["bg"], line=dict(color=color, width=2.5)),
            hovertemplate=f"<b>{fuente}</b><br>Año: %{{x}}<br>{label_m}: %{{y:,.2f}}<extra></extra>",
        )
        if ev_chart == "Área":
            fig2.add_trace(go.Scatter(mode="lines+markers", fill="tozeroy",
                fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
                **base_kw))
        elif ev_chart == "Líneas":
            fig2.add_trace(go.Scatter(mode="lines+markers+text",
                text=[f"{v:,.0f}" for v in sub[col_m]],
                textposition="top center", textfont=dict(size=9, color=color),
                **base_kw))
        else:
            fig2.add_trace(go.Bar(x=sub["anio"], y=sub[col_m], name=fuente,
                marker_color=color,
                hovertemplate=f"<b>{fuente}</b><br>%{{x}}: %{{y:,.2f}}<extra></extra>"))

    if ev_chart == "Barras":
        fig2.update_layout(barmode="group")

    # Anotar CAGR de cada fuente
    for fuente in (ev_fuentes or []):
        c_val = cagr(df_ev, fuente)
        if c_val is not None:
            sub = agg_ev[agg_ev["fuente"] == fuente].sort_values("anio")
            if not sub.empty:
                color = FUENTE_COLORES.get(fuente, C["neutral"])
                fig2.add_annotation(
                    x=sub["anio"].iloc[-1], y=sub[col_m].iloc[-1],
                    text=f"CAGR {c_val:+.1f}%",
                    font=dict(size=10, color=color, family="Georgia"),
                    bgcolor=C["bg2"], bordercolor=color, borderwidth=1,
                    borderpad=4, showarrow=True, arrowhead=2, arrowcolor=color,
                    ax=30, ay=-30,
                )

    fig2.update_layout(**base_layout(height=460, hovermode="x unified",
        title_text=f"📈 Evolución Histórica — {label_m}",
        xaxis=dict(tickmode="array", tickvals=ANIOS, gridcolor=C["grid"]),
        yaxis=dict(title=label_m, gridcolor=C["grid"]),
        xaxis_title="Año"))
    st.plotly_chart(fig2, use_container_width=True)

    # CAGR tabla resumen
    if ev_fuentes:
        cagr_data = [(f, cagr(df_ev, f)) for f in ev_fuentes]
        cagr_df = pd.DataFrame([(f, f"{c:+.1f}%" if c else "N/D") for f, c in cagr_data],
                               columns=["Fuente", "CAGR 2019–2023"])
        st.dataframe(cagr_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CONSUMO & COSTOS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown(title_html("💡", "Consumo Energético y Costos por Sector",
                "Análisis regional · Sectorial · Tendencia anual"), unsafe_allow_html=True)

    cc1, cc2, cc3, cc4 = st.columns([1, 1.2, 1, 1])
    with cc1:
        cc_regiones = st.multiselect("Regiones", REGIONES, default=REGIONES, key="cc_r")
    with cc2:
        cc_sectores = st.multiselect("Sectores", SECTORES, default=SECTORES, key="cc_s")
    with cc3:
        cc_anio_r = st.slider("Rango de años", min(ANIOS), max(ANIOS),
                              (min(ANIOS), max(ANIOS)), key="cc_a")
    with cc4:
        cc_metrica = st.radio("Métrica", [
            ("Consumo (GWh)", "consumo_gwh"),
            ("Costo $/kWh", "costo_promedio_kwh"),
            ("Usuarios", "usuarios"),
        ], format_func=lambda x: x[0], key="cc_m")

    col_cc, label_cc = cc_metrica
    df_cc = df_consumo[
        (df_consumo["anio"] >= cc_anio_r[0]) &
        (df_consumo["anio"] <= cc_anio_r[1]) &
        (df_consumo["region"].isin(cc_regiones)) &
        (df_consumo["sector"].isin(cc_sectores))
    ]

    fig3 = make_subplots(rows=1, cols=2,
        subplot_titles=[f"{label_cc} por Región y Sector", f"Tendencia Anual — {label_cc}"])

    agg_rs = df_cc.groupby(["region", "sector"])[col_cc].sum().reset_index()
    for sector in df_cc["sector"].unique():
        sub = agg_rs[agg_rs["sector"] == sector]
        fig3.add_trace(go.Bar(
            x=sub["region"], y=sub[col_cc],
            name=sector.replace("_", " ").title(),
            marker_color=SECTOR_COLORES.get(sector, C["neutral"]),
            hovertemplate=f"<b>{sector}</b><br>%{{x}}: %{{y:,.1f}}<extra></extra>",
        ), row=1, col=1)

    agg_a = df_cc.groupby(["anio", "sector"])[col_cc].sum().reset_index()
    for sector in df_cc["sector"].unique():
        sub = agg_a[agg_a["sector"] == sector].sort_values("anio")
        fig3.add_trace(go.Scatter(
            x=sub["anio"], y=sub[col_cc],
            name=sector.replace("_", " ").title(),
            mode="lines+markers",
            line=dict(color=SECTOR_COLORES.get(sector, C["neutral"]), width=2),
            showlegend=False,
            hovertemplate=f"<b>{sector}</b><br>%{{x}}: %{{y:,.1f}}<extra></extra>",
        ), row=1, col=2)

    fig3.update_layout(**base_layout(barmode="stack", height=460, hovermode="x unified",
        title_text=f"💡 Consumo y Costos — {cc_anio_r[0]}–{cc_anio_r[1]}"))
    for i in [1, 2]:
        fig3.update_xaxes(gridcolor=C["grid"], row=1, col=i)
        fig3.update_yaxes(gridcolor=C["grid"], row=1, col=i)
    st.plotly_chart(fig3, use_container_width=True)

    # Heatmap costos
    st.subheader("🌡️ Heatmap — Costo promedio $/kWh por Región y Sector")
    pivot_h = df_cc.groupby(["region", "sector"])["costo_promedio_kwh"].mean().unstack().fillna(0)
    fig3b = go.Figure(go.Heatmap(
        z=pivot_h.values,
        x=[c.replace("_", " ").title() for c in pivot_h.columns],
        y=pivot_h.index,
        colorscale=[[0, C["bg2"]], [0.3, C["hidro"]], [0.7, C["solar"]], [1, C["red"]]],
        text=[[f"${v:,.0f}" for v in row] for row in pivot_h.values],
        texttemplate="%{text}", textfont=dict(size=12, color="white"),
        hovertemplate="Región: %{y}<br>Sector: %{x}<br>Costo: $%{z:,.0f} COP/kWh<extra></extra>",
        colorbar=dict(title="$/kWh", tickfont=dict(color=C["text"])),
    ))
    fig3b.update_layout(**base_layout(height=320, title_text="Costos por Región y Sector ($/kWh COP)"))
    st.plotly_chart(fig3b, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — EMISIONES CO2
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown(title_html("🌿", "Emisiones de CO₂ por Sector — Colombia",
                "Evolución histórica · Comparación · Meta NDC 2030 (–51%)"), unsafe_allow_html=True)

    em1, em2, em3 = st.columns([1, 1.2, 1])
    with em1:
        em_sectores = st.multiselect("Sectores", sorted(df_emis["sector"].unique()),
            default=sorted(df_emis["sector"].unique()), key="em_s")
    with em2:
        em_deptos = st.multiselect("Departamentos", ["Todos"] + sorted(df_emis["departamento"].unique()),
            default=["Todos"], key="em_d")
    with em3:
        em_vista = st.radio("Visualización", ["Tendencia", "Apilado", "vs Meta NDC", "Por depto"],
            key="em_v")

    df_em = df_emis.copy()
    if "Todos" not in em_deptos and em_deptos:
        df_em = df_em[df_em["departamento"].isin(em_deptos)]
    if em_sectores:
        df_em = df_em[df_em["sector"].isin(em_sectores)]

    if em_vista == "Tendencia":
        agg = df_em.groupby(["anio", "sector"])["mt_co2"].sum().reset_index()
        fig4 = go.Figure()
        for s in agg["sector"].unique():
            sub = agg[agg["sector"] == s].sort_values("anio")
            fig4.add_trace(go.Scatter(
                x=sub["anio"], y=sub["mt_co2"],
                name=s.replace("_", " ").title(),
                mode="lines+markers",
                line=dict(color=SECTOR_COLORES.get(s, C["neutral"]), width=2.5),
                marker=dict(size=8),
                hovertemplate=f"<b>{s}</b><br>%{{x}}: %{{y:.3f}} Mt CO₂<extra></extra>",
            ))
        fig4.update_layout(**base_layout(height=440, hovermode="x unified",
            title_text="📉 Tendencia de Emisiones por Sector",
            xaxis_title="Año", yaxis_title="Mt CO₂"))

    elif em_vista == "Apilado":
        agg = df_em.groupby(["anio", "sector"])["mt_co2"].sum().reset_index()
        fig4 = go.Figure()
        for s in agg["sector"].unique():
            sub = agg[agg["sector"] == s].sort_values("anio")
            fig4.add_trace(go.Bar(x=sub["anio"], y=sub["mt_co2"],
                name=s.replace("_", " ").title(),
                marker_color=SECTOR_COLORES.get(s, C["neutral"])))
        fig4.update_layout(**base_layout(barmode="stack", height=440,
            title_text="📊 Emisiones Apiladas por Sector",
            xaxis_title="Año", yaxis_title="Mt CO₂"))

    elif em_vista == "vs Meta NDC":
        agg = df_emis[df_emis["sector"] == "energia_electrica"].groupby("anio")["mt_co2"].sum().reset_index()
        base_val = float(agg[agg["anio"] == agg["anio"].min()]["mt_co2"].values[0]) if len(agg) else 1
        meta = base_val * 0.49
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=agg["anio"], y=agg["mt_co2"], name="Emisiones reales",
            mode="lines+markers",
            line=dict(color=C["solar"], width=3),
            marker=dict(size=10, color=C["bg"], line=dict(color=C["solar"], width=2.5)),
            fill="tozeroy", fillcolor="rgba(255,183,0,0.08)",
        ))
        fig4.add_hline(y=meta, line_dash="dash", line_color=C["green"], line_width=2,
            annotation_text=f"🎯 Meta NDC 2030: {meta:.3f} Mt",
            annotation_font=dict(color=C["green"], size=12))
        fig4.add_annotation(x=agg["anio"].max(), y=agg["mt_co2"].iloc[-1],
            text=f"Actual: {agg['mt_co2'].iloc[-1]:.3f} Mt",
            font=dict(color=C["solar"], size=11), bgcolor=C["bg2"],
            bordercolor=C["solar"], borderwidth=1, borderpad=4, showarrow=True)
        fig4.update_layout(**base_layout(height=440,
            title_text="🎯 Sector Eléctrico vs Meta NDC Colombia (–51%)",
            xaxis_title="Año", yaxis_title="Mt CO₂"))

    else:  # Por depto
        agg = df_em.groupby("departamento")["mt_co2"].sum().reset_index().sort_values("mt_co2", ascending=False)
        fig4 = go.Figure(go.Bar(
            x=agg["departamento"], y=agg["mt_co2"],
            marker=dict(color=agg["mt_co2"],
                        colorscale=[[0, C["bg2"]], [0.5, C["gas"]], [1, C["red"]]],
                        showscale=True, colorbar=dict(title="Mt CO₂", tickfont=dict(color=C["text"]))),
            hovertemplate="<b>%{x}</b><br>%{y:.3f} Mt CO₂<extra></extra>",
        ))
        fig4.update_layout(**base_layout(height=440,
            title_text="🗺️ Emisiones Totales por Departamento",
            xaxis_tickangle=-35, xaxis_title="Departamento", yaxis_title="Mt CO₂"))

    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PROYECTOS ERNC
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(title_html("🏗️", "Pipeline de Proyectos ERNC",
                "Inversión · Empleos · Estado · Dispersión capacidad vs USD"), unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    with p1:
        p_estados = st.multiselect("Estado del proyecto",
            sorted(df_proy["estado"].unique()), default=sorted(df_proy["estado"].unique()), key="p_e")
    with p2:
        p_tipos = st.multiselect("Tipo de energía",
            sorted(df_proy["tipo_energia"].unique()), default=sorted(df_proy["tipo_energia"].unique()), key="p_t")
    with p3:
        p_deptos_f = st.multiselect("Departamento",
            ["Todos"] + sorted(df_proy["departamento"].unique()), default=["Todos"], key="p_d")

    df_p = df_proy.copy()
    if p_estados: df_p = df_p[df_p["estado"].isin(p_estados)]
    if p_tipos:   df_p = df_p[df_p["tipo_energia"].isin(p_tipos)]
    if "Todos" not in p_deptos_f and p_deptos_f:
        df_p = df_p[df_p["departamento"].isin(p_deptos_f)]

    # KPIs proyectos
    pk1, pk2, pk3, pk4 = st.columns(4)
    pk1.metric("Proyectos", len(df_p))
    pk2.metric("Capacidad Total", f"{df_p['capacidad_mw'].sum():,.0f} MW")
    pk3.metric("Inversión Total", f"USD {df_p['inversion_musd'].sum():,.0f}M")
    pk4.metric("Empleos", f"{int(df_p['empleos_generados'].sum()):,}")

    pv1, pv2 = st.columns(2)
    with pv1:
        # Inversión por tipo y estado
        agg_inv = df_p.groupby(["tipo_energia", "estado"]).agg(
            inv=("inversion_musd", "sum"), n=("nombre_proyecto", "count")).reset_index()
        fig5a = go.Figure()
        for est in agg_inv["estado"].unique():
            sub = agg_inv[agg_inv["estado"] == est]
            fig5a.add_trace(go.Bar(
                x=sub["tipo_energia"], y=sub["inv"],
                name=est.replace("_", " ").title(),
                marker_color=ESTADO_COLORES.get(est, C["neutral"]),
                customdata=sub["n"],
                hovertemplate="<b>%{x}</b> · %{fullData.name}<br>USD %{y:,.1f}M<br>Proyectos: %{customdata}<extra></extra>",
            ))
        fig5a.update_layout(**base_layout(barmode="stack", height=380,
            title_text="💰 Inversión por Tipo y Estado",
            xaxis_tickangle=-20, yaxis_title="MUSD"))
        st.plotly_chart(fig5a, use_container_width=True)

    with pv2:
        # Scatter capacidad vs inversión
        fig5b = px.scatter(df_p, x="capacidad_mw", y="inversion_musd",
            color="tipo_energia", symbol="estado", size="empleos_generados",
            size_max=35, color_discrete_map=FUENTE_COLORES,
            hover_name="nombre_proyecto",
            hover_data={"empresa": True, "departamento": True,
                        "capacidad_mw": ":.1f", "inversion_musd": ":.1f"},
            labels={"capacidad_mw": "Capacidad (MW)", "inversion_musd": "Inversión (MUSD)",
                    "tipo_energia": "Tipo"}, template="plotly_dark")
        fig5b.update_layout(**base_layout(height=380,
            title_text="🔵 MW vs USD — Tamaño = Empleos"))
        st.plotly_chart(fig5b, use_container_width=True)

    # Tabla detallada
    with st.expander("📋 Tabla completa de proyectos"):
        cols_show = ["nombre_proyecto", "empresa", "departamento", "tipo_energia",
                     "estado", "capacidad_mw", "inversion_musd", "empleos_generados", "municipio"]
        st.dataframe(df_p[cols_show].sort_values("inversion_musd", ascending=False)
                     .rename(columns={c: c.replace("_", " ").title() for c in cols_show}),
                     use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — ZONAS ZNI
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown(title_html("🗺️", "Zonas No Interconectadas (ZNI)",
                "Cobertura · Horas de servicio · Población sin acceso"), unsafe_allow_html=True)

    z1, z2, z3 = st.columns(3)
    with z1:
        z_regiones = st.multiselect("Regiones", REGIONES, default=REGIONES, key="z_r")
    with z2:
        z_cobertura = st.radio("Cobertura", ["Todas", "Con servicio", "Sin servicio"], key="z_c")
    with z3:
        z_vista = st.radio("Vista", ["Horas de servicio", "Población", "Proyectos", "Tabla"], key="z_v")

    df_z = df_zni[df_zni["region"].isin(z_regiones)].copy()
    if z_cobertura == "Con servicio":  df_z = df_z[df_z["tiene_energia"] == True]
    elif z_cobertura == "Sin servicio": df_z = df_z[df_z["tiene_energia"] == False]

    # KPIs ZNI
    zk1, zk2, zk3, zk4 = st.columns(4)
    zk1.metric("Total ZNI", len(df_z))
    zk2.metric("Sin Servicio", int((df_z["tiene_energia"] == False).sum()))
    zk3.metric("Población Total", f"{int(df_z['poblacion'].sum()):,}")
    zk4.metric("Horas Prom/día", f"{df_z[df_z['tiene_energia']==True]['horas_servicio_dia'].mean():.1f}h")

    if z_vista == "Horas de servicio":
        df_zs = df_z.sort_values("horas_servicio_dia", ascending=False)
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=df_zs["nombre_zona"], y=df_zs["horas_servicio_dia"],
            marker_color=[C["green"] if t else C["red"] for t in df_zs["tiene_energia"]],
            customdata=df_zs[["departamento", "municipio", "fuente_principal", "poblacion"]].values,
            hovertemplate="<b>%{x}</b><br>Depto: %{customdata[0]}<br>Municipio: %{customdata[1]}<br>"
                          "Fuente: %{customdata[2]}<br>Población: %{customdata[3]:,}<br>"
                          "Horas/día: %{y}<extra></extra>",
        ))
        fig6.add_hline(y=24, line_dash="dot", line_color=C["subtext"],
                       annotation_text="24h ideal")
        fig6.add_hline(y=12, line_dash="dash", line_color=C["accent"],
                       annotation_text="12h mínimo recomendado",
                       annotation_font=dict(color=C["accent"]))
        fig6.update_layout(**base_layout(height=420,
            title_text="⚡ Horas de Servicio Eléctrico por Zona",
            xaxis_tickangle=-30, yaxis_title="Horas / día"))

    elif z_vista == "Población":
        agg_z = df_z.groupby(["departamento", "tiene_energia"])["poblacion"].sum().reset_index()
        fig6 = go.Figure()
        for tiene, nombre, color in [(True, "Con Servicio", C["green"]), (False, "Sin Servicio", C["red"])]:
            sub = agg_z[agg_z["tiene_energia"] == tiene]
            fig6.add_trace(go.Bar(x=sub["departamento"], y=sub["poblacion"], name=nombre,
                marker_color=color,
                hovertemplate=f"<b>%{{x}}</b> · {nombre}<br>Población: %{{y:,}}<extra></extra>"))
        fig6.update_layout(**base_layout(barmode="stack", height=420,
            title_text="👥 Población ZNI por Departamento y Cobertura",
            xaxis_tickangle=-25, yaxis_title="Personas"))

    elif z_vista == "Proyectos":
        df_z["tiene_proyecto"] = df_z["proyecto_asignado"].notna()
        cnt = df_z.groupby(["departamento", "tiene_proyecto"]).size().reset_index(name="zonas")
        fig6 = go.Figure()
        for tp, nombre, color in [(True, "Con Proyecto", C["green"]), (False, "Sin Proyecto", C["red"])]:
            sub = cnt[cnt["tiene_proyecto"] == tp]
            fig6.add_trace(go.Bar(x=sub["departamento"], y=sub["zonas"], name=nombre,
                marker_color=color))
        fig6.update_layout(**base_layout(barmode="group", height=420,
            title_text="🏗️ Asignación de Proyectos en ZNI",
            xaxis_tickangle=-25, yaxis_title="Número de Zonas"))

    else:  # Tabla
        cols_z = ["nombre_zona", "departamento", "municipio", "poblacion",
                  "tiene_energia", "horas_servicio_dia", "fuente_principal", "proyecto_asignado"]
        fig6 = go.Figure(data=[go.Table(
            header=dict(values=["Zona", "Depto", "Municipio", "Población", "Servicio",
                                "Horas/día", "Fuente", "Proyecto"],
                fill_color=C["bg2"], font=dict(color=C["accent"], size=11),
                align="center", height=30),
            cells=dict(
                values=[df_z[c] for c in cols_z],
                fill_color=[[C["bg3"] if i % 2 == 0 else C["bg"] for i in range(len(df_z))]]*8,
                font=dict(color=C["text"], size=10), align="left", height=26),
        )])
        fig6.update_layout(**base_layout(height=420, title_text="📋 Tabla ZNI"))

    st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — ANÁLISIS COMPARATIVO
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown(title_html("🔬", "Análisis Comparativo y Correlaciones",
                "Índice de transición · CAGR · Correlaciones · Heatmap"), unsafe_allow_html=True)

    an_vista = st.radio("Selecciona el análisis", [
        "Índice de Transición por Departamento",
        "CAGR por Fuente Energética",
        "Inversión ERNC vs Emisiones CO₂",
        "Heatmap Comparativo Regiones",
    ], horizontal=True, key="an_v")

    if an_vista == "Índice de Transición por Departamento":
        cap_23 = df_cap[df_cap["anio"] == g_anio]
        renov = cap_23[cap_23["tipo"].isin(["renovable", "alternativa"])].groupby("departamento")["capacidad_mw"].sum()
        total = cap_23.groupby("departamento")["capacidad_mw"].sum()
        pct   = (renov / total * 100).fillna(0).reset_index(name="pct_renovable")
        emp   = df_proy.groupby("departamento")["empleos_generados"].sum().reset_index()
        inv_d = df_proy.groupby("departamento")["inversion_musd"].sum().reset_index()
        idx   = pct.merge(emp, on="departamento", how="left").merge(inv_d, on="departamento", how="left").fillna(0)
        idx   = idx.sort_values("pct_renovable", ascending=False)

        fan1, fan2 = st.columns(2)
        with fan1:
            fig7a = go.Figure(go.Bar(
                x=idx["departamento"], y=idx["pct_renovable"],
                marker=dict(color=idx["pct_renovable"],
                    colorscale=[[0, C["red"]], [0.5, C["solar"]], [1, C["green"]]],
                    showscale=True, colorbar=dict(title="%", tickfont=dict(color=C["text"]))),
                hovertemplate="<b>%{x}</b><br>%{y:.1f}% renovable<extra></extra>",
            ))
            fig7a.update_layout(**base_layout(height=400,
                title_text=f"% Cap. Renovable por Dpto ({g_anio})",
                xaxis_tickangle=-40, yaxis_title="% Renovable"))
            st.plotly_chart(fig7a, use_container_width=True)

        with fan2:
            fig7b = go.Figure(go.Scatter(
                x=idx["inversion_musd"], y=idx["empleos_generados"],
                mode="markers+text", text=idx["departamento"],
                textposition="top center", textfont=dict(size=8, color=C["subtext"]),
                marker=dict(size=10, color=C["solar"],
                            line=dict(color=C["bg"], width=1.5)),
                hovertemplate="<b>%{text}</b><br>USD %{x:,.0f}M<br>%{y:,} empleos<extra></extra>",
            ))
            fig7b.update_layout(**base_layout(height=400,
                title_text="Inversión ERNC vs Empleos",
                xaxis_title="Inversión (MUSD)", yaxis_title="Empleos Directos"))
            st.plotly_chart(fig7b, use_container_width=True)

    elif an_vista == "CAGR por Fuente Energética":
        cagrs = [(f, cagr(df_cap, f)) for f in FUENTES]
        cagrs = sorted([(f, c) for f, c in cagrs if c is not None], key=lambda x: x[1], reverse=True)
        fig7c = go.Figure(go.Bar(
            x=[x[0] for x in cagrs], y=[x[1] for x in cagrs],
            marker=dict(color=[C["green"] if x[1] >= 0 else C["red"] for x in cagrs]),
            text=[f"{x[1]:+.1f}%" for x in cagrs],
            textposition="outside", textfont=dict(size=11, color=C["text"]),
            hovertemplate="<b>%{x}</b><br>CAGR: %{y:+.1f}%<extra></extra>",
        ))
        fig7c.add_hline(y=0, line_color=C["subtext"], line_width=1)
        fig7c.update_layout(**base_layout(height=440,
            title_text="📈 CAGR por Fuente Energética (2019–2023)",
            xaxis_tickangle=-25, yaxis_title="CAGR (%)"))
        st.plotly_chart(fig7c, use_container_width=True)

    elif an_vista == "Inversión ERNC vs Emisiones CO₂":
        inv_e = df_proy.groupby("departamento")["inversion_musd"].sum().reset_index()
        emi_e = df_emis[df_emis["anio"] == g_anio].groupby("departamento")["mt_co2"].sum().reset_index()
        merged = inv_e.merge(emi_e, on="departamento", how="inner")
        corr_val = merged["inversion_musd"].corr(merged["mt_co2"])
        fig7d = px.scatter(merged, x="inversion_musd", y="mt_co2",
            text="departamento", size="inversion_musd", size_max=40,
            color="mt_co2", color_continuous_scale="RdYlGn_r",
            labels={"inversion_musd": "Inversión ERNC (MUSD)", "mt_co2": "Emisiones CO₂ (Mt)"},
            template="plotly_dark")
        fig7d.update_traces(textposition="top center", textfont=dict(size=9, color=C["subtext"]))
        fig7d.update_layout(**base_layout(height=460,
            title_text=f"🔵 Inversión vs Emisiones — r = {corr_val:.2f}"))
        st.plotly_chart(fig7d, use_container_width=True)

    else:  # Heatmap comparativo
        pivot_r = df_cap[df_cap["anio"] == g_anio].groupby(["region", "fuente"])["capacidad_mw"].sum().unstack().fillna(0)
        fig7e = go.Figure(go.Heatmap(
            z=pivot_r.values,
            x=pivot_r.columns.tolist(),
            y=pivot_r.index.tolist(),
            colorscale=[[0, C["bg3"]], [0.4, C["accent2"]], [0.8, C["solar"]], [1, C["green"]]],
            text=[[f"{v:,.0f}" for v in row] for row in pivot_r.values],
            texttemplate="%{text}", textfont=dict(size=10, color="white"),
            hovertemplate="Región: %{y}<br>Fuente: %{x}<br>%{z:,.1f} MW<extra></extra>",
            colorbar=dict(title="MW", tickfont=dict(color=C["text"])),
        ))
        fig7e.update_layout(**base_layout(height=380, xaxis_tickangle=-30,
            title_text=f"🌡️ Capacidad (MW) por Región y Fuente — {g_anio}"))
        st.plotly_chart(fig7e, use_container_width=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:32px; padding:18px 24px;
            background:linear-gradient(135deg,{C['bg3']},{C['bg2']});
            border-radius:10px; border-top:2px solid {C['border']};
            display:flex; justify-content:space-between; align-items:center;
            flex-wrap:wrap; gap:10px;">
  <div style="color:{C['subtext']};font-size:11px;">
    📡 Fuente: <b style='color:{C['accent']}'>datos.gov.co</b> — IPSE · UPME · IDEAM · DANE
    &nbsp;|&nbsp; 🛠️ Python · MySQL · Streamlit · Plotly
  </div>
  <div style="color:{C['subtext']};font-size:11px;">
    🎓 <b style='color:{C['accent']}'>Bootcamp Talento Tech</b> — Análisis de Datos · Nivel Integrador · 2025
  </div>
</div>
""", unsafe_allow_html=True)
