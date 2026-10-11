## Aplicación publicada

El tablero actuarial de seguros se encuentra disponible en Streamlit Cloud:

**[Acceder al tablero de tarificación de seguros](https://tablero-seguros-entrega-pujkpyhgqkynunqve562hp.streamlit.app/)**

La aplicación permite consultar indicadores de cartera, analizar factores de riesgo y realizar cotizaciones de seguros mediante una interfaz interactiva.

## Funcionalidades del tablero

### 1. Filtros interactivos

El tablero permite segmentar la cartera de seguros mediante filtros de:

- **Cobertura:** tipo de protección contratada.
- **Sexo:** segmentación de los asegurados o conductores.
- **Uso:** clasificación del uso del vehículo.
- **Combustible:** tipo de combustible del vehículo.
- **Edad:** selección de rangos de edad.

Estos filtros permiten analizar diferentes perfiles de riesgo y observar cómo cambian los indicadores y las visualizaciones según la selección realizada.

### 2. Indicadores principales (KPIs)

La aplicación presenta cinco indicadores actuariales:

- **Exposición:** medida del tiempo o volumen de riesgo asegurado.
- **Número de siniestros:** cantidad de eventos registrados en la cartera seleccionada.
- **Frecuencia:** relación entre el número de siniestros y la exposición.
- **Severidad:** costo promedio de los siniestros.
- **Prima pura:** costo esperado de siniestralidad por unidad de exposición, calculado a partir de la frecuencia y la severidad.

Estos indicadores permiten evaluar el comportamiento de la cartera y comprender los componentes fundamentales de la tarificación.

### 3. Visualizaciones interactivas

El tablero incorpora gráficas para analizar la frecuencia de siniestros por factores de segmentación.

Las visualizaciones facilitan la comparación entre categorías y ayudan a identificar diferencias en el comportamiento del riesgo.

### 4. Cotizador actuarial de seguros

La aplicación incluye un cotizador que permite estimar primas para distintos perfiles de riesgo mediante tres etapas de cálculo.

El objetivo es comparar las estimaciones obtenidas mediante enfoques empíricos y modelos estadísticos de frecuencia y severidad.

El proyecto contempla modelos lineales generalizados (GLM), incluyendo distribuciones Poisson para frecuencia y Gamma para severidad.

La cotización permite relacionar las características del perfil seleccionado con el costo esperado del seguro.

## Bonus: integración con Google Sheets

Como funcionalidad adicional, el proyecto incorpora persistencia de cotizaciones mediante Google Sheets.

Esta integración permite conservar un registro de las cotizaciones generadas desde la aplicación publicada, facilitando su consulta y seguimiento.

### Funcionamiento

1. El usuario ingresa o selecciona las características del perfil que desea cotizar.
2. El cotizador realiza los cálculos correspondientes.
3. La aplicación registra la información de la cotización en una hoja de Google Sheets.
4. Las cotizaciones guardadas pueden consultarse posteriormente.

### Configuración y seguridad

La conexión con Google Sheets se realiza mediante una cuenta de servicio de Google Cloud.

Las credenciales se configuran mediante los secretos de Streamlit Cloud y no deben publicarse en el repositorio de GitHub.

Para utilizar esta funcionalidad en otro despliegue, es necesario configurar las credenciales correspondientes y conceder a la cuenta de servicio los permisos necesarios sobre la hoja de cálculo.

### Beneficios

- Persistencia de cotizaciones.
- Registro de resultados para consultas posteriores.
- Integración con un servicio externo.
- Separación entre el código público y las credenciales privadas.

## Tecnologías utilizadas

- **Python:** desarrollo y procesamiento de datos.
- **Streamlit:** construcción y publicación del tablero.
- **Pandas:** manipulación y análisis de información.
- **Parquet:** almacenamiento de los datos utilizados por la aplicación.
- **Modelos GLM:** estimación actuarial de frecuencia y severidad.
- **Google Sheets API:** registro de cotizaciones.
- **GitHub:** control de versiones y publicación del código.
- **Streamlit Community Cloud:** alojamiento de la aplicación.
