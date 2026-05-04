# database.py — Conexión MySQL + datasets datos.gov.co integrados
# Bootcamp Talento Tech — Nivel Integrador 2025
#
# FUENTES DE DATOS OFICIALES (datos.gov.co):
#   1. IPSE  — Cobertura ZNI
#   2. UPME  — Proyectos FNCER (vy9n-w6hc) ← NUEVO, hasta 2025
#   3. UPME  — Balance Energético (consumo sectorial)
#   4. IDEAM — Inventario GEI / Emisiones CO2
#   5. DANE  — DIVIPOLA departamentos
#
# CONTEXTO ACTUALIZADO (UPME 2024-2025):
#   - Plan 6GW+: 82 proyectos solares/eólicos, 1.348 MW en operación
#   - Crecimiento solar 2024: +187,3% (el mayor año de la historia)
#   - FNCER representan 9% de capacidad total SIN a 2024
#   - Meta PND 2022-2026: 2.297 MW de FNCER en operación

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import streamlit as st

# ── Credenciales BD ───────────────────────────────────────────────────────────
DB = dict(
    user     = "u748235332_energetica",
    password = "P4ulin4.*",
    host     = "82.197.82.63",
    port     = 3306,
    database = "u748235332_energetica",
)

# ── URLs de datasets públicos datos.gov.co ────────────────────────────────────
URLS = {
    "fncer_upme":
        "https://www.datos.gov.co/api/views/vy9n-w6hc/rows.csv?accessType=DOWNLOAD",
}

# ── Engine MySQL ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_engine():
    url = (
        f"mysql+pymysql://{DB['user']}:{DB['password']}"
        f"@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8mb4"
    )
    return create_engine(url, pool_pre_ping=True)

def Q(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, get_engine())

# ════════════════════════════════════════════════════════════════════════════════
# LOADERS DESDE MySQL (datos históricos 2019-2023)
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def load_capacidad():
    return Q("""
        SELECT d.nombre AS departamento, d.region,
               fe.nombre AS fuente, fe.tipo, fe.codigo AS cod_fuente,
               ci.anio, ci.capacidad_mw,
               ci.proyectos_activos, ci.proyectos_en_construccion,
               ROUND(ci.inversion_cop/1e12,3) AS inversion_bill_cop
        FROM capacidad_instalada ci
        JOIN departamentos d ON ci.id_departamento = d.id_departamento
        JOIN fuentes_energia fe ON ci.id_fuente = fe.id_fuente
        ORDER BY ci.anio, ci.capacidad_mw DESC""")

@st.cache_data(ttl=600, show_spinner=False)
def load_consumo():
    return Q("""
        SELECT d.nombre AS departamento, d.region,
               ce.anio, ce.trimestre, ce.sector,
               ce.consumo_gwh, ce.costo_promedio_kwh, ce.usuarios
        FROM consumo_energetico ce
        JOIN departamentos d ON ce.id_departamento = d.id_departamento""")

@st.cache_data(ttl=600, show_spinner=False)
def load_emisiones():
    return Q("""
        SELECT d.nombre AS departamento, d.region,
               e.anio, e.sector,
               ROUND(e.co2_toneladas/1e6, 4) AS mt_co2,
               e.meta_reduccion_pct
        FROM emisiones_co2 e
        JOIN departamentos d ON e.id_departamento = d.id_departamento""")

@st.cache_data(ttl=600, show_spinner=False)
def load_proyectos():
    return Q("""
        SELECT d.nombre AS departamento, d.region,
               fe.nombre AS tipo_energia,
               p.nombre_proyecto, p.empresa, p.estado,
               p.capacidad_mw, p.inversion_musd, p.empleos_generados,
               p.municipio
        FROM proyectos_ernc p
        JOIN departamentos d ON p.id_departamento = d.id_departamento
        JOIN fuentes_energia fe ON p.id_fuente = fe.id_fuente""")

@st.cache_data(ttl=600, show_spinner=False)
def load_zni():
    return Q("""
        SELECT d.nombre AS departamento, d.region,
               z.nombre_zona, z.municipio, z.poblacion,
               z.tiene_energia, z.horas_servicio_dia,
               z.fuente_principal, z.proyecto_asignado
        FROM zonas_no_interconectadas z
        JOIN departamentos d ON z.id_departamento = d.id_departamento""")

# ════════════════════════════════════════════════════════════════════════════════
# LOADER FNCER UPME — datos.gov.co (vy9n-w6hc) — 2004-2025
# Fuente: Ministerio de Minas y Energía / UPME
# Actualización: automática desde la API pública
# ════════════════════════════════════════════════════════════════════════════════

# Normalización de nombres de departamento (CSV usa mayúsculas sin tildes)
_DEPTO_NORM = {
    "ANTIOQUIA":"Antioquia","ATLÁNTICO":"Atlantico","ATLANTICO":"Atlantico",
    "BOLÍVAR":"Bolivar","BOLIVAR":"Bolivar","BOYACÁ":"Boyaca","BOYACA":"Boyaca",
    "CALDAS":"Caldas","CAQUETÁ":"Caqueta","CAQUETA":"Caqueta",
    "CAUCA":"Cauca","CESAR":"Cesar","CHOCÓ":"Choco","CHOCO":"Choco",
    "CÓRDOBA":"Cordoba","CORDOBA":"Cordoba","CUNDINAMARCA":"Cundinamarca",
    "HUILA":"Huila","LA GUAJIRA":"La Guajira","MAGDALENA":"Magdalena",
    "META":"Meta","NARIÑO":"Narino","NARINO":"Narino",
    "NORTE DE SANTANDER":"Norte de Santander","QUINDÍO":"Quindio","QUINDIO":"Quindio",
    "RISARALDA":"Risaralda","SANTANDER":"Santander","SUCRE":"Sucre",
    "TOLIMA":"Tolima","VALLE DEL CAUCA":"Valle del Cauca",
    "CASANARE":"Casanare","AMAZONAS":"Amazonas","GUAINÍA":"Guainia","GUAINIA":"Guainia",
    "GUAVIARE":"Guaviare","VAUPÉS":"Vaupes","VAUPES":"Vaupes",
    "VICHADA":"Vichada","ARAUCA":"Arauca","PUTUMAYO":"Putumayo",
    "BOGOTÁ D.C.":"Bogota D.C.","BOGOTA D.C.":"Bogota D.C.",
    "ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA":"San Andres",
    "SAN ANDRES":"San Andres",
}

# Mapa tipo energía CSV → nombre BD
_TIPO_MAP = {
    "Solar":     "Solar Fotovoltaica",
    "Eólico":    "Eolica",
    "Eolico":    "Eolica",
    "Hidráulico":"Pequena Central Hidroelectrica",
    "Hidraulico":"Pequena Central Hidroelectrica",
    "Biomasa":   "Biomasa",
    "Geotérmico":"Geotermica",
    "Geotermico":"Geotermica",
}

# Regiones por departamento
_REGION = {
    "Antioquia":"Andina","Atlantico":"Caribe","Bogota D.C.":"Andina",
    "Bolivar":"Caribe","Boyaca":"Andina","Caldas":"Andina",
    "Caqueta":"Amazonica","Cauca":"Pacifica","Cesar":"Caribe",
    "Choco":"Pacifica","Cordoba":"Caribe","Cundinamarca":"Andina",
    "Huila":"Andina","La Guajira":"Caribe","Magdalena":"Caribe",
    "Meta":"Orinoquia","Narino":"Pacifica","Norte de Santander":"Andina",
    "Quindio":"Andina","Risaralda":"Andina","Santander":"Andina",
    "Sucre":"Caribe","Tolima":"Andina","Valle del Cauca":"Pacifica",
    "Casanare":"Orinoquia","Amazonas":"Amazonica","Guainia":"Amazonica",
    "Guaviare":"Amazonica","Vaupes":"Amazonica","Vichada":"Orinoquia",
    "Arauca":"Orinoquia","Putumayo":"Amazonica","San Andres":"Caribe",
}

@st.cache_data(ttl=3600, show_spinner=False)
def load_fncer_upme() -> pd.DataFrame:
    """
    Carga el dataset Meta FNCER de datos.gov.co (vy9n-w6hc).
    Incluye proyectos con FPO desde 2004 hasta 2025+.
    Columnas resultado:
        proyecto, tipo_energia, capacidad_mw, departamento, region,
        municipio, fecha_fpo, anio_fpo, energia_kwh_dia,
        usuarios, inversion_cop, inversion_musd, empleos,
        emisiones_co2_ton_anio, estado
    """
    try:
        df = pd.read_csv(URLS["fncer_upme"], encoding="utf-8")

        # Renombrar columnas
        df.columns = [c.strip() for c in df.columns]
        rename = {
            "Proyecto":                 "proyecto",
            "Tipo":                     "tipo_raw",
            "Capacidad":                "capacidad_mw",
            "Departamento":             "depto_raw",
            "Municipio":                "municipio",
            "Fecha estimada FPO":       "fecha_fpo",
            "Energía [kWh/día]":        "energia_kwh_dia",
            "Usuarios":                 "usuarios",
            "Inversión estimada [COP]": "inversion_cop",
            "Empleos estimados":        "empleos",
            "Emisiones CO2 [Ton/año]":  "emisiones_co2_ton_anio",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        # Limpiar y normalizar
        df["departamento"] = (df["depto_raw"].str.strip().str.upper()
                              .map(lambda x: _DEPTO_NORM.get(x, x.title())))
        df["region"]       = df["departamento"].map(_REGION).fillna("Otra")
        df["tipo_energia"] = df["tipo_raw"].str.strip().map(
            lambda x: _TIPO_MAP.get(x, x))

        # Fechas
        df["fecha_fpo"] = pd.to_datetime(df["fecha_fpo"], errors="coerce")
        df["anio_fpo"]  = df["fecha_fpo"].dt.year

        # Numéricos
        for col in ["capacidad_mw", "energia_kwh_dia", "usuarios",
                    "inversion_cop", "empleos", "emisiones_co2_ton_anio"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Inversión en MUSD (TRM ~4.000 COP/USD)
        df["inversion_musd"] = (df["inversion_cop"] / 4000 / 1e6).round(3)

        # Estado inferido desde fecha FPO
        hoy = pd.Timestamp.today()
        df["estado"] = df["fecha_fpo"].apply(
            lambda f: "operativo" if pd.notna(f) and f <= hoy else "proyectado"
        )

        cols = ["proyecto","tipo_energia","capacidad_mw","departamento",
                "region","municipio","fecha_fpo","anio_fpo",
                "energia_kwh_dia","usuarios","inversion_cop",
                "inversion_musd","empleos","emisiones_co2_ton_anio","estado"]
        return df[[c for c in cols if c in df.columns]].reset_index(drop=True)

    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar el dataset FNCER de datos.gov.co: {e}")
        return pd.DataFrame()


# ════════════════════════════════════════════════════════════════════════════════
# FUNCIÓN COMBINADA: proyectos BD + FNCER datos.gov.co
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def load_proyectos_completo() -> pd.DataFrame:
    """
    Combina los proyectos de la BD MySQL (históricos 2019-2023)
    con el dataset FNCER UPME de datos.gov.co (2004-2025+).
    Deduplica por nombre de proyecto (fuzzy: primeros 20 chars).
    """
    df_bd = load_proyectos()
    df_fncer = load_fncer_upme()

    if df_fncer.empty:
        return df_bd

    # Normalizar columnas del dataset FNCER al mismo esquema que BD
    df_fncer_norm = pd.DataFrame({
        "departamento":   df_fncer["departamento"],
        "region":         df_fncer["region"],
        "tipo_energia":   df_fncer["tipo_energia"],
        "nombre_proyecto":df_fncer["proyecto"],
        "empresa":        "UPME/Minminas",
        "estado":         df_fncer["estado"],
        "capacidad_mw":   df_fncer["capacidad_mw"],
        "inversion_musd": df_fncer["inversion_musd"],
        "empleos_generados": df_fncer["empleos"],
        "municipio":      df_fncer["municipio"],
        "anio_fpo":       df_fncer["anio_fpo"],
        "energia_kwh_dia":df_fncer["energia_kwh_dia"],
        "usuarios_fncer": df_fncer["usuarios"],
        "emisiones_co2_ton": df_fncer["emisiones_co2_ton_anio"],
        "fuente_dataset": "datos.gov.co — UPME FNCER (vy9n-w6hc)",
    })

    # Marcar BD como fuente
    df_bd["anio_fpo"] = None
    df_bd["energia_kwh_dia"] = None
    df_bd["usuarios_fncer"] = None
    df_bd["emisiones_co2_ton"] = None
    df_bd["fuente_dataset"] = "BD MySQL — UPME/IPSE"

    # Deduplicar: si el proyecto del FNCER ya existe en BD (match parcial)
    nombres_bd = set(df_bd["nombre_proyecto"].str[:20].str.upper())
    df_fncer_nuevo = df_fncer_norm[
        ~df_fncer_norm["nombre_proyecto"].str[:20].str.upper().isin(nombres_bd)
    ]

    combined = pd.concat([df_bd, df_fncer_nuevo], ignore_index=True)
    combined["capacidad_mw"] = pd.to_numeric(
        combined["capacidad_mw"], errors="coerce").fillna(0)

    return combined


# ════════════════════════════════════════════════════════════════════════════════
# DATOS CONTEXTUALES 2024-2025 (UPME — no en datos.gov.co aún)
# Fuente: UPME Balance de Gestión 2024, Plan 6GW+
# ════════════════════════════════════════════════════════════════════════════════

CONTEXTO_2024 = {
    "capacidad_solar_operacion_mw":    1348.55,
    "capacidad_solar_pruebas_mw":       731.34,
    "total_fncer_operacion_mw":        2079.89,
    "crecimiento_vs_2022_pct":            700,
    "meta_pnd_2026_mw":                2297.08,
    "avance_meta_pnd_pct":                80,
    "proyectos_activos_6gw":               82,
    "factor_emision_sin_gco2_kwh":        160,  # muy bajo vs mundo (475)
    "proyectos_destacados_2024": [
        {"nombre": "LATAM Solar La Loma",   "mw": 150, "depto": "Cesar",
         "municipio": "El Paso",   "tipo": "Solar Fotovoltaica"},
        {"nombre": "Porton del Sol",        "mw": 102, "depto": "Caldas",
         "municipio": "La Dorada", "tipo": "Solar Fotovoltaica"},
        {"nombre": "Parque Solar La Union", "mw": 100, "depto": "Cordoba",
         "municipio": "San Carlos","tipo": "Solar Fotovoltaica"},
        {"nombre": "Guajira 1 Wind Farm",   "mw": 198, "depto": "La Guajira",
         "municipio": "Maicao",    "tipo": "Eolica"},
        {"nombre": "Jepirachi II",          "mw": 204, "depto": "La Guajira",
         "municipio": "Uribia",    "tipo": "Eolica"},
    ],
    "fuente": "UPME — Informe de Gestion 2024 / Plan 6GW+ / datos.gov.co",
    "url_plan_6gw": "https://www.upme.gov.co/",
}
