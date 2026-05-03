# database.py — Conexión MySQL y carga de datasets con caché Streamlit
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# ── Credenciales ───────────────────────────────────────────────────────────────
DB = dict(
    user     = "u748235332_energetica",
    password = "P4ulin4.*",
    host     = "82.197.82.63",
    port     = 3306,
    database = "u748235332_energetica",
)

@st.cache_resource(show_spinner=False)
def get_engine():
    url = (
        f"mysql+pymysql://{DB['user']}:{DB['password']}"
        f"@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8mb4"
    )
    return create_engine(url, pool_pre_ping=True)

def Q(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, get_engine())

# ── Datasets — todos cacheados 10 min ─────────────────────────────────────────
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
