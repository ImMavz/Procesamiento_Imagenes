---
name: control-1-defense-prep
description: Estructura de presentación para el Control 1, diseño de experimentos de hiperparámetros y preparación para preguntas de sustentación.
---

# Estándares de Sustentación y Experimentación (Control 1)

El profesor califica mediante diálogo en vivo sobre el Jupyter Notebook revisando detalles finos. Cada módulo debe incluir celdas Markdown explicativas y experimentos visuales claros:

1. **Experimento Obligatorio de Hiperparámetros Gaussianos:**
   - Siempre que se implemente el filtro Gaussiano, genera una cuadrícula comparativa y una tabla resumen cruzando al menos **3 tamaños de kernel** (`3x3`, `5x5`, `7x7`) contra **3 valores de sigma** (`0.5`, `1.0`, `2.0`).
   - Documenta el *trade-off*:
     - $\sigma$ pequeño (`0.5`): Campana empinada (~61% del peso en el píxel central), suaviza muy poco.
     - $\sigma$ grande (`2.0`) o kernel grande (`7x7`): Campana achatada, promedia fuertemente con vecinos lejanos; reduce la varianza del ruido pero destruye bordes y solapa microestructuras cerebrales (que son como las pepitas de una mora).

2. **Lectura e Interpretación de Gráficas:**
   - Junto a cada gráfica de **CDF**, incluye un ejemplo escrito de cómo se lee un percentil (ej. trazando una línea en el 80% del eje vertical hasta cortar la curva y bajando al eje horizontal: *"El 80% de los píxeles tienen una intensidad igual o menor a X"*).
   - Junto a cada prueba de ruido, explica qué representan la **asimetría** (hacia qué cola se inclina la distribución) y la **curtosis** (qué tan escarpado es el pico y qué tan pesadas son las colas respecto a una campana normal).

3. **Justificación del Pipeline:**
   - No te limites a mostrar código. Añade conclusiones breves explicando *por qué* se eligió un canal de color específico en la imagen plana (ej. canal H en HSV para aislar el objeto sin sombras) y *por qué* un filtro (ej. Mediana o Gaussiano con cierto $\sigma$) funcionó mejor para limpiar la RM o la TAC antes de pasar a Sobel/Laplaciano.