# theme.py — Paleta, layouts y utilidades de visualización
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paleta principal ───────────────────────────────────────────────────────────
C = dict(
    bg       = "#0D1B2A",
    bg2      = "#112233",
    bg3      = "#0A1628",
    grid     = "#1E3A5C",
    border   = "#1E3A5C",
    text     = "#E8EDF2",
    subtext  = "#7A9BB5",
    accent   = "#FFB700",
    accent2  = "#00D4FF",
    green    = "#00C896",
    red      = "#FF4D6D",
    solar    = "#FFB700",
    eolica   = "#00D4FF",
    hidro    = "#4FC3F7",
    biomasa  = "#56C784",
    gas      = "#FF7043",
    geot     = "#CE93D8",
    neutral  = "#7986CB",
    purple   = "#9C6FDE",
)

FUENTE_COLORES = {
    "Solar Fotovoltaica":            C["solar"],
    "Eólica":                        C["eolica"],
    "Hidroeléctrica":                C["hidro"],
    "Biomasa":                       C["biomasa"],
    "Gas Natural":                   C["gas"],
    "Geotérmica":                    C["geot"],
    "Pequeña Central Hidroeléctrica":"#81D4FA",
    "Combustóleo/ACPM":              "#FF5252",
    "Carbón":                        "#78909C",
    "Hidrógeno Verde":               C["green"],
}

REGION_COLORES = {
    "Andina":    C["neutral"],
    "Caribe":    C["solar"],
    "Pacífica":  C["biomasa"],
    "Orinoquía": C["gas"],
    "Amazónica": C["geot"],
}

SECTOR_COLORES = {
    "residencial":     C["hidro"],
    "industrial":      C["gas"],
    "comercial":       C["solar"],
    "transporte":      C["red"],
    "agropecuario":    C["biomasa"],
    "publico":         C["neutral"],
    "energia_electrica": C["solar"],
}

ESTADO_COLORES = {
    "operativo":       C["green"],
    "en_construccion": C["solar"],
    "radicado":        C["eolica"],
    "suspendido":      C["red"],
    "cancelado":       "#78909C",
}

# ── Layout base para todos los gráficos ───────────────────────────────────────
def base_layout(**kwargs):
    layout = dict(
        paper_bgcolor = C["bg"],
        plot_bgcolor  = C["bg2"],
        font          = dict(family="Georgia, 'Times New Roman', serif",
                             color=C["text"], size=12),
        margin        = dict(l=50, r=30, t=55, b=45),
        xaxis         = dict(gridcolor=C["grid"], zerolinecolor=C["grid"],
                             linecolor=C["border"]),
        yaxis         = dict(gridcolor=C["grid"], zerolinecolor=C["grid"],
                             linecolor=C["border"]),
        legend        = dict(bgcolor="rgba(13,27,42,0.85)",
                             bordercolor=C["border"], borderwidth=1,
                             font=dict(size=11)),
        hoverlabel    = dict(bgcolor=C["bg3"], bordercolor=C["accent"],
                             font=dict(color=C["text"], size=12)),
        title         = dict(font=dict(size=15, color=C["accent"],
                                       family="Georgia, serif"),
                             x=0.01),
    )
    layout.update(kwargs)
    return layout


def title_html(icon, title, subtitle=""):
    sub = f'<p style="color:{C["subtext"]};font-size:13px;margin:2px 0 0 0;letter-spacing:1px;">{subtitle}</p>' if subtitle else ""
    return f"""
    <div style="background:linear-gradient(135deg,{C['bg']},{C['bg2']});
                padding:22px 28px; border-radius:12px;
                border-left:4px solid {C['accent']}; margin-bottom:20px;">
      <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-size:36px;">{icon}</span>
        <div>
          <h2 style="color:{C['accent']};font-family:Georgia,serif;
                     margin:0;font-size:22px;letter-spacing:.5px;">{title}</h2>
          {sub}
        </div>
      </div>
    </div>"""


def kpi_card(label, value, unit, icon, color=None):
    color = color or C["accent"]
    return f"""
    <div style="background:linear-gradient(135deg,{C['bg2']},{C['bg3']});
                border:1px solid {C['border']}; border-top:3px solid {color};
                border-radius:10px; padding:18px 14px; text-align:center;">
      <div style="font-size:28px;margin-bottom:6px;">{icon}</div>
      <div style="color:{color};font-size:20px;font-weight:bold;
                  font-family:Georgia,serif;">{value}</div>
      <div style="color:{C['subtext']};font-size:10px;letter-spacing:1px;
                  text-transform:uppercase;margin-top:3px;">{unit}</div>
      <div style="color:{C['text']};font-size:11px;margin-top:6px;">{label}</div>
    </div>"""


def divider():
    return f'<hr style="border:none;border-top:1px solid {C["border"]};margin:24px 0;">'
