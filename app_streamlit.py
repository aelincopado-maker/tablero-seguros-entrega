import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DATA = BASE / "datos" / "datos.parquet"
DB = BASE / "cartera.db"
st.set_page_config(page_title="Tablero de seguros | Analítica", layout="wide")

# Identidad visual: modo oscuro y acentos violetas.
st.markdown("""
<style>
/* Filtros violeta: multiselect, selectbox, slider y controles del cotizador. */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
[data-testid="stSidebar"] [data-baseweb="input"] > div {
  background: #2B1B42 !important; border: 1px solid #8B5CF6 !important;
  border-radius: 10px !important; color: #F5EDFF !important;
}
[data-baseweb="tag"],
[data-baseweb="tag"] > span,
[data-baseweb="tag"] > div,
[data-testid="stMultiSelect"] [data-baseweb="tag"],
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
  background: #7C3AED !important;
  background-color: #7C3AED !important;
  border-radius: 7px !important;
  color: #FFFFFF !important;
}
[data-baseweb="tag"] [role="presentation"],
[data-baseweb="tag"] [data-baseweb="icon"] { color: #FFFFFF !important; }
[data-baseweb="tag"] span, [data-baseweb="tag"] svg { color: #FFFFFF !important; fill: #FFFFFF !important; }
[data-baseweb="popover"] [role="option"]:hover,
[role="listbox"] [role="option"]:hover { background-color: #49306D !important; }
[data-baseweb="popover"] [aria-selected="true"],
[role="listbox"] [aria-selected="true"] { background-color: #513080 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { color: #D8B4FE !important; font-weight: 600; }
[data-testid="stSlider"] [role="slider"] { background: #A78BFA !important; border-color: #C4B5FD !important; }
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] { background-color: #A78BFA !important; }
[data-testid="stSlider"] [data-baseweb="slider"] > div > div { accent-color: #8B5CF6 !important; }
input[type="checkbox"], input[type="radio"], input[type="range"] { accent-color: #8B5CF6 !important; }
[data-testid="stSlider"] [data-testid="stTickBar"] { color: #D8B4FE !important; }
[data-testid="stForm"] [data-baseweb="select"] > div { border: 1px solid #8B5CF6 !important; }
[data-testid="stFormSubmitButton"] button { background: #7C3AED !important; color: white !important; border-color: #A78BFA !important; }
[data-testid="stFormSubmitButton"] button:hover { background: #9333EA !important; }
:root { color-scheme: dark; }
.stApp, [data-testid="stAppViewContainer"] { background: #0D0B15; color: #F5F3FF; }
[data-testid="stHeader"] { background: rgba(13,11,21,.88); }
[data-testid="stSidebar"] { background: #171225; border-right: 1px solid #392A55; }
[data-testid="stSidebar"] * { color: #F0EAFE; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1450px; }
h1, h2, h3 { color: #F5F0FF !important; letter-spacing: -.025em; }
h1 { font-weight: 800 !important; }
[data-testid="stMetric"] { background: linear-gradient(145deg,#211832,#171223); border: 1px solid #49346A; border-radius: 16px; padding: 18px 16px; box-shadow: 0 8px 22px #00000025; }
[data-testid="stMetricLabel"] { color: #C8B7E8; }
[data-testid="stMetricValue"] { color: #D6BCFA; }
div[data-testid="stForm"] { background: #191426; border: 1px solid #49346A; border-radius: 18px; padding: 22px; }
.stButton > button[kind="primary"], button[data-testid="stFormSubmitButton-primaryFormSubmitButton"] { background: #7C3AED; color: white; border: 0; border-radius: 10px; }
.stButton > button[kind="primary"]:hover { background: #9461F3; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div { background-color: #21192F !important; border-color: #5D467C !important; }
[data-testid="stDataFrame"], [data-testid="stExpander"] { border-radius: 12px; }
hr { border-color: #45325F; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar():
    if not DATA.exists():
        st.error("Falta datos/datos.parquet. Inclúyelo en el repositorio.")
        st.stop()
    df = pd.read_parquet(DATA)
    aliases = {
        "cobertura": ["cobertura", "coverage"],
        "sexo": ["sexo", "genero", "gender"],
        "uso": ["uso", "use"],
        "combustible": ["combustible", "fuel"],
        "edad": ["edad", "edad_conductor", "age"],
        "exposicion": ["exposicion", "exposición", "expo", "exposure"],
        "siniestros": ["siniestros", "n_siniestros", "num_siniestros", "nbclaim", "claims", "frecuencia_siniestros"],
        "costo": ["costo", "monto_total", "costo_total", "monto_siniestros", "importe_siniestros", "claimamount", "loss", "losses"],
    }
    lookup = {str(c).lower().strip(): c for c in df.columns}
    ren = {}
    for target, opts in aliases.items():
        for opt in opts:
            if opt in lookup:
                ren[lookup[opt]] = target
                break
    df = df.rename(columns=ren)
    required = list(aliases)
    missing = [c for c in required if c not in df]
    if missing:
        st.error(f"Columnas faltantes: {missing}. Columnas disponibles: {list(df.columns)}")
        st.stop()
    for c in ["exposicion", "siniestros", "costo", "edad"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=required)
    df = df[(df.exposicion > 0) & (df.siniestros >= 0) & (df.costo >= 0)]
    for c in ["cobertura", "sexo", "uso", "combustible"]:
        df[c] = df[c].astype(str)
    if df.empty:
        st.error("No hay registros válidos en el parquet.")
        st.stop()
    return df

def metricas(df):
    expo = float(df.exposicion.sum())
    n = float(df.siniestros.sum())
    costo = float(df.costo.sum())
    return expo, n, n / expo if expo else 0, costo / n if n else 0, costo / expo if expo else 0

def grupo(df, factor):
    g = df.groupby(factor, observed=True).agg(exposicion=("exposicion","sum"), siniestros=("siniestros","sum"), costo=("costo","sum")).reset_index()
    g["frecuencia"] = g.siniestros / g.exposicion
    g["prima_pura"] = g.costo / g.exposicion
    return g

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            cobertura TEXT, sexo TEXT, uso TEXT, combustible TEXT,
            edad INTEGER, exposicion REAL, prima_empirica REAL,
            prima_glm REAL, prima_precio REAL)""")

def guardar(datos):
    init_db()
    with sqlite3.connect(DB) as con:
        con.execute("""INSERT INTO cotizaciones
            (cobertura, sexo, uso, combustible, edad, exposicion,
            prima_empirica, prima_glm, prima_precio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", datos)


def guardar_google_sheets(datos):
    """Guarda una cotización en Google Sheets usando st.secrets.

    Devuelve (ok, mensaje). No expone credenciales ni datos sensibles.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        if "gcp_service_account" not in st.secrets or "google_sheet_id" not in st.secrets:
            return False, "Falta configurar gcp_service_account o google_sheet_id en st.secrets."

        info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        cliente = gspread.authorize(creds)
        libro = cliente.open_by_key(str(st.secrets["google_sheet_id"]))
        nombre_hoja = str(st.secrets.get("google_worksheet", "Cotizaciones"))
        try:
            hoja = libro.worksheet(nombre_hoja)
        except gspread.WorksheetNotFound:
            hoja = libro.add_worksheet(title=nombre_hoja, rows=1000, cols=12)
        encabezados = ["fecha_utc", "cobertura", "sexo", "uso", "combustible",
                       "edad", "exposicion", "prima_empirica", "prima_glm", "prima_precio"]
        if not hoja.row_values(1):
            hoja.append_row(encabezados, value_input_option="RAW")
        fila = [datetime.now(timezone.utc).isoformat(timespec="seconds"), *datos]
        hoja.append_row(fila, value_input_option="RAW")
        return True, "Cotización guardada correctamente en Google Sheets."
    except Exception as exc:
        # No mostrar el error completo: podría incluir datos de configuración.
        return False, ("No se pudo guardar en Google Sheets. Comprueba que el ID de la hoja "
                       "sea correcto, que esté compartida con la cuenta de servicio como Editor "
                       "y que las credenciales de st.secrets sean válidas. "
                       f"Tipo de error: {type(exc).__name__}.")

df = cargar()
st.title("🚗 Tablero de tarificación de seguros")
st.markdown("""
<div style="
    color: #C4B5FD;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 8px;
">
    Desarrollado por Jessica Copado
</div>
<p style="color: #A1A1AA;">
    Diplomado en Machine Learning en Seguros | Módulo 5
</p>
""", unsafe_allow_html=True)
st.caption("Análisis de frecuencia, severidad, prima pura y cotizador de tres etapas")

st.sidebar.header("✦ Filtros de cartera")
filtros = {}
for col in ["cobertura", "sexo", "uso", "combustible"]:
    valores = sorted(df[col].unique().tolist())
    filtros[col] = st.sidebar.multiselect(col.capitalize(), valores, default=valores)
min_age, max_age = int(df.edad.min()), int(df.edad.max())
if min_age < max_age:
    rango = st.sidebar.slider("Edad", min_age, max_age, (min_age, max_age))
else:
    rango = (min_age, max_age)
mask = df.edad.between(*rango)
for col, seleccion in filtros.items():
    mask &= df[col].isin(seleccion)
filtered = df.loc[mask].copy()
if filtered.empty:
    st.warning("No hay datos para los filtros elegidos. Modifica la selección.")
    st.stop()

expo, n, freq, sev, pura = metricas(filtered)
st.subheader("✦ Indicadores principales")
cols = st.columns(5)
for col, title, value in zip(cols,
    ["Exposición", "N.º siniestros", "Frecuencia", "Severidad", "Prima pura"],
    [f"{expo:,.2f}", f"{n:,.0f}", f"{freq:.2%}", f"${sev:,.2f}", f"${pura:,.2f}"]):
    col.metric(title, value)

st.subheader("✦ Frecuencia por factor")
factor = st.selectbox("Factor de segmentación", ["cobertura", "sexo", "uso", "combustible"])
g = grupo(filtered, factor)
fig, ax = plt.subplots(figsize=(10, 4), facecolor="#171223")
ax.set_facecolor("#171223")
colors = ["#6D28D9", "#7C3AED", "#8B5CF6", "#A78BFA", "#C4B5FD"]
bars = ax.bar(g[factor].astype(str), g["frecuencia"],
              color=[colors[i % len(colors)] for i in range(len(g))], width=0.65)
ax.set_ylabel("Siniestros / exposición", color="#DDD1F1")
ax.set_xlabel(factor.capitalize(), color="#DDD1F1")
ax.tick_params(axis="x", rotation=20, colors="#E5DAF7")
ax.tick_params(axis="y", colors="#E5DAF7")
ax.grid(axis="y", alpha=0.18, color="#C4B5FD")
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, pos: f"{v:.0%}"))
for bar in bars:
    h = bar.get_height()
    ax.annotate(f"{h:.1%}", (bar.get_x() + bar.get_width()/2, h),
                xytext=(0, 5), textcoords="offset points", ha="center",
                va="bottom", fontsize=9, color="#E9D5FF")
ax.margins(y=0.18)
fig.tight_layout()
st.pyplot(fig, width="stretch")
plt.close(fig)
st.dataframe(g, width="stretch", hide_index=True)

st.subheader("✦ Cotizador de seguros")
st.caption("ETAPA 1 · Prima empírica   →   ETAPA 2 · Prima GLM   →   ETAPA 3 · Prima precio")
with st.form("cotizador"):
    a,b,c,d = st.columns(4)
    cob = a.selectbox("Cobertura", sorted(df.cobertura.unique()))
    sex = b.selectbox("Sexo", sorted(df.sexo.unique()))
    uso = c.selectbox("Uso", sorted(df.uso.unique()))
    comb = d.selectbox("Combustible", sorted(df.combustible.unique()))
    e1,e2,e3 = st.columns(3)
    edad = e1.number_input("Edad", min_value=min_age, max_value=max_age, value=int(df.edad.median()))
    exposicion = e2.number_input("Exposición (años)", min_value=0.01, max_value=10.0, value=1.0, step=0.25)
    margen = e3.slider("Recargo comercial (%)", min_value=0, max_value=100, value=25)
    submit = st.form_submit_button("Calcular primas", type="primary")

if submit:
    # Empírico: segmento exacto; fallback a cobertura; finalmente cartera completa.
    seg = df[(df.cobertura == cob) & (df.sexo == sex) &
             (df.uso == uso) & (df.combustible == comb)]
    if seg.exposicion.sum() < 5:
        seg = df[df.cobertura == cob]
    if seg.empty:
        seg = df
    prima_emp = metricas(seg)[4] * exposicion

    # GLM Poisson para frecuencia con offset log(exposición) y
    # Gamma(log) para severidad en registros con siniestros.
    # Fallback explícito si la muestra no permite ajustar.
    prima_glm = prima_emp
    nota = ""
    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
        work = df.copy()
        work["edad_c"] = (work.edad - work.edad.mean()) / max(work.edad.std(), 1)
        nuevo = pd.DataFrame([{"cobertura":cob,"sexo":sex,"uso":uso,
                               "combustible":comb,"edad":edad}])
        nuevo["edad_c"] = (nuevo.edad - work.edad.mean()) / max(work.edad.std(), 1)
        formula = "siniestros ~ C(cobertura)+C(sexo)+C(uso)+C(combustible)+edad_c"
        mf = smf.glm(formula, data=work, family=sm.families.Poisson(),
                     offset=np.log(work.exposicion)).fit()
        f_pred = float(mf.predict(nuevo, offset=np.array([0.0])).iloc[0])
        sevdata = work[work.siniestros > 0].copy()
        sevdata["severidad_ind"] = sevdata.costo / sevdata.siniestros
        sevdata = sevdata[sevdata.severidad_ind > 0]
        if len(sevdata) < 10:
            raise ValueError("Pocos registros con siniestros positivos")
        ms = smf.glm("severidad_ind ~ C(cobertura)+C(sexo)+C(uso)+C(combustible)+edad_c",
                     data=sevdata, family=sm.families.Gamma(sm.families.links.Log()),
                     freq_weights=sevdata.siniestros).fit()
        s_pred = float(ms.predict(nuevo).iloc[0])
        prima_glm = max(0.0, f_pred * s_pred * exposicion)
        if not np.isfinite(prima_glm):
            raise ValueError("Predicción no finita")
    except (ValueError, KeyError, np.linalg.LinAlgError, ImportError) as exc:
        nota = f"GLM no estimable con estos datos: se usa la prima empírica como respaldo ({exc})."
    prima_precio = prima_glm * (1 + margen/100)
    x,y,z = st.columns(3)
    x.metric("1 · Prima empírica", f"${prima_emp:,.2f}")
    y.metric("2 · Prima GLM", f"${prima_glm:,.2f}")
    z.metric("3 · Prima precio", f"${prima_precio:,.2f}")
    if nota:
        st.warning(nota)
    datos_cotizacion = (cob, sex, uso, comb, int(edad), float(exposicion),
                        float(prima_emp), float(prima_glm), float(prima_precio))
    ok, mensaje = guardar_google_sheets(datos_cotizacion)
    if ok:
        st.success("☁️ " + mensaje)
    else:
        st.warning("Google Sheets: " + mensaje)
    try:
        guardar(datos_cotizacion)
        st.info("Copia local guardada en SQLite (cartera.db).")
    except sqlite3.Error:
        st.warning("No se pudo guardar la copia local en SQLite.")

with st.expander("Historial de cotizaciones (SQLite local)"):
    init_db()
    with sqlite3.connect(DB) as con:
        hist = pd.read_sql_query("SELECT * FROM cotizaciones ORDER BY id DESC LIMIT 100", con)
    st.dataframe(hist, width="stretch", hide_index=True)
    st.caption("En Streamlit Community Cloud este archivo puede perderse al reiniciar. No equivale al bonus de Google Sheets.")
