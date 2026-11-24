# Prototipo Kaufmann · Slotting inteligente con IA

Prototipo académico (Proyecto Integrado, Técnico en Logística INACAP) de la alternativa 1A:
clasificación ABC con K-means y propuesta de reubicación de repuestos para la bodega 1151.

Los Excel de Kaufmann **no se suben a este repositorio**: se cargan en la app cada vez y no se guardan.

## Archivos
- `app.py` — la página (Streamlit)
- `motor.py` — el modelo (K-means, layout, simulación con órdenes reales)
- `requirements.txt` — librerías
- `.streamlit/config.toml` — colores y tema

## Correr en tu computador (opcional)
    pip install -r requirements.txt
    streamlit run app.py
