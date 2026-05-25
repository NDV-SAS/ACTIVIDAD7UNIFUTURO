import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Matrícula Pregrado Bogotá 2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos desde Parquet
@st.cache_data
def load_data():
    data_dir = Path(__file__).parent / "data"
    df_mat = pd.read_parquet(data_dir / "matriculados.parquet")
    df_primer = pd.read_parquet(data_dir / "primer_curso.parquet")
    df_prog = pd.read_parquet(data_dir / "programas.parquet")
    return df_mat, df_primer, df_prog

@st.cache_data
def get_bogota_data():
    df_mat, df_primer, df_prog = load_data()
    
    # Filtrar Bogotá
    bogota_mat = df_mat[df_mat['MUNICIPIO DE OFERTA DEL PROGRAMA'] == 'Bogotá, D.C.'].copy()
    
    # Mapeo de código SNIES a modalidad
    snies_modalidad = bogota_mat[['CÓDIGO SNIES DEL PROGRAMA', 'MODALIDAD']].drop_duplicates()
    
    # Unir con primer curso
    bogota_primer = df_primer.merge(
        snies_modalidad,
        left_on='Código_SNIES_programa',
        right_on='CÓDIGO SNIES DEL PROGRAMA',
        how='inner'
    )
    
    # Filtrar programas de Bogotá
    bogota_prog = df_prog[df_prog['MUNICIPIO_OFERTA_PROGRAMA'] == 'Bogotá, D.C.'].copy()
    
    return bogota_mat, bogota_primer, bogota_prog

# Cargar datos
bogota_mat, bogota_primer, bogota_prog = get_bogota_data()

# Header
st.title("📊 Matrícula de Pregrado en Bogotá 2024")
total_matricula = bogota_mat['MATRICULADOS'].sum()
st.markdown(f'<p class="subtitle">Total de estudiantes matriculados: {total_matricula:,}</p>', unsafe_allow_html=True)

# KPIs
col1, col2, col3, col4 = st.columns(4)

dist = bogota_mat.groupby('MODALIDAD')['MATRICULADOS'].sum().sort_values(ascending=False)
tendencia = bogota_mat.groupby(['MODALIDAD', 'SEMESTRE'])['MATRICULADOS'].sum().reset_index()
tendencia_pivot = tendencia.pivot(index='SEMESTRE', columns='MODALIDAD', values='MATRICULADOS').fillna(0)

# Calcular variación Virtual
if 'Virtual' in tendencia_pivot.columns and 1 in tendencia_pivot.index and 2 in tendencia_pivot.index:
    var_virtual = ((tendencia_pivot.loc[2, 'Virtual'] - tendencia_pivot.loc[1, 'Virtual']) / tendencia_pivot.loc[1, 'Virtual'] * 100)
else:
    var_virtual = 0

with col1:
    st.metric("Presencial", f"{dist.iloc[0]:,}", help="Estudiantes en modalidad presencial")
with col2:
    st.metric("Virtual", f"{dist.iloc[1]:,}", help="Estudiantes en modalidad virtual")
with col3:
    st.metric("Crecimiento Virtual", f"{var_virtual:+.1f}%", help="Variación 2024-I a 2024-II")
with col4:
    st.metric("Modalidades", f"{len(dist)}", help="Número de modalidades activas")

st.markdown("---")

# Fila 1: Distribución y Tendencia
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución de Matrícula por Modalidad")
    pct = (dist / dist.sum() * 100).round(1)
    fig_dist = go.Figure(data=[go.Pie(
        labels=dist.index,
        values=dist.values,
        hole=0.5,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig_dist.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_dist, use_container_width=True)

with col2:
    st.subheader("Tendencia de Matrícula 2024-I vs 2024-II")
    fig_tend = go.Figure()
    totales = tendencia_pivot.sum().sort_values(ascending=False)
    for modalidad in totales.index[:3]:
        fig_tend.add_trace(go.Scatter(
            x=['2024-I', '2024-II'],
            y=tendencia_pivot[modalidad].values,
            mode='lines+markers',
            name=modalidad,
            line=dict(width=3),
            marker=dict(size=10)
        ))
    fig_tend.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_tend, use_container_width=True)

st.markdown("---")

# Fila 2: Top Programas
col1, col2 = st.columns(2)

prog_modalidad = bogota_mat.groupby(['PROGRAMA ACADÉMICO', 'MODALIDAD'])['MATRICULADOS'].sum().reset_index()

with col1:
    st.subheader("Top 5 Programas Presenciales")
    df_pres = prog_modalidad[prog_modalidad['MODALIDAD'] == 'Presencial'].nlargest(5, 'MATRICULADOS').sort_values('MATRICULADOS', ascending=True)
    fig_pres = go.Figure(data=[go.Bar(
        x=df_pres['MATRICULADOS'],
        y=df_pres['PROGRAMA ACADÉMICO'],
        orientation='h'
    )])
    fig_pres.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_pres, use_container_width=True)

with col2:
    st.subheader("Top 5 Programas Virtuales")
    df_virt = prog_modalidad[prog_modalidad['MODALIDAD'] == 'Virtual'].nlargest(5, 'MATRICULADOS').sort_values('MATRICULADOS', ascending=True)
    fig_virt = go.Figure(data=[go.Bar(
        x=df_virt['MATRICULADOS'],
        y=df_virt['PROGRAMA ACADÉMICO'],
        orientation='h'
    )])
    fig_virt.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_virt, use_container_width=True)

st.markdown("---")

# Fila 3: Instituciones y Demanda
col1, col2 = st.columns(2)

with col1:
    st.subheader("Principales Instituciones (Presencial)")
    inst_modalidad = bogota_mat.groupby(['INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)', 'MODALIDAD'])['MATRICULADOS'].sum().reset_index()
    df_inst = inst_modalidad[inst_modalidad['MODALIDAD'] == 'Presencial'].nlargest(8, 'MATRICULADOS').sort_values('MATRICULADOS', ascending=True)
    fig_inst = go.Figure(data=[go.Bar(
        x=df_inst['MATRICULADOS'],
        y=df_inst['INSTITUCIÓN DE EDUCACIÓN SUPERIOR (IES)'],
        orientation='h'
    )])
    fig_inst.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_inst, use_container_width=True)

with col2:
    st.subheader("Demanda Nueva vs Oferta Activa")
    primer_curso = bogota_primer.groupby('MODALIDAD')['Número de matriculados'].sum()
    programas_activos = bogota_prog.groupby('MODALIDAD').size()
    df_demanda = pd.DataFrame({
        'Modalidad': primer_curso.index,
        'Primer Curso': primer_curso.values,
        'Programas Activos': [programas_activos.get(m, 0) for m in primer_curso.index]
    }).sort_values('Primer Curso', ascending=False).head(4)
    
    fig_demanda = go.Figure()
    fig_demanda.add_trace(go.Bar(
        x=df_demanda['Modalidad'],
        y=df_demanda['Primer Curso'],
        name='Primer Curso',
        yaxis='y'
    ))
    fig_demanda.add_trace(go.Scatter(
        x=df_demanda['Modalidad'],
        y=df_demanda['Programas Activos'],
        name='Programas',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=12),
        yaxis='y2'
    ))
    fig_demanda.update_layout(
        height=400,
        yaxis=dict(title="Estudiantes Primer Curso", side='left'),
        yaxis2=dict(title="Programas Activos", side='right', overlaying='y')
    )
    st.plotly_chart(fig_demanda, use_container_width=True)

st.markdown("---")

# Matriz de Oportunidades
st.subheader("Matriz de Oportunidades por Área y Modalidad")
st.caption("Índice = % Demanda Nueva - % Oferta Activa (valores positivos indican oportunidad)")

# Calcular matriz
primer_area = bogota_primer.merge(
    bogota_mat[['CÓDIGO SNIES DEL PROGRAMA', 'ÁREA DE CONOCIMIENTO']].drop_duplicates(),
    left_on='Código_SNIES_programa',
    right_on='CÓDIGO SNIES DEL PROGRAMA',
    how='left'
)

demanda = primer_area.groupby(['ÁREA DE CONOCIMIENTO', 'MODALIDAD'])['Número de matriculados'].sum().reset_index()
demanda_pivot = demanda.pivot(index='ÁREA DE CONOCIMIENTO', columns='MODALIDAD', values='Número de matriculados').fillna(0)

oferta = bogota_prog.groupby(['ÁREA_DE_CONOCIMIENTO', 'MODALIDAD']).size().reset_index(name='Programas')
oferta_pivot = oferta.pivot(index='ÁREA_DE_CONOCIMIENTO', columns='MODALIDAD', values='Programas').fillna(0)

areas_comunes = demanda_pivot.index.intersection(oferta_pivot.index)
demanda_pivot = demanda_pivot.loc[areas_comunes]
oferta_pivot = oferta_pivot.loc[areas_comunes]

oportunidad = pd.DataFrame(index=demanda_pivot.index, columns=demanda_pivot.columns)

for modalidad in demanda_pivot.columns:
    if modalidad in oferta_pivot.columns:
        pct_demanda = (demanda_pivot[modalidad] / demanda_pivot[modalidad].sum() * 100)
        pct_oferta = (oferta_pivot[modalidad] / oferta_pivot[modalidad].sum() * 100)
        oportunidad[modalidad] = pct_demanda - pct_oferta

oportunidad = oportunidad.fillna(0).astype(float)

modalidades_principales = ['Presencial', 'Virtual', 'A distancia']
oportunidad_filtrado = oportunidad[[col for col in modalidades_principales if col in oportunidad.columns]]

fig_oport = go.Figure(data=go.Heatmap(
    z=oportunidad_filtrado.values,
    x=oportunidad_filtrado.columns,
    y=oportunidad_filtrado.index,
    colorscale='RdYlGn',
    zmid=0,
    text=oportunidad_filtrado.values.round(1),
    texttemplate='%{text}',
    textfont={"size": 9},
    colorbar=dict(title="Índice")
))
fig_oport.update_layout(height=500)
st.plotly_chart(fig_oport, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #95a5a6; font-size: 0.9rem;">Dashboard de Análisis de Matrícula de Pregrado en Bogotá, 2024</p>',
    unsafe_allow_html=True
)

def display():
    return {"_display_type": "stats", "stats": [("Streamlit App", "Creado")]}

# --- Execute display() ---
"""Serializes and outputs the result of display() for the Plotly Studio runtime."""

import json
import traceback

from utils.display_util import _dumps, _serialize_result  # type: ignore[import-not-found]

if __name__ == "__main__":
    try:
        if "display" in dir():
            _result = display()  # type: ignore[name-defined]  # noqa: F821 - defined in user code
        else:
            # Fallback for data modules that define classes/functions but no display().
            # Just report success so the step doesn't error out.
            _result = {
                "_display_type": "stats",
                "stats": [("Status", "Module loaded successfully")],
            }
        _serialized = _serialize_result(_result)
        _json_str = _dumps(_serialized)
    except Exception as _display_err:
        _json_str = json.dumps({"type": "error", "value": traceback.format_exc()})
    print("__RESULT_START__")
    print(_json_str)
    print("__RESULT_END__")
