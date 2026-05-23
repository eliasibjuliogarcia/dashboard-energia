# theme.py — Sistema de Diseño · Dashboard Transición Energética Colombia
# Paleta, tipografía, componentes y utilidades de visualización
# Versión 2.0 — Eliasib García · Bootcamp Talento Tech 2025

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════════════════════
# PALETA DE COLOR  — "Obsidian & Ember"
# Base: azul noche profundo · Acento: ámbar eléctrico · Energía: verde esmeralda
# ══════════════════════════════════════════════════════════════════════════════
C = dict(
    # Fondos
    bg        = "#08111E",   # negro marino
    bg2       = "#0E1F30",   # azul noche
    bg3       = "#071019",   # negro abismo
    bg4       = "#111D2B",   # panel elevado
    bg_glass  = "rgba(14,31,48,0.82)",

    # Estructura
    grid      = "#132233",
    border    = "#1A3550",
    border2   = "#0F2438",
    divider   = "#162B40",

    # Tipografía
    text      = "#DCE8F0",
    subtext   = "#607D8B",
    muted     = "#3D5A6E",
    caption   = "#4A6478",

    # Acento principal — ámbar eléctrico
    accent    = "#F0A500",
    accent_lo = "rgba(240,165,0,0.12)",
    accent_hi = "#FFD060",

    # Acento secundario — cian energético
    accent2   = "#00C8E8",
    accent2_lo = "rgba(0,200,232,0.10)",

    # Semáforo
    green     = "#00D49A",
    green_lo  = "rgba(0,212,154,0.12)",
    yellow    = "#F5C518",
    red       = "#FF3D5A",
    red_lo    = "rgba(255,61,90,0.10)",
    orange    = "#FF7A3D",

    # Fuentes energéticas
    solar     = "#F0A500",
    eolica    = "#00C8E8",
    hidro     = "#4BBAF5",
    biomasa   = "#3EC87A",
    gas       = "#FF7A3D",
    geot      = "#C678DD",
    purple    = "#9B72CF",
    neutral   = "#607D8B",
    coal      = "#78909C",
)

# ── Colores por fuente energética ──────────────────────────────────────────────
FUENTE_COLORES = {
    "Solar Fotovoltaica":              C["solar"],
    "Eólica":                          C["eolica"],
    "Hidroeléctrica":                  C["hidro"],
    "Biomasa":                         C["biomasa"],
    "Gas Natural":                     C["gas"],
    "Geotérmica":                      C["geot"],
    "Pequeña Central Hidroeléctrica":  "#70C8F8",
    "Combustóleo/ACPM":                "#FF5252",
    "Carbón":                          C["coal"],
    "Hidrógeno Verde":                 C["green"],
}

REGION_COLORES = {
    "Andina":    "#7986CB",
    "Caribe":    C["solar"],
    "Pacífica":  C["biomasa"],
    "Orinoquía": C["gas"],
    "Amazónica": C["geot"],
}

SECTOR_COLORES = {
    "residencial":       C["hidro"],
    "industrial":        C["gas"],
    "comercial":         C["solar"],
    "transporte":        C["red"],
    "agropecuario":      C["biomasa"],
    "publico":           C["neutral"],
    "energia_electrica": C["accent2"],
}

ESTADO_COLORES = {
    "operativo":         C["green"],
    "en_construccion":   C["solar"],
    "radicado":          C["eolica"],
    "suspendido":        C["red"],
    "cancelado":         C["coal"],
    "proyectado":        C["accent2"],
}

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT BASE PLOTLY
# ══════════════════════════════════════════════════════════════════════════════
def base_layout(**kwargs):
    layout = dict(
        paper_bgcolor = C["bg"],
        plot_bgcolor  = C["bg2"],
        font          = dict(
            family = "IBM Plex Sans, 'Source Sans 3', sans-serif",
            color  = C["text"],
            size   = 12,
        ),
        margin        = dict(l=52, r=24, t=52, b=44),
        xaxis         = dict(
            gridcolor     = C["grid"],
            zerolinecolor = C["border"],
            linecolor     = C["border"],
            tickfont      = dict(color=C["subtext"], size=10),
        ),
        yaxis         = dict(
            gridcolor     = C["grid"],
            zerolinecolor = C["border"],
            linecolor     = C["border"],
            tickfont      = dict(color=C["subtext"], size=10),
        ),
        legend        = dict(
            bgcolor      = "rgba(8,17,30,0.88)",
            bordercolor  = C["border"],
            borderwidth  = 1,
            font         = dict(size=11, color=C["text"]),
            itemsizing   = "constant",
        ),
        hoverlabel    = dict(
            bgcolor    = "#07101B",
            bordercolor= C["accent"],
            font       = dict(color=C["text"], size=12,
                              family="IBM Plex Sans, sans-serif"),
        ),
        title         = dict(
            font = dict(size=14, color=C["accent"],
                        family="Fraunces, Georgia, serif"),
            x    = 0.01,
            y    = 0.97,
        ),
        modebar       = dict(
            bgcolor     = C["bg"],
            color       = C["muted"],
            activecolor = C["accent"],
        ),
    )
    layout.update(kwargs)
    return layout


# ══════════════════════════════════════════════════════════════════════════════
# COMPONENTES HTML — Sistema coherente de UI
# ══════════════════════════════════════════════════════════════════════════════

def page_header(icon: str, title: str, subtitle: str = "",
                badge: str = "", badge_color: str = "") -> str:
    """Encabezado de sección con badge opcional."""
    badge_color = badge_color or C["accent"]
    badge_html  = (
        f'<span style="background:{badge_color}22;color:{badge_color};'
        f'border:1px solid {badge_color}44;border-radius:20px;'
        f'padding:2px 10px;font-size:10px;letter-spacing:1.5px;'
        f'font-weight:600;vertical-align:middle;margin-left:10px;">'
        f'{badge}</span>'
    ) if badge else ""

    sub_html = (
        f'<p style="color:{C["subtext"]};font-size:12px;margin:4px 0 0 0;'
        f'letter-spacing:.8px;font-family:\'IBM Plex Sans\',sans-serif;">'
        f'{subtitle}</p>'
    ) if subtitle else ""

    return f"""
<div style="
    background: linear-gradient(135deg, {C['bg3']} 0%, {C['bg4']} 100%);
    padding: 20px 26px;
    border-radius: 12px;
    border: 1px solid {C['border2']};
    border-left: 4px solid {C['accent']};
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;">
  <div style="
      position:absolute;right:-20px;top:-20px;
      width:120px;height:120px;border-radius:50%;
      background:radial-gradient({C['accent']}18,transparent 70%);
      pointer-events:none;">
  </div>
  <div style="display:flex;align-items:center;gap:14px;position:relative;">
    <div style="
        font-size:32px;line-height:1;
        filter:drop-shadow(0 0 12px {C['accent']}66);">{icon}</div>
    <div>
      <h2 style="
          color:{C['accent']};
          font-family:'Fraunces','Playfair Display',Georgia,serif;
          margin:0;font-size:20px;letter-spacing:.3px;font-weight:700;
          line-height:1.2;">{title}{badge_html}</h2>
      {sub_html}
    </div>
  </div>
</div>"""


def kpi_card(label: str, value: str, unit: str,
             icon: str, color: str = "", delta: str = "") -> str:
    """Tarjeta KPI con delta opcional."""
    color = color or C["accent"]
    delta_html = ""
    if delta:
        d_color = C["green"] if delta.startswith("+") else C["red"]
        arrow   = "▲" if delta.startswith("+") else "▼"
        delta_html = (
            f'<div style="color:{d_color};font-size:10px;margin-top:5px;'
            f'font-weight:600;">{arrow} {delta}</div>'
        )
    return f"""
<div style="
    background: linear-gradient(145deg, {C['bg4']}, {C['bg3']});
    border: 1px solid {C['border2']};
    border-top: 2px solid {color};
    border-radius: 10px;
    padding: 18px 14px;
    text-align: center;
    transition: all .2s;
    position: relative;
    overflow: hidden;">
  <div style="
      position:absolute;bottom:-12px;right:-12px;
      font-size:52px;opacity:.06;line-height:1;">{icon}</div>
  <div style="font-size:24px;margin-bottom:6px;
              filter:drop-shadow(0 0 8px {color}66);">{icon}</div>
  <div style="color:{color};font-size:21px;font-weight:700;
              font-family:'Fraunces',Georgia,serif;line-height:1.1;">{value}</div>
  <div style="color:{C['subtext']};font-size:9px;letter-spacing:1.5px;
              text-transform:uppercase;margin-top:3px;">{unit}</div>
  <div style="color:{C['text']};font-size:11px;margin-top:7px;
              border-top:1px solid {C['border']};padding-top:7px;">{label}</div>
  {delta_html}
</div>"""


def stat_row(items: list) -> str:
    """Fila de estadísticas inline: lista de (valor, label, color)."""
    parts = []
    for val, lbl, col in items:
        col = col or C["accent"]
        parts.append(f"""
        <div style="text-align:center;padding:0 18px;
                    border-right:1px solid {C['border']};">
          <div style="color:{col};font-size:17px;font-weight:700;
                      font-family:'Fraunces',serif;">{val}</div>
          <div style="color:{C['subtext']};font-size:10px;
                      letter-spacing:1px;text-transform:uppercase;">{lbl}</div>
        </div>""")
    # Quitar el borde del último
    if parts:
        parts[-1] = parts[-1].replace(
            f"border-right:1px solid {C['border']};", "")
    return f"""
<div style="
    background:{C['bg4']};border:1px solid {C['border2']};
    border-radius:8px;padding:14px 4px;
    display:flex;justify-content:center;align-items:center;
    flex-wrap:wrap;gap:4px;margin:8px 0;">
  {''.join(parts)}
</div>"""


def alert_card(title: str, body: str, color: str = "",
               icon: str = "⚠") -> str:
    color = color or C["red"]
    return f"""
<div style="
    background: linear-gradient(135deg,
        {color}0A 0%, {C['bg3']} 100%);
    border: 1px solid {color}30;
    border-left: 3px solid {color};
    border-radius: 8px;
    padding: 13px 16px;
    margin: 6px 0;">
  <div style="display:flex;align-items:flex-start;gap:10px;">
    <span style="font-size:16px;margin-top:1px;
                 filter:drop-shadow(0 0 6px {color}88);">{icon}</span>
    <div>
      <b style="color:{color};font-size:12px;">{title}</b>
      <p style="color:{C['subtext']};font-size:11px;
                margin:3px 0 0;line-height:1.6;">{body}</p>
    </div>
  </div>
</div>"""


def solution_card(title: str, body: str, color: str = "",
                  icon: str = "✦") -> str:
    color = color or C["green"]
    return f"""
<div style="
    background: linear-gradient(135deg,
        {color}08 0%, {C['bg3']} 100%);
    border: 1px solid {color}28;
    border-left: 3px solid {color};
    border-radius: 8px;
    padding: 13px 16px;
    margin: 6px 0;">
  <div style="display:flex;align-items:flex-start;gap:10px;">
    <span style="font-size:14px;margin-top:2px;color:{color};">{icon}</span>
    <div>
      <b style="color:{color};font-size:12px;">{title}</b>
      <p style="color:{C['subtext']};font-size:11px;
                margin:3px 0 0;line-height:1.6;">{body}</p>
    </div>
  </div>
</div>"""


def impact_card(title: str, desc: str, result: str,
                color: str = "", icon: str = "◆") -> str:
    color = color or C["accent"]
    return f"""
<div style="
    background: linear-gradient(145deg, {C['bg4']}, {C['bg3']});
    border: 1px solid {color}30;
    border-top: 2px solid {color};
    border-radius: 10px;
    padding: 16px 14px;
    min-height: 148px;
    position: relative;
    overflow: hidden;">
  <div style="position:absolute;top:-8px;right:10px;font-size:40px;
              opacity:.07;color:{color};">{icon}</div>
  <div style="color:{color};font-size:12px;font-weight:700;
              margin-bottom:8px;letter-spacing:.3px;">{title}</div>
  <div style="color:{C['text']};font-size:11px;line-height:1.65;
              margin-bottom:10px;">{desc}</div>
  <div style="
      color:{color};font-size:10px;font-weight:700;
      border-top:1px solid {color}22;padding-top:8px;
      letter-spacing:.5px;">{result}</div>
</div>"""


def step_card(number: str, title: str, subtitle: str,
              color: str = "") -> str:
    color = color or C["accent"]
    return f"""
<div style="
    background: linear-gradient(145deg, {C['bg4']}, {C['bg3']});
    border: 1px solid {color}28;
    border-top: 2px solid {color};
    border-radius: 8px;
    padding: 12px 8px;
    text-align: center;">
  <div style="color:{color};font-size:18px;font-weight:800;
              font-family:'Fraunces',serif;opacity:.6;
              line-height:1;">{number}</div>
  <div style="color:{C['text']};font-size:10px;font-weight:700;
              margin-top:5px;letter-spacing:.3px;">{title}</div>
  <div style="color:{C['subtext']};font-size:9px;
              margin-top:2px;letter-spacing:.5px;">{subtitle}</div>
</div>"""


def section_divider(label: str = "") -> str:
    if label:
        return f"""
<div style="display:flex;align-items:center;gap:14px;margin:20px 0 14px;">
  <div style="flex:1;height:1px;background:{C['border']};"></div>
  <span style="color:{C['subtext']};font-size:10px;letter-spacing:2px;
               text-transform:uppercase;white-space:nowrap;">{label}</span>
  <div style="flex:1;height:1px;background:{C['border']};"></div>
</div>"""
    return f'<div style="height:1px;background:{C["border"]};margin:20px 0;"></div>'


def source_caption(text: str) -> str:
    return (f'<p style="color:{C["caption"]};font-size:10px;'
            f'margin-top:-6px;margin-bottom:4px;letter-spacing:.4px;">'
            f'ⓘ {text}</p>')


def badge(text: str, color: str = "") -> str:
    color = color or C["accent"]
    return (f'<span style="background:{color}18;color:{color};'
            f'border:1px solid {color}38;border-radius:4px;'
            f'padding:2px 8px;font-size:10px;font-weight:600;'
            f'letter-spacing:.8px;">{text}</span>')