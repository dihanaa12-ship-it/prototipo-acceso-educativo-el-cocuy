import os
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st


APP_TITLE = "Sistema IA para el Analisis del Acceso Educativo en El Cocuy"
DATA_PATH = os.path.join("data", "datos_acceso_educativo_el_cocuy.csv")


CONECTIVIDAD_VALORES = ["Sin conectividad", "Baja", "Media", "Alta"]
ZONA_VALORES = ["Rural", "Urbana"]
SI_NO = ["Si", "No"]
ESTABILIDAD_VALORES = ["Baja", "Media", "Alta"]
FRECUENCIA_VALORES = ["Nunca", "Ocasional", "Semanal", "Diaria"]
APOYO_VALORES = ["Bajo", "Medio", "Alto"]


COLUMNAS_BASE = [
    "id_caso",
    "institucion",
    "zona",
    "vereda_o_sector",
    "conectividad",
    "tiene_computador",
    "tiene_celular",
    "acceso_internet_hogar",
    "distancia_institucion_km",
    "estabilidad_electrica",
    "frecuencia_uso_plataformas",
    "apoyo_familiar",
]


st.set_page_config(page_title=APP_TITLE, page_icon="📚", layout="wide")


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def calcular_puntaje_riesgo(fila):
    """Calcula un puntaje de riesgo de acceso educativo entre 0 y 100.

    La logica se basa en reglas ponderadas propias de un prototipo TRL5.
    No pretende reemplazar una validacion estadistica con datos reales.
    """
    puntaje = 0

    zona = normalizar_texto(fila.get("zona"))
    conectividad = normalizar_texto(fila.get("conectividad"))
    computador = normalizar_texto(fila.get("tiene_computador"))
    celular = normalizar_texto(fila.get("tiene_celular"))
    internet = normalizar_texto(fila.get("acceso_internet_hogar"))
    electricidad = normalizar_texto(fila.get("estabilidad_electrica"))
    frecuencia = normalizar_texto(fila.get("frecuencia_uso_plataformas"))
    apoyo = normalizar_texto(fila.get("apoyo_familiar"))

    try:
        distancia = float(fila.get("distancia_institucion_km", 0))
    except (TypeError, ValueError):
        distancia = 0

    if zona == "Rural":
        puntaje += 15

    puntaje += {
        "Sin conectividad": 25,
        "Baja": 18,
        "Media": 8,
        "Alta": 0,
    }.get(conectividad, 10)

    if computador == "No":
        puntaje += 10

    if celular == "No":
        puntaje += 8

    if internet == "No":
        puntaje += 20

    if distancia > 15:
        puntaje += 15
    elif distancia > 8:
        puntaje += 10
    elif distancia > 3:
        puntaje += 5

    puntaje += {"Baja": 8, "Media": 4, "Alta": 0}.get(electricidad, 4)
    puntaje += {"Nunca": 12, "Ocasional": 8, "Semanal": 4, "Diaria": 0}.get(frecuencia, 6)
    puntaje += {"Bajo": 8, "Medio": 4, "Alto": 0}.get(apoyo, 4)

    return int(min(100, puntaje))


def clasificar_nivel_riesgo(puntaje):
    if puntaje >= 60:
        return "Alto"
    if puntaje >= 35:
        return "Medio"
    return "Bajo"


def generar_recomendacion(fila):
    recomendaciones = []

    if fila["nivel_riesgo"] == "Alto":
        recomendaciones.append("Priorizar acompanamiento institucional y seguimiento docente.")
    elif fila["nivel_riesgo"] == "Medio":
        recomendaciones.append("Realizar seguimiento preventivo y fortalecer recursos digitales disponibles.")
    else:
        recomendaciones.append("Mantener condiciones actuales y monitorear cambios en el acceso educativo.")

    if fila["conectividad"] in ["Sin conectividad", "Baja"]:
        recomendaciones.append("Gestionar alternativas de conectividad comunitaria o acceso offline a contenidos.")

    if fila["tiene_computador"] == "No":
        recomendaciones.append("Evaluar prestamo, donacion o uso compartido de equipos tecnologicos.")

    if fila["acceso_internet_hogar"] == "No":
        recomendaciones.append("Habilitar puntos de acceso a internet en institucion, biblioteca o centro comunitario.")

    if fila["distancia_institucion_km"] > 8:
        recomendaciones.append("Considerar estrategias flexibles por distancia, transporte o actividades asincronicas.")

    if fila["frecuencia_uso_plataformas"] in ["Nunca", "Ocasional"]:
        recomendaciones.append("Implementar orientacion basica sobre uso de plataformas educativas.")

    return " ".join(recomendaciones)


def preparar_datos(df):
    df = df.copy()

    for columna in COLUMNAS_BASE:
        if columna not in df.columns:
            df[columna] = ""

    df["distancia_institucion_km"] = pd.to_numeric(
        df["distancia_institucion_km"], errors="coerce"
    ).fillna(0)

    df["puntaje_riesgo"] = df.apply(calcular_puntaje_riesgo, axis=1)
    df["nivel_riesgo"] = df["puntaje_riesgo"].apply(clasificar_nivel_riesgo)
    df["recomendacion"] = df.apply(generar_recomendacion, axis=1)
    return df


def cargar_datos_iniciales():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame(columns=COLUMNAS_BASE)


def inicializar_estado():
    if "datos" not in st.session_state:
        st.session_state["datos"] = preparar_datos(cargar_datos_iniciales())


def mostrar_metricas(df):
    total = len(df)
    riesgo_alto = int((df["nivel_riesgo"] == "Alto").sum()) if total else 0
    riesgo_medio = int((df["nivel_riesgo"] == "Medio").sum()) if total else 0
    riesgo_bajo = int((df["nivel_riesgo"] == "Bajo").sum()) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Casos analizados", total)
    c2.metric("Riesgo alto", riesgo_alto)
    c3.metric("Riesgo medio", riesgo_medio)
    c4.metric("Riesgo bajo", riesgo_bajo)


def grafico_conteo(df, columna, titulo):
    st.subheader(titulo)
    if df.empty:
        st.info("No hay datos disponibles para graficar.")
        return
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = [columna, "cantidad"]
    st.bar_chart(conteo.set_index(columna))


def pagina_inicio():
    st.title(APP_TITLE)
    st.write(
        "Prototipo funcional TRL5 para analizar condiciones de acceso educativo "
        "en el municipio de El Cocuy, Boyaca, a partir de variables de conectividad, "
        "ubicacion, disponibilidad tecnologica y uso de plataformas digitales."
    )

    st.info(
        "Este sistema es un prototipo academico en ambiente simulado. No utiliza datos "
        "personales reales y no reemplaza decisiones institucionales. Su objetivo es validar "
        "la logica funcional de analisis, clasificacion de riesgo y generacion de recomendaciones."
    )

    st.markdown("### Modulos del prototipo")
    st.markdown(
        """
        1. **Datos:** carga CSV o registro manual de casos.
        2. **Diagnostico:** visualizacion de indicadores generales.
        3. **Clasificacion IA:** calculo de puntaje y nivel de riesgo.
        4. **Recomendaciones:** acciones sugeridas segun las condiciones detectadas.
        5. **Reporte TRL5:** resumen y descarga de resultados.
        """
    )


def pagina_datos():
    st.title("Datos de acceso educativo")
    st.write("Use la base simulada incluida o cargue un archivo CSV con la misma estructura.")

    archivo = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if archivo is not None:
        df_cargado = pd.read_csv(archivo)
        st.session_state["datos"] = preparar_datos(df_cargado)
        st.success("Archivo cargado y procesado correctamente.")

    st.markdown("### Registrar caso manual")
    with st.form("formulario_caso"):
        c1, c2, c3 = st.columns(3)
        with c1:
            id_caso = st.text_input("ID del caso", value=f"CASO-{len(st.session_state['datos']) + 1:03d}")
            institucion = st.text_input("Institucion educativa", value="Institucion Educativa El Cocuy")
            zona = st.selectbox("Zona", ZONA_VALORES)
            vereda_o_sector = st.text_input("Vereda o sector", value="Sector rural")
        with c2:
            conectividad = st.selectbox("Nivel de conectividad", CONECTIVIDAD_VALORES)
            tiene_computador = st.selectbox("Tiene computador", SI_NO)
            tiene_celular = st.selectbox("Tiene celular", SI_NO)
            acceso_internet = st.selectbox("Internet en el hogar", SI_NO)
        with c3:
            distancia = st.number_input("Distancia a la institucion (km)", min_value=0.0, max_value=60.0, value=5.0, step=0.5)
            electricidad = st.selectbox("Estabilidad electrica", ESTABILIDAD_VALORES)
            frecuencia = st.selectbox("Uso de plataformas digitales", FRECUENCIA_VALORES)
            apoyo = st.selectbox("Apoyo familiar", APOYO_VALORES)

        enviar = st.form_submit_button("Agregar caso")
        if enviar:
            nuevo = pd.DataFrame([
                {
                    "id_caso": id_caso,
                    "institucion": institucion,
                    "zona": zona,
                    "vereda_o_sector": vereda_o_sector,
                    "conectividad": conectividad,
                    "tiene_computador": tiene_computador,
                    "tiene_celular": tiene_celular,
                    "acceso_internet_hogar": acceso_internet,
                    "distancia_institucion_km": distancia,
                    "estabilidad_electrica": electricidad,
                    "frecuencia_uso_plataformas": frecuencia,
                    "apoyo_familiar": apoyo,
                }
            ])
            datos_base = st.session_state["datos"][COLUMNAS_BASE]
            st.session_state["datos"] = preparar_datos(pd.concat([datos_base, nuevo], ignore_index=True))
            st.success("Caso agregado correctamente.")

    st.markdown("### Base de datos procesada")
    st.dataframe(st.session_state["datos"], use_container_width=True)


def pagina_diagnostico():
    st.title("Diagnostico general")
    df = st.session_state["datos"]
    mostrar_metricas(df)

    c1, c2 = st.columns(2)
    with c1:
        grafico_conteo(df, "zona", "Distribucion por zona")
        grafico_conteo(df, "conectividad", "Nivel de conectividad")
    with c2:
        grafico_conteo(df, "nivel_riesgo", "Nivel de riesgo calculado")
        grafico_conteo(df, "acceso_internet_hogar", "Acceso a internet en el hogar")

    st.markdown("### Promedios relevantes")
    if not df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Distancia promedio a la institucion", f"{df['distancia_institucion_km'].mean():.1f} km")
        c2.metric("Puntaje promedio de riesgo", f"{df['puntaje_riesgo'].mean():.1f}/100")


def pagina_clasificacion():
    st.title("Clasificacion IA del riesgo educativo")
    df = st.session_state["datos"]
    st.write(
        "El prototipo calcula un puntaje de riesgo mediante reglas ponderadas. "
        "Esta logica representa una inteligencia artificial basica de apoyo a la decision "
        "en ambiente simulado TRL5."
    )

    if df.empty:
        st.warning("No hay datos para clasificar.")
        return

    filtro = st.multiselect(
        "Filtrar por nivel de riesgo",
        options=["Alto", "Medio", "Bajo"],
        default=["Alto", "Medio", "Bajo"],
    )
    df_filtrado = df[df["nivel_riesgo"].isin(filtro)]

    columnas = [
        "id_caso",
        "institucion",
        "zona",
        "conectividad",
        "acceso_internet_hogar",
        "distancia_institucion_km",
        "puntaje_riesgo",
        "nivel_riesgo",
    ]
    st.dataframe(df_filtrado[columnas].sort_values("puntaje_riesgo", ascending=False), use_container_width=True)

    st.markdown("### Criterios usados por el prototipo")
    st.markdown(
        """
        - Mayor riesgo si el caso pertenece a zona rural.
        - Mayor riesgo si presenta baja conectividad o ausencia de internet en el hogar.
        - Mayor riesgo si no cuenta con computador o celular.
        - Mayor riesgo si la distancia a la institucion es elevada.
        - Mayor riesgo si hay baja estabilidad electrica o baja frecuencia de uso de plataformas digitales.
        - Mayor riesgo si el apoyo familiar reportado es bajo.
        """
    )


def pagina_recomendaciones():
    st.title("Recomendaciones automaticas")
    df = st.session_state["datos"]

    if df.empty:
        st.warning("No hay datos para generar recomendaciones.")
        return

    nivel = st.selectbox("Seleccione nivel de riesgo", ["Alto", "Medio", "Bajo"])
    df_filtrado = df[df["nivel_riesgo"] == nivel]

    st.write(f"Casos encontrados con riesgo {nivel.lower()}: {len(df_filtrado)}")
    for _, fila in df_filtrado.iterrows():
        with st.expander(f"{fila['id_caso']} - {fila['institucion']} - Riesgo {fila['nivel_riesgo']}"):
            st.write(f"**Zona:** {fila['zona']}")
            st.write(f"**Conectividad:** {fila['conectividad']}")
            st.write(f"**Distancia:** {fila['distancia_institucion_km']} km")
            st.write(f"**Puntaje:** {fila['puntaje_riesgo']}/100")
            st.write(f"**Recomendacion:** {fila['recomendacion']}")


def pagina_reporte():
    st.title("Reporte TRL5")
    df = st.session_state["datos"]
    mostrar_metricas(df)

    st.markdown("### Interpretacion tecnica")
    st.write(
        "El prototipo se considera TRL5 porque permite validar, en un ambiente simulado "
        "y controlado, las funciones principales del sistema: entrada de datos, procesamiento, "
        "clasificacion de riesgo, visualizacion de indicadores y generacion de recomendaciones."
    )

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Fecha de generacion del reporte: {fecha}")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar reporte CSV",
        data=csv,
        file_name="reporte_acceso_educativo_el_cocuy.csv",
        mime="text/csv",
    )

    st.markdown("### Limitaciones del prototipo")
    st.markdown(
        """
        - Usa datos simulados y no informacion personal real.
        - La clasificacion corresponde a reglas ponderadas de apoyo a la decision.
        - Requiere validacion futura con datos institucionales reales.
        - No reemplaza el criterio de docentes, directivos o entidades educativas.
        """
    )


def main():
    inicializar_estado()

    st.sidebar.title("Menu")
    pagina = st.sidebar.radio(
        "Seleccione un modulo",
        [
            "Inicio",
            "Datos",
            "Diagnostico",
            "Clasificacion IA",
            "Recomendaciones",
            "Reporte TRL5",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Proyecto de grado - Prototipo funcional TRL5")

    if pagina == "Inicio":
        pagina_inicio()
    elif pagina == "Datos":
        pagina_datos()
    elif pagina == "Diagnostico":
        pagina_diagnostico()
    elif pagina == "Clasificacion IA":
        pagina_clasificacion()
    elif pagina == "Recomendaciones":
        pagina_recomendaciones()
    elif pagina == "Reporte TRL5":
        pagina_reporte()


if __name__ == "__main__":
    main()
