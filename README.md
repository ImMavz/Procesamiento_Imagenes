# Control 1: Procesamiento Digital de Imágenes (PDI)
**Ponderación:** 50% de la Calificación Final  
**Especialidad:** Visión por Computador e Imágenes Médicas (DICOM/NIfTI)  
**Autor:** Joseph Herrera  

---

## 📌 Resumen del Proyecto

Este repositorio contiene la implementación algorítmica completa, desarrollada **estrictamente desde cero (from scratch)** sin librerías de alto nivel (`cv2`, `skimage`, `scipy.ndimage`), para el análisis, filtrado y detección de bordes sobre tres modalidades de adquisición física esencialmente distintas:

1. **Imagen Plana Convencional (2D):** Fotografía óptica (8 bits por canal RGB, rango $[0, 255]$), capturada bajo radiación electromagnética visible.
2. **Resonancia Magnética (RM / MRI - Corte Axial):** Matriz cruda de 16 bits nativos (rango $[0, 65535]$ sin unidades), capturada por tiempos de relajación nuclear ($T1/T2$). Estándar de oro para tejidos blandos y sistema límbico (amígdala, hipocampo, tálamo).
3. **Tomografía Computarizada (TAC / CT - Corte Cráneo):** Coeficiente de atenuación de rayos X calibrado en **Unidades Hounsfield (HU)** (valores con signo: aire $\approx -1000\text{ HU}$, agua $= 0\text{ HU}$, hueso $> +1000\text{ HU}$). Estándar para estructuras de alta densidad ósea.

---

## 📁 Estructura del Proyecto

```
control1/
├── .agents/skills/                   # Reglas permanentes y rúbrica de sustentación
│   ├── control-1-defense-prep.md     # Estándares de sustentación, trade-offs e hiperparámetros
│   ├── medical-imaging-domain.md     # Fisiología radiométrica, 16 bits, HU y anonimización
│   ├── noise-and-filters-math.md     # Matemáticas de ruido, normalización y derivadas
│   └── pdi-core-rules.md             # Reglas estrictas: from scratch, inmutabilidad, sin cv2
├── imagenes/                         # Datos de entrada crudos (Raw Data)
│   ├── ImagenPlana/luna.jpg          # Fotografía real 2D (967x725 px)
│   ├── RMI/1.3.12.2...               # Archivo DICOM de Resonancia Magnética (564x512 px)
│   └── tomografia/1.3.6.1...dcm      # Archivo DICOM de Tomografía Computarizada (512x512 px)
├── notebooks/                        # Entorno de sustentación en vivo
│   ├── Control_1_PDI.ipynb           # Notebook maestro con los 7 módulos y gráficas
│   └── prueba1.ipynb                 # Réplica sincronizada para ejecución directa en VS Code
├── src/                              # Módulos Python modulares from scratch
│   ├── modulo1_io_headers.py         # Carga, metadatos, calibración HU y anonimización
│   ├── modulo2_color_spaces.py       # Gris biológico, YUV matricial y HSV a trozos
│   ├── modulo3_histogram_cdf.py      # Histograma, CDF percentiles, Global y CLAHE manual
│   ├── modulo4_noise_modeling.py     # ROIs homogéneas, momentos y test Kolmogorov-Smirnov
│   ├── modulo5_convolution_filters.py# Motor 4 ciclos for, Gaussiano normalizado y Mediana
│   ├── modulo6_edge_detection.py     # Sobel (magnitud/dirección) y Laplaciano (Taylor)
│   └── modulo7_variance_operator.py  # Operador estadístico no lineal local R = 1 - 1/(1+var)
└── generate_notebook.py              # Generador automatizado del pipeline reproducible
```

---

## 🚀 Ejecución y Reproducibilidad

1. **Activar el entorno virtual:**
   ```bash
   source .venv/bin/activate
   ```
2. **Abrir en VS Code o Jupyter:**
   - Abrir el archivo `control1/notebooks/Control_1_PDI.ipynb` o `control1/notebooks/prueba1.ipynb`.
   - Seleccionar el kernel de Python (`.venv` o `Python (PDI Control 1)`).
   - Ejecutar celda por celda o presionar **Run All**. Todas las celdas se ejecutan sin errores en $< 15$ segundos.

---

## 🏆 Cumplimiento de las Reglas de Oro

1. **Cero Dependencias de Caja Negra:** Ninguna función importa ni llama a `cv2`, `skimage` o `scipy.ndimage`. Todo el pipeline se basa en `numpy` y bucles `for` nativos.
2. **Inmutabilidad Absoluta:** Toda función clona la matriz de entrada con `.copy()`.
3. **Respeto al Rango Dinámico Crudo:** No existe compresión previa a 8 bits en RM ni TAC. Los cálculos operan sobre `uint16` y `float64` en escala Hounsfield real.
4. **Normalización Gaussiana Estricta:** Todo kernel gaussiano se normaliza dividiendo entre `np.sum(kernel)`, garantizando suma $1.0$.
5. **Anonimización Clínica:** Las etiquetas PHI se limpian con cadena vacía `""` según norma DICOM PS 3.15 y estándares éticos HIPAA.

