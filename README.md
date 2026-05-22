# Sistema IA para el Analisis del Acceso Educativo en El Cocuy

Prototipo funcional TRL5 desarrollado como apoyo al proyecto de grado **Sistema basado en inteligencia artificial para el mejoramiento del acceso a los servicios educativos en el municipio de El Cocuy, Boyaca**.

## Objetivo

Analizar condiciones de acceso educativo mediante variables como zona, conectividad, disponibilidad de dispositivos, acceso a internet, distancia a la institucion educativa, estabilidad electrica, frecuencia de uso de plataformas digitales y apoyo familiar. Con esta informacion, el sistema clasifica el nivel de riesgo de acceso educativo en bajo, medio o alto y genera recomendaciones de mejora.

## Caracteristicas principales

- Carga de datos desde archivo CSV.
- Registro manual de nuevos casos.
- Procesamiento automatico de variables educativas y tecnologicas.
- Clasificacion del riesgo de acceso educativo.
- Visualizacion de indicadores y graficos.
- Generacion de recomendaciones automaticas.
- Descarga de reporte en formato CSV.
- Funcionamiento en ambiente simulado/controlado como prototipo TRL5.

## Tecnologias usadas

- Python
- Streamlit
- Pandas
- NumPy
- CSV como almacenamiento inicial
- GitHub para control y publicacion del codigo

## Estructura del proyecto

```text
prototipo-acceso-educativo-el-cocuy/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── datos_acceso_educativo_el_cocuy.csv
└── docs/
    ├── instrucciones_github.md
    ├── guion_video_10_min.md
    └── evidencia_trl5.md
```

## Ejecucion local

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicacion:

```bash
streamlit run app.py
```

3. Abrir en el navegador:

```text
http://localhost:8501
```

## Despliegue sugerido en Streamlit Community Cloud

1. Subir este proyecto a un repositorio de GitHub.
2. Ingresar a Streamlit Community Cloud.
3. Crear una nueva aplicacion seleccionando el repositorio.
4. Configurar el archivo principal como `app.py`.
5. Desplegar la aplicacion y copiar el enlace generado.

## Aclaracion academica

Este prototipo no utiliza datos personales reales. La base incluida es simulada y se usa para validar la logica funcional del sistema en un ambiente controlado. La clasificacion de riesgo se realiza mediante reglas ponderadas de apoyo a la decision, por lo que requiere validacion futura con datos reales antes de una implementacion institucional.
