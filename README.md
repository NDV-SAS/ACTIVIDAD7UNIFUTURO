# Dashboard de Matricula de Pregrado en Bogota 2024

Dashboard interactivo para analizar la matricula de pregrado en Bogota durante el ano 2024.

## Deployment en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona este repositorio
5. Main file: `streamlit_app.py`
6. Click "Deploy"

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Datos

Los datos estan en formato Parquet (92% mas pequenos que Excel) para carga rapida:
- `data/matriculados.parquet` - Estudiantes matriculados
- `data/primer_curso.parquet` - Matriculados de primer curso
- `data/programas.parquet` - Programas SNIES

## Caracteristicas

- Distribucion de matricula por modalidad
- Tendencias 2024-I vs 2024-II
- Top programas por modalidad
- Principales instituciones
- Analisis de demanda vs oferta
- Matriz de oportunidades por area
