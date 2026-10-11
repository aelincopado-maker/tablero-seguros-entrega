# Tablero actuarial de seguros

Aplicación Streamlit para explorar KPIs de cartera, segmentar riesgos y cotizar mediante prima empírica y GLM Poisson/Gamma.

## Preparación

1. Coloca el **archivo de datos autorizado** en `datos/datos.parquet`.
2. Instala dependencias: `python -m pip install -r requirements.txt`.
3. Ejecuta: `python -m streamlit run app_streamlit.py`.
4. Verifica los alias de columnas en `app_streamlit.py` contra el parquet de clase.

La aplicación reconstruye `cartera.db` desde Parquet. No se debe subir la base SQLite ni información personal de asegurados a un repositorio público.

## Publicación

Crea un repositorio público en GitHub, sube estos archivos y despliega desde https://share.streamlit.io usando rama `main` y archivo principal `app_streamlit.py`.

**Nota:** Es una plantilla de implementación basada en la rúbrica; se deben validar los modelos y resultados con la cartera y el código original de clase antes de entregar.
