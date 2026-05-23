# database.py — Capa de Datos · Dashboard Transición Energética Colombia
# Bootcamp Talento Tech — Nivel Integrador 2025
# ──────────────────────────────────────────────────────────────────────────────
# FUENTES OFICIALES (datos.gov.co):
#   1. UPME  — Meta FNCER (vy9n-w6hc) · Proyectos 2004-2025
#   2. UPME  — Balance Energético · Consumo sectorial por dpto y trimestre
#   3. IPSE  — Cobertura Zonas No Interconectadas (ZNI)
#   4. IDEAM — Inventario Nacional GEI · Emisiones CO₂ por sector 2019-2023
#   5. DANE  — DIVIPOLA · División político-administrativa
#
# CONTEXTO UPME 2024-2025:
#   · Plan 6GW+: 82 proyectos solares/eólicos activos
#   · 1.348 MW solares en operación — crecimiento solar 2024: +187,3%
#   · FNCER representan 9% de capacidad total SIN a 2024
#   · Meta PND 2022-2026: 2.297 MW FNCER en operación
# ──────────────────────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE ACCESO
# ══════════════════════════════════════════════════════════════════════════════
_DB = dict(
    user     = "u748235332_energetica",
    password = "P4ulin4.*",
    host     = "82.197.82.63",
    port     = 3306,
    database = "u748235332_energetica",
)

_URLS = {
    "fncer_upme": (
        "https://www.datos.gov.co/api/views/vy9n-w6hc"
        "/rows.csv?accessType=DOWNLOAD"
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# ENGINE MYSQL
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_engine():
    """Retorna el engine SQLAlchemy con pool_pre_ping para reconexión."""
    url = (
        f"mysql+pymysql://{_DB['user']}:{_DB['password']}"
        f"@{_DB['host']}:{_DB['port']}/{_DB['database']}"
        f"?charset=utf8mb4"
    )
    return create_engine(
        url,
        pool_pre_ping   = True,
        pool_recycle    = 280,
        pool_size       = 3,
        max_overflow    = 5,
        connect_args    = {"connect_timeout": 10},
    )


def _query(sql: str) -> pd.DataFrame:
    """Ejecuta una consulta SQL y retorna un DataFrame; maneja errores con gracia."""
    try:
        return pd.read_sql(sql, get_engine())
    except (OperationalError, SQLAlchemyError) as exc:
        logger.warning("BD no disponible: %s", exc)
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
# TABLAS NORMALIZADAS MYSQL  (datos históricos 2019-2023)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def load_capacidad() -> pd.DataFrame:
    return _query("""
        SELECT
            d.nombre                          AS departamento,
            d.region,
            fe.nombre                         AS fuente,
            fe.tipo,
            fe.codigo                         AS cod_fuente,
            ci.anio,
            ci.capacidad_mw,
            ci.proyectos_activos,
            ci.proyectos_en_construccion,
            ROUND(ci.inversion_cop / 1e12, 3) AS inversion_bill_cop
        FROM  capacidad_instalada ci
        JOIN  departamentos   d  ON ci.id_departamento = d.id_departamento
        JOIN  fuentes_energia fe ON ci.id_fuente       = fe.id_fuente
        ORDER BY ci.anio, ci.capacidad_mw DESC
    """)


@st.cache_data(ttl=600, show_spinner=False)
def load_consumo() -> pd.DataFrame:
    return _query("""
        SELECT
            d.nombre  AS departamento,
            d.region,
            ce.anio,
            ce.trimestre,
            ce.sector,
            ce.consumo_gwh,
            ce.costo_promedio_kwh,
            ce.usuarios
        FROM  consumo_energetico ce
        JOIN  departamentos d ON ce.id_departamento = d.id_departamento
    """)


@st.cache_data(ttl=600, show_spinner=False)
def load_emisiones() -> pd.DataFrame:
    return _query("""
        SELECT
            d.nombre                          AS departamento,
            d.region,
            e.anio,
            e.sector,
            ROUND(e.co2_toneladas / 1e6, 4)  AS mt_co2,
            e.meta_reduccion_pct
        FROM  emisiones_co2 e
        JOIN  departamentos d ON e.id_departamento = d.id_departamento
    """)


@st.cache_data(ttl=600, show_spinner=False)
def load_proyectos() -> pd.DataFrame:
    return _query("""
        SELECT
            d.nombre    AS departamento,
            d.region,
            fe.nombre   AS tipo_energia,
            p.nombre_proyecto,
            p.empresa,
            p.estado,
            p.capacidad_mw,
            p.inversion_musd,
            p.empleos_generados,
            p.municipio
        FROM  proyectos_ernc p
        JOIN  departamentos   d  ON p.id_departamento = d.id_departamento
        JOIN  fuentes_energia fe ON p.id_fuente       = fe.id_fuente
    """)


@st.cache_data(ttl=600, show_spinner=False)
def load_zni() -> pd.DataFrame:
    return _query("""
        SELECT
            d.nombre  AS departamento,
            d.region,
            z.nombre_zona,
            z.municipio,
            z.poblacion,
            z.tiene_energia,
            z.horas_servicio_dia,
            z.fuente_principal,
            z.proyecto_asignado
        FROM  zonas_no_interconectadas z
        JOIN  departamentos d ON z.id_departamento = d.id_departamento
    """)


# ══════════════════════════════════════════════════════════════════════════════
# NORMALIZACIÓN FNCER — datos.gov.co (vy9n-w6hc)
# ══════════════════════════════════════════════════════════════════════════════

_DEPTO_NORM: dict[str, str] = {
    "ANTIOQUIA":                    "Antioquia",
    "ATLÁNTICO":                    "Atlantico",
    "ATLANTICO":                    "Atlantico",
    "BOLÍVAR":                      "Bolivar",
    "BOLIVAR":                      "Bolivar",
    "BOYACÁ":                       "Boyaca",
    "BOYACA":                       "Boyaca",
    "CALDAS":                       "Caldas",
    "CAQUETÁ":                      "Caqueta",
    "CAQUETA":                      "Caqueta",
    "CAUCA":                        "Cauca",
    "CESAR":                        "Cesar",
    "CHOCÓ":                        "Choco",
    "CHOCO":                        "Choco",
    "CÓRDOBA":                      "Cordoba",
    "CORDOBA":                      "Cordoba",
    "CUNDINAMARCA":                 "Cundinamarca",
    "HUILA":                        "Huila",
    "LA GUAJIRA":                   "La Guajira",
    "MAGDALENA":                    "Magdalena",
    "META":                         "Meta",
    "NARIÑO":                       "Narino",
    "NARINO":                       "Narino",
    "NORTE DE SANTANDER":           "Norte de Santander",
    "QUINDÍO":                      "Quindio",
    "QUINDIO":                      "Quindio",
    "RISARALDA":                    "Risaralda",
    "SANTANDER":                    "Santander",
    "SUCRE":                        "Sucre",
    "TOLIMA":                       "Tolima",
    "VALLE DEL CAUCA":              "Valle del Cauca",
    "CASANARE":                     "Casanare",
    "AMAZONAS":                     "Amazonas",
    "GUAINÍA":                      "Guainia",
    "GUAINIA":                      "Guainia",
    "GUAVIARE":                     "Guaviare",
    "VAUPÉS":                       "Vaupes",
    "VAUPES":                       "Vaupes",
    "VICHADA":                      "Vichada",
    "ARAUCA":                       "Arauca",
    "PUTUMAYO":                     "Putumayo",
    "BOGOTÁ D.C.":                  "Bogota D.C.",
    "BOGOTA D.C.":                  "Bogota D.C.",
    "ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA": "San Andres",
    "SAN ANDRES":                   "San Andres",
}

_TIPO_MAP: dict[str, str] = {
    "Solar":      "Solar Fotovoltaica",
    "Eólico":     "Eólica",
    "Eolico":     "Eólica",
    "Hidráulico": "Pequeña Central Hidroeléctrica",
    "Hidraulico": "Pequeña Central Hidroeléctrica",
    "Biomasa":    "Biomasa",
    "Geotérmico": "Geotérmica",
    "Geotermico": "Geotérmica",
}

_REGION_MAP: dict[str, str] = {
    "Antioquia": "Andina",      "Atlantico": "Caribe",
    "Bogota D.C.": "Andina",    "Bolivar": "Caribe",
    "Boyaca": "Andina",         "Caldas": "Andina",
    "Caqueta": "Amazónica",     "Cauca": "Pacífica",
    "Cesar": "Caribe",          "Choco": "Pacífica",
    "Cordoba": "Caribe",        "Cundinamarca": "Andina",
    "Huila": "Andina",          "La Guajira": "Caribe",
    "Magdalena": "Caribe",      "Meta": "Orinoquía",
    "Narino": "Pacífica",       "Norte de Santander": "Andina",
    "Quindio": "Andina",        "Risaralda": "Andina",
    "Santander": "Andina",      "Sucre": "Caribe",
    "Tolima": "Andina",         "Valle del Cauca": "Pacífica",
    "Casanare": "Orinoquía",    "Amazonas": "Amazónica",
    "Guainia": "Amazónica",     "Guaviare": "Amazónica",
    "Vaupes": "Amazónica",      "Vichada": "Orinoquía",
    "Arauca": "Orinoquía",      "Putumayo": "Amazónica",
    "San Andres": "Caribe",
}

# ══════════════════════════════════════════════════════════════════════════════
# LOADER FNCER — datos.gov.co (vy9n-w6hc)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def load_fncer_upme() -> pd.DataFrame:
    """
    Carga el dataset Meta FNCER de datos.gov.co (vy9n-w6hc).
    Rango temporal: 2004-2025+.

    Columnas resultantes:
        proyecto, tipo_energia, capacidad_mw, departamento, region,
        municipio, fecha_fpo, anio_fpo, energia_kwh_dia, usuarios,
        inversion_cop, inversion_musd, empleos,
        emisiones_co2_ton_anio, estado
    """
    try:
        raw = pd.read_csv(_URLS["fncer_upme"], encoding="utf-8")
        raw.columns = [c.strip() for c in raw.columns]

        _rename = {
            "Proyecto":                  "proyecto",
            "Tipo":                      "tipo_raw",
            "Capacidad":                 "capacidad_mw",
            "Departamento":              "depto_raw",
            "Municipio":                 "municipio",
            "Fecha estimada FPO":        "fecha_fpo",
            "Energía [kWh/día]":         "energia_kwh_dia",
            "Usuarios":                  "usuarios",
            "Inversión estimada [COP]":  "inversion_cop",
            "Empleos estimados":         "empleos",
            "Emisiones CO2 [Ton/año]":   "emisiones_co2_ton_anio",
        }
        df = raw.rename(columns={k: v for k, v in _rename.items()
                                 if k in raw.columns})

        # Normalización geográfica
        df["departamento"] = (
            df["depto_raw"].str.strip().str.upper()
            .map(lambda x: _DEPTO_NORM.get(x, x.title()))
        )
        df["region"]       = df["departamento"].map(_REGION_MAP).fillna("Otra")
        df["tipo_energia"] = (
            df["tipo_raw"].str.strip()
            .map(lambda x: _TIPO_MAP.get(x, x))
        )

        # Fechas
        df["fecha_fpo"] = pd.to_datetime(df["fecha_fpo"], errors="coerce")
        df["anio_fpo"]  = df["fecha_fpo"].dt.year

        # Numéricos
        for col in ["capacidad_mw", "energia_kwh_dia", "usuarios",
                    "inversion_cop", "empleos", "emisiones_co2_ton_anio"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Inversión en MUSD (TRM referencia: ~4.200 COP/USD, promedio 2024)
        df["inversion_musd"] = (df["inversion_cop"] / 4_200 / 1e6).round(3)

        # Estado: operativo si FPO ≤ hoy
        hoy = pd.Timestamp.today()
        df["estado"] = df["fecha_fpo"].apply(
            lambda f: "operativo" if pd.notna(f) and f <= hoy else "proyectado"
        )

        _cols = [
            "proyecto", "tipo_energia", "capacidad_mw",
            "departamento", "region", "municipio",
            "fecha_fpo", "anio_fpo",
            "energia_kwh_dia", "usuarios",
            "inversion_cop", "inversion_musd",
            "empleos", "emisiones_co2_ton_anio", "estado",
        ]
        return (df[[c for c in _cols if c in df.columns]]
                .reset_index(drop=True))

    except Exception as exc:
        st.warning(f"⚠ No se pudo cargar el dataset FNCER de datos.gov.co: {exc}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
# COMBINADO: proyectos BD + FNCER datos.gov.co
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def load_proyectos_completo() -> pd.DataFrame:
    """
    Fusiona proyectos de la BD MySQL (2019-2023) con el dataset
    FNCER UPME de datos.gov.co (2004-2025+).
    Deduplicación por coincidencia parcial de nombre (primeros 24 chars).
    """
    df_bd    = load_proyectos()
    df_fncer = load_fncer_upme()

    if df_fncer.empty:
        df_bd["fuente_dataset"] = "BD MySQL — UPME/IPSE"
        return df_bd

    # Normalizar FNCER al esquema BD
    df_fn_norm = pd.DataFrame({
        "departamento":    df_fncer["departamento"],
        "region":          df_fncer["region"],
        "tipo_energia":    df_fncer["tipo_energia"],
        "nombre_proyecto": df_fncer["proyecto"],
        "empresa":         "UPME / Minminas",
        "estado":          df_fncer["estado"],
        "capacidad_mw":    df_fncer["capacidad_mw"],
        "inversion_musd":  df_fncer["inversion_musd"],
        "empleos_generados": df_fncer["empleos"],
        "municipio":       df_fncer["municipio"],
        "anio_fpo":        df_fncer["anio_fpo"],
        "energia_kwh_dia": df_fncer["energia_kwh_dia"],
        "usuarios_fncer":  df_fncer["usuarios"],
        "emisiones_co2_ton": df_fncer["emisiones_co2_ton_anio"],
        "fuente_dataset":  "datos.gov.co — UPME FNCER (vy9n-w6hc)",
    })

    # Enriquecer BD con columnas adicionales
    for col in ["anio_fpo", "energia_kwh_dia", "usuarios_fncer",
                "emisiones_co2_ton"]:
        df_bd[col] = pd.NA
    df_bd["fuente_dataset"] = "BD MySQL — UPME/IPSE"

    # Deduplicar: descartar proyectos FNCER ya presentes en BD
    nombres_bd = set(df_bd["nombre_proyecto"].str[:24].str.upper())
    df_nuevos  = df_fn_norm[
        ~df_fn_norm["nombre_proyecto"].str[:24].str.upper()
        .isin(nombres_bd)
    ]

    combined = pd.concat([df_bd, df_nuevos], ignore_index=True)
    combined["capacidad_mw"] = (
        pd.to_numeric(combined["capacidad_mw"], errors="coerce").fillna(0)
    )
    return combined


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXTO 2024-2025 — UPME  (no disponible aún en datos.gov.co)
# Fuente: UPME Balance de Gestión 2024 / Plan 6GW+
# ══════════════════════════════════════════════════════════════════════════════

CONTEXTO_2024: dict = {
    "capacidad_solar_operacion_mw":   1_348.55,
    "capacidad_solar_pruebas_mw":       731.34,
    "total_fncer_operacion_mw":       2_079.89,
    "crecimiento_solar_vs_2022_pct":      700,
    "meta_pnd_2026_mw":               2_297.08,
    "avance_meta_pnd_pct":                 80,
    "proyectos_activos_6gw":               82,
    "factor_emision_sin_gco2_kwh":        160,   # vs 475 g CO₂/kWh mundial
    "proyectos_destacados_2024": [
        {"nombre": "LATAM Solar La Loma",    "mw": 150,
         "depto": "Cesar",      "municipio": "El Paso",    "tipo": "Solar Fotovoltaica"},
        {"nombre": "Portón del Sol",         "mw": 102,
         "depto": "Caldas",     "municipio": "La Dorada",  "tipo": "Solar Fotovoltaica"},
        {"nombre": "Parque Solar La Unión",  "mw": 100,
         "depto": "Córdoba",    "municipio": "San Carlos", "tipo": "Solar Fotovoltaica"},
        {"nombre": "Guajira 1 Wind Farm",    "mw": 198,
         "depto": "La Guajira", "municipio": "Maicao",     "tipo": "Eólica"},
        {"nombre": "Jepírachi II",           "mw": 204,
         "depto": "La Guajira", "municipio": "Uribia",     "tipo": "Eólica"},
    ],
    "fuente": "UPME — Informe de Gestión 2024 / Plan 6GW+ / datos.gov.co",
    "url_plan_6gw": "https://www.upme.gov.co/",
}