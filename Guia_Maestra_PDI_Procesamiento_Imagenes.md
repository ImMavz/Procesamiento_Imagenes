# Guía Maestra de Cátedra: Procesamiento Digital de Imágenes y Visión Artificial

**Profesor Titular:** Cátedra de Procesamiento Digital de Imágenes (PDI)  
**Nivel Académico:** 9.° Semestre — Ingeniería de Sistemas, Universidad del Valle  
**Enfoque Pedagógico:** Rigor Físico-Matemático, Modelamiento Estocástico, Deducción Numérica Discreta e Implementación Algorítmica en Python/OpenCV/NumPy

---

## Prólogo Metodológico del Docente

Estimado futuro colega ingeniero:

El procesamiento digital de imágenes (PDI) no consiste en ejecutar filtros "caja negra" llamando funciones arbitrarias de una biblioteca externa. Para un ingeniero de sistemas en su ciclo profesional, una imagen digital no es una fotografía: es una matriz bidimensional (o tensor multidimensional) de intensidades energéticas discretizadas, fruto de un muestreo espacial y una cuantización radiométrica gobernados por leyes físicas y fisiológicas.

En este compendio se consolida y desglosa minuciosamente el contenido íntegro impartido a lo largo del curso (sesiones de septiembre y octubre de 2026), articulado en **7 Clases Magistrales**. Cada clase contiene:
1. **Título y Objetivo de la Clase**: Fundamentación contextual y pertinencia en la ingeniería.
2. **Explicación Teórica Profunda**: El *por qué* y el *cómo* físico, biofísico y arquitectural.
3. **Algoritmos y Matemáticas**: Deducciones analíticas paso a paso, aproximaciones por series de Taylor, funciones de densidad de probabilidad, operadores matriciales y kernels discretos.
4. **Casos de Uso y Aplicación en Código**: Implementaciones ejecutables con NumPy y OpenCV que traducen la lógica matemática directamente en algoritmos de producción.

---

## Índice General

1. [Clase 1: Fundamentos de Representación Matricial, Formatos Clínicos (DICOM/NIfTI), Cuantización y Protocolos de Anonimización Ético-Legal](#clase-1-fundamentos-de-representación-matricial-formatos-clínicos-dicomnifti-cuantización-y-protocolos-de-anonimización-ético-legal)
2. [Clase 2: Biología de la Visión Humana, Espacios de Color (RGB, YUV, HSV) y Transformaciones de Contraste con Histogramas](#clase-2-biología-de-la-visión-humana-espacios-de-color-rgb-yuv-hsv-y-transformaciones-de-contraste-con-histogramas)
3. [Clase 3: Unidades Hounsfield (HU) en Tomografía, Ventaneo Clínico y Función de Distribución Acumulada (CDF)](#clase-3-unidades-hounsfield-hu-en-tomografía-ventaneo-clínico-y-función-de-distribución-acumulada-cdf)
4. [Clase 4: Modelamiento Estocástico del Ruido en Imágenes, Momentos Estadísticos y Test de Kolmogorov-Smirnov](#clase-4-modelamiento-estocástico-del-ruido-en-imágenes-momentos-estadísticos-y-test-de-kolmogorov-smirnov)
5. [Clase 5: Motor Maestro de Convolución Bidimensional y Filtros Espaciales de Paso Bajo (Suavizado Lineal y No Lineal)](#clase-5-motor-maestro-de-convolución-bidimensional-y-filtros-espaciales-de-paso-bajo-suavizado-lineal-y-no-lineal)
6. [Clase 6: Filtros Espaciales de Paso Alto, Deducción por Series de Taylor, Gradiente Diferencial (Sobel) y Laplaciano](#clase-6-filtros-espaciales-de-paso-alto-deducción-por-series-de-taylor-gradiente-diferencial-sobel-y-laplaciano)
7. [Clase 7: Detección Avanzada de Bordes: Algoritmo Óptimo de Canny (Supresión No Máxima e Histéresis) y Operador Estadístico Local de Varianza](#clase-7-detección-avanzada-de-bordes-algoritmo-óptimo-de-canny-supresión-no-máxima-e-histéresis-y-operador-estadístico-local-de-varianza)

---

## Clase 1: Fundamentos de Representación Matricial, Formatos Clínicos (DICOM/NIfTI), Cuantización y Protocolos de Anonimización Ético-Legal

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Estructura de matrices digitales, cuantización de bits, encabezados en estándares médicos (DICOM, NIfTI) y marco ético-legal de disociación de identidad.
* **Objetivo Académico:** Comprender la naturaleza computacional de una imagen como una función bidimensional discretizada $f(x, y)$, dominar las diferencias entre imágenes ópticas estándar (8 bits) y datos biomédicos de alta resolución dinámica (12, 14 y 16 bits), y aplicar rigurosamente los estándares de seguridad de datos de pacientes (Ley Estatutaria 1581 de 2012 / HIPAA).

### 2. Explicación Teórica
#### 2.1. La Imagen como Función Discretizada
Físicamente, una imagen continua $f(x, y)$ representa la irradiación o reflectancia espectral recibida en un plano focal sensor. Para ser procesada por una arquitectura Von Neumann o Harvard, debe someterse a:
1. **Muestreo espacial (Sampling):** Discretización del dominio continuo $(x, y) \in \mathbb{R}^2$ en una cuadrícula rectangular de $M$ filas y $N$ columnas. La distancia física entre centros de muestreo se denomina *Pixel Spacing* $(\Delta x, \Delta y)$ en milímetros por píxel.
2. **Cuantización de amplitud (Quantization):** Discretización del rango de intensidades continuas en $L = 2^b$ niveles enteros, donde $b$ es la profundidad de bits por canal.
   * **Imágenes estándar (8 bits):** $b = 8 \implies L = 256$ niveles $\in [0, 255]$. Adecuado para monitores convencionales y la sensibilidad del ojo humano, pero insuficiente para diferenciar variaciones sutiles de densidad radiológica.
   * **Imágenes de Resonancia Magnética (RM) y Tomografía Axial Computarizada (TAC) (12 a 16 bits):** $b = 16 \implies L = 65,536$ niveles $\in [0, 65535]$ (o en enteros con signo $[-32768, 32767]$). Permite registrar rangos físicos gigantescos sin saturación.

#### 2.2. Estructuras Clínicas: DICOM vs. NIfTI
A diferencia de los contenedores comerciales (PNG, JPEG), los formatos biomédicos almacenan conjuntamente la matriz de vóxeles y los metadatos clínicos:
* **DICOM (*Digital Imaging and Communications in Medicine*):** Estándar de interoperabilidad hospitalaria (sistemas PACS). Cada archivo contiene un mapa de etiquetas *(Group, Element)* que codifica la identidad del paciente, calibraciones radiométricas (`RescaleSlope`, `RescaleIntercept`), dimensiones espaciales (`PixelSpacing`, `SliceThickness`) y parámetros de adquisición (tiempo de eco $TE$, tiempo de repetición $TR$).
* **NIfTI (*Neuroimaging Informatics Technology Initiative*):** Formato volumétrico 3D/4D optimizado para neuroimagen analítica (fMRI, DTI), que preserva las matrices afines $4 \times 4$ de orientación en el espacio neurológico estándar (ejes Ras/LAS).

#### 2.3. Anonimización y Responsabilidad Profesional
El procesamiento de datos de salud en Colombia está sujeto a la **Ley 1581 de 2012** (Régimen de Protección de Datos Personales y Datos Sensibles) y normativas internacionales (HIPAA Safe Harbor). Como ingenieros de sistemas:
* Jamás debe manipularse información médica como si fuera una base de datos comercial.
* Los identificadores directos obligatorios de disociación son: `PatientName` (0010,0010), `PatientID` (0010,0020), `PatientBirthDate` (0010,0030), `AccessionNumber` (0008,0050) y `InstitutionName` (0008,0080).

### 3. Algoritmos y Matemáticas
#### 3.1. Relación de Cuantización y Error de Discretización
Para una señal continua acotada en $[f_{\min}, f_{\max}]$, el tamaño del cuanto $\Delta q$ al usar $b$ bits es:
$$\Delta q = \frac{f_{\max} - f_{\min}}{2^b - 1}$$
La potencia del ruido de cuantización (asumiendo distribución uniforme de error de redondeo) es:
$$\sigma_q^2 = \frac{\Delta q^2}{12}$$
A mayor cantidad de bits ($b=16$ frente a $b=8$), el error de cuantización desciende drásticamente, preservando los detalles de baja amplitud indispensables en diagnósticos de tejido blando.

#### 3.2. Transformación Lineal de Almacenamiento a Magnitud Física
En DICOM, el valor almacenado en memoria `SV` (*Stored Value*, entero sin signo) debe transformarse al valor físico real `PV` (*Physical Value*) mediante los tags de reescalado:
$$\text{PV} = m \cdot \text{SV} + c$$
Donde:
* $m = \text{RescaleSlope}$ (etiqueta `(0028, 1053)`)
* $c = \text{RescaleIntercept}$ (etiqueta `(0028, 1052)`)

### 4. Casos de Uso y Aplicación (Python + OpenCV / PyDICOM)
A continuación se presenta el código para inspeccionar un corte DICOM, verificar su resolución radiométrica, extraer el espaciado físico y anonimizar los tags sensibles antes de persistir o procesar la matriz:

```python
import pydicom
import numpy as np
import cv2

def inspeccionar_y_anonimizar_dicom(ruta_entrada: str, ruta_salida: str) -> np.ndarray:
    """
    Lee un archivo DICOM, imprime metadatos dimensionales y físicos,
    aplica protocolo de anonimización ética y devuelve la matriz en float32 reescalada.
    """
    # 1. Cargar archivo DICOM con encabezados
    ds = pydicom.dcmread(ruta_entrada)
    
    # 2. Extracción de metadatos de adquisición
    filas = ds.Rows
    columnas = ds.Columns
    bits_almacenados = ds.BitsStored
    pixel_spacing = getattr(ds, "PixelSpacing", [1.0, 1.0]) # mm/píxel
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
    
    print(f"Dimensiones de la matriz: {filas} x {columnas}")
    print(f"Profundidad de bits declarada: {bits_almacenados} bits")
    print(f"Resolución espacial física (dx, dy): {pixel_spacing} mm/píxel")
    print(f"Parámetros de reescalado: Slope={slope}, Intercept={intercept}")
    
    # 3. Anonimización estricta (Ley 1581 / HIPAA)
    tags_anonimizar = [
        "PatientName", "PatientID", "PatientBirthDate", 
        "PatientSex", "InstitutionName", "ReferringPhysicianName"
    ]
    for tag in tags_anonimizar:
        if tag in ds:
            setattr(ds, tag, "ANONIMIZADO")
            
    # Guardar archivo anonimizado
    ds.save_as(ruta_salida)
    print(f"Archivo anonimizado guardado en: {ruta_salida}")
    
    # 4. Extracción y reescalado de la matriz a magnitud física
    matriz_raw = ds.pixel_array.astype(np.float32)
    matriz_fisica = (matriz_raw * slope) + intercept
    return matriz_fisica
```

---

## Clase 2: Biología de la Visión Humana, Espacios de Color (RGB, YUV, HSV) y Transformaciones de Contraste con Histogramas

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Fundamento biofísico del ojo humano, teoría tricromática, espacios de color desacoplados (YUV, HSV) y modelado estadístico por histograma.
* **Objetivo Académico:** Explicar cómo la anatomía de los fotorreceptores retinales determina las fórmulas empíricas de luminancia en ingeniería, formular las matrices de conversión entre espacios de color e implementar el cálculo manual de histogramas continuos y discretos.

### 2. Explicación Teórica
#### 2.1. Fisiología Retinal: Conos, Bastoncillos y la Fóvea
El sistema visual humano (HVS) realiza un filtrado biológico selectivo en la retina:
* **Bastoncillos (~120 millones):** Células de visión escotópica (baja iluminación nocturna). No discriminan color; saturan a niveles medios de fotones.
* **Conos (~6 a 7 millones):** Concentrados en la fóvea central. Son los responsables de la visión fotópica (alta resolución diurna y percepción cromática). Existen tres subtipos según su pico de absorción de longitud de onda:
  * **Conos S (Short / Azul):** Pico aproximado a $420\text{ nm}$. Representan apenas el ~2% al 5% de la fóvea.
  * **Conos M (Medium / Verde):** Pico en $530\text{ nm}$. Altísima densidad.
  * **Conos L (Long / Rojo):** Pico en $560\text{ nm}$. Altísima densidad.

Debido a que la máxima absorción de la combinación de conos L y M se sitúa en los $\approx 555\text{ nm}$ (espectro verde-amarillo), el ser humano percibe con mucha mayor nitidez los cambios de brillo en la banda verde que en la banda azul. Por esta razón biológica estricta, la conversión a escala de grises jamás puede ser un simple promedio aritmético $\frac{R+G+B}{3}$.

#### 2.2. Espacios de Color y Desacoplamiento de la Información
1. **RGB (Red, Green, Blue):** Espacio aditivo orientado al hardware (pantallas CRT, OLED, sensores Bayer). Presenta una limitación crítica para la visión computacional: los tres canales están fuertemente correlacionados con la iluminación general de la escena.
2. **YUV / YCbCr:** Desarrollado para la transmisión analógica y digital de televisión compatible (NTSC/PAL). Separa la luminancia pura ($Y$) de la crominancia o color ($U$ y $V$). Esto permite la compresión perceptual por submuestreo cromático (Chroma Subsampling 4:2:0).
3. **HSV (Hue, Saturation, Value):** Geometría cónica/cilíndrica que desacopla la longitud de onda dominante (Tono $H \in [0^\circ, 360^\circ]$), la pureza o pureza espectral (Saturación $S \in [0, 1]$) y la intensidad del brillo (Valor $V \in [0, 1]$). Es el espacio predilecto para la segmentación de objetos invariable a sombras.

### 3. Algoritmos y Matemáticas
#### 3.1. Fórmula Estándar de Luminancia Fotópica (ITU-R BT.601)
$$Y = 0.299 \cdot R + 0.5876 \cdot G + 0.1140 \cdot B$$
Nótese cómo el canal Verde ($G$) posee el $58.76\%$ del peso perceptual, el Rojo ($R$) el $29.9\%$, y el Azul ($B$) únicamente el $11.4\%$.

#### 3.2. Transformación Matricial Exacta a Espacio YUV
$$\begin{bmatrix} Y \\ U \\ V \end{bmatrix} = \begin{bmatrix} 0.299 & 0.5876 & 0.114 \\ -0.14713 & -0.28886 & 0.436 \\ 0.615 & -0.51499 & -0.10001 \end{bmatrix} \begin{bmatrix} R \\ G \\ B \end{bmatrix}$$

#### 3.3. Fundamento Matemático del Histograma
Para una imagen digital monodimensional $I$ de tamaño $M \times N$ con $L$ niveles posibles:
$$h(r_k) = n_k, \quad k = 0, 1, \dots, L-1$$
Donde $n_k$ es el número de píxeles con intensidad $r_k$. El histograma normalizado define la Función de Masa de Probabilidad (PMF) discreta:
$$p(r_k) = \frac{n_k}{M \cdot N}, \quad \sum_{k=0}^{L-1} p(r_k) = 1$$

### 4. Casos de Uso y Aplicación (Python + OpenCV / NumPy)
Implementación algorítmica desde cero de la conversión a gris biológico y del cálculo manual del histograma sin usar `cv2.calcHist`:

```python
import numpy as np
import cv2
import matplotlib.pyplot as plt

def conversion_espacios_y_histograma_scratch(img_bgr: np.ndarray):
    """
    Convierte BGR a RGB, calcula Gris Biológico de acuerdo a ITU-R BT.601
    y computa el histograma de frecuencias discretas desde cero.
    """
    # 1. OpenCV lee en BGR por defecto -> convertir a RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float64)
    R = img_rgb[:, :, 0]
    G = img_rgb[:, :, 1]
    B = img_rgb[:, :, 2]
    
    # 2. Gris Biológico ponderado
    gris_biologico = np.floor(0.299 * R + 0.5876 * G + 0.1140 * B).astype(np.uint8)
    
    # 3. Espacio HSV para segmentación cromática desacoplada
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    canal_H = img_hsv[:, :, 0] # Matiz [0, 179] en OpenCV
    
    # 4. Cálculo algorítmico del Histograma (from scratch)
    H, W = gris_biologico.shape
    histograma = np.zeros(256, dtype=np.int64)
    
    # Recorrido directo por cuantización
    for y in range(H):
        for x in range(W):
            valor_pixel = gris_biologico[y, x]
            histograma[valor_pixel] += 1
            
    pmf = histograma / (H * W)
    
    return gris_biologico, canal_H, histograma, pmf
```

---

## Clase 3: Unidades Hounsfield (HU) en Tomografía, Ventaneo Clínico y Función de Distribución Acumulada (CDF)

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Escala radiométrica de Hounsfield en tomografía axial computarizada (TAC), mapeo de ventanas de atenuación tisular y ecualización de histograma mediante la función de distribución acumulada (CDF).
* **Objetivo Académico:** Comprender la física de atenuación de rayos X ($HU$), resolver la contradicción biológica entre los 12-16 bits de los equipos médicos y los 8 bits de los monitores mediante *Windowing*, y deducir analíticamente el operador no lineal de ecualización global por CDF.

### 2. Explicación Teórica
#### 2.1. Escala y Unidades Hounsfield (HU)
Sir Godfrey Hounsfield diseñó una escala cuantitativa lineal que mapea los coeficientes de atenuación lineal de los rayos X ($\mu$) del tejido biológico analizado respecto al agua destilada y al aire atmosférico:
* **Agua pura:** Define el origen de la escala: $0\text{ HU}$.
* **Aire:** Coeficiente de atenuación nulo relativo a los tejidos: $-1000\text{ HU}$.
* **Grasa corporal:** Menor densidad que el agua: $\approx -120\text{ a } -90\text{ HU}$.
* **Tejido blando / Músculo / Cerebro:** $\approx +20\text{ a } +60\text{ HU}$.
* **Hueso trabecular y cortical:** Alta densidad de calcio: $+400\text{ a } +3000\text{ HU}$.
* **Implantes metálicos:** Metales pesados que absorben el haz: $> +3000\text{ HU}$.

#### 2.2. La Técnica del Ventaneo Clínico (Window Level & Window Width)
Una tomografía almacena fácilmente rangos de $[-1000, 3000]\text{ HU}$ (más de $4000$ niveles de intensidad discretos). No obstante:
1. El ojo humano únicamente es capaz de discriminar entre 30 y 50 niveles de gris simultáneamente.
2. Los monitores estándar despliegan únicamente 8 bits ($[0, 255]$).

Si comprimimos todo el rango de $4000\text{ HU}$ linealmente en $256$ niveles de gris, la sutil diferencia entre la materia gris cerebral ($+40\text{ HU}$) y la materia blanca ($+30\text{ HU}$) se reduce a una fracción de nivel de gris ($\Delta \approx 0.6$), resultando en una imagen visualmente homogénea e inservible para el diagnóstico médico.

La solución médica es el **Ventaneo**, definido por:
* **Nivel de Ventana ($WL$ o *Window Center*):** El valor de HU central de la patología o tejido de interés.
* **Ancho de Ventana ($WW$ o *Window Width*):** El rango dinámico que se expandirá a toda la escala visual $[0, 255]$.

| Estructura Tisular | Nivel de Ventana ($WL$) | Ancho de Ventana ($WW$) | Rango Visualizado $[HU_{\min}, HU_{\max}]$ |
| :--- | :---: | :---: | :---: |
| **Cerebro (Tejido Blando)** | $+40\text{ HU}$ | $80\text{ HU}$ | $[0, +80]\text{ HU}$ |
| **Óseo (Fracturas/Cráneo)** | $+500\text{ HU}$ | $2000\text{ HU}$ | $[-500, +1500]\text{ HU}$ |
| **Pulmón (Parénquima)** | $-600\text{ HU}$ | $1500\text{ HU}$ | $[-1350, +150]\text{ HU}$ |

#### 2.3. Ecualización por Función de Distribución Acumulada (CDF)
La ecualización es una transformación puntual monotónica $s = T(r)$ que busca redistribuir las intensidades de modo que el histograma de salida exhiba una densidad de probabilidad uniforme. Dado que no se puede "inventar" información que no fue muestreada, la ecualización en dominios discretos estira las regiones con alta densidad de píxeles y comprime las regiones desiertas, maximizando la entropía visual de la imagen.

### 3. Algoritmos y Matemáticas
#### 3.1. Ecuación de Calibración Hounsfield
$$\text{HU} = 1000 \times \frac{\mu_{\text{tejido}} - \mu_{\text{agua}}}{\mu_{\text{agua}} - \mu_{\text{aire}}}$$

#### 3.2. Ecuación de Transferencia de Ventaneo
Dado un vóxel con valor en unidades Hounsfield $x$, su mapeo al rango de visualización $[0, 255]$ es una función lineal por partes con saturación:
$$V(x) = \begin{cases} 
0, & x \le WL - \frac{WW}{2} \\ 
255, & x \ge WL + \frac{WW}{2} \\ 
\left\lfloor 255 \cdot \frac{x - \left(WL - \frac{WW}{2}\right)}{WW} \right\rfloor, & WL - \frac{WW}{2} < x < WL + \frac{WW}{2} 
\end{cases}$$

#### 3.3. Deducción Analítica de la Ecualización por CDF
Consideremos la función de probabilidad continua $p_r(r)$. Buscamos una transformación estrictamente creciente $s = T(r)$ tal que la probabilidad del nivel de salida sea plana: $p_s(s) = \frac{1}{L-1}$.
Por el teorema de conservación de la probabilidad:
$$p_s(s) \, ds = p_r(r) \, dr \implies \frac{1}{L-1} \, ds = p_r(r) \, dr$$
Integrando a ambos lados entre $0$ y $r$:
$$\int_0^s \frac{1}{L-1} \, dw = \int_0^r p_r(w) \, dw \implies \frac{s}{L-1} = F_r(r)$$
$$s = T(r) = (L - 1) \cdot F_r(r) = (L - 1) \int_0^r p_r(w) \, dw$$
En el dominio discreto digital:
$$s_k = \left\lfloor (L - 1) \sum_{j=0}^k \frac{n_j}{M \cdot N} \right\rfloor$$
Para evitar que el fondo negro masivo desplace el rango dinámico útil, se computa la CDF normalizada con su valor mínimo no nulo ($CDF_{\min}$):
$$s_k = \left\lfloor \frac{\text{CDF}(k) - \text{CDF}_{\min}}{(M \cdot N) - \text{CDF}_{\min}} \cdot (L - 1) \right\rfloor$$

### 4. Casos de Uso y Aplicación (Python + OpenCV / NumPy)
Código que implementa la función de ventaneo clínico para tomografía y el algoritmo de ecualización exacta por CDF sin funciones prefabricadas:

```python
import numpy as np
import cv2

def aplicar_ventaneo_clinico(matriz_hu: np.ndarray, wl: float, ww: float) -> np.ndarray:
    """
    Mapea una matriz física en Unidades Hounsfield (HU) a uint8 [0, 255]
    utilizando una ventana centrada en WL de ancho WW.
    """
    hu_min = wl - (ww / 2.0)
    hu_max = wl + (ww / 2.0)
    
    # Truncamiento (clipping) en los extremos de la ventana
    imagen_clipeada = np.clip(matriz_hu, hu_min, hu_max)
    
    # Reescalado lineal normalizado a [0, 255]
    imagen_uint8 = ((imagen_clipeada - hu_min) / ww * 255.0).astype(np.uint8)
    return imagen_uint8


def ecualizacion_cdf_scratch(imagen_gris: np.ndarray) -> np.ndarray:
    """
    Implementación algorítmica de la ecualización de histograma
    mediante el cálculo analítico de la CDF discreta.
    """
    H, W = imagen_gris.shape
    total_pixeles = H * W
    
    # 1. Histograma
    hist = np.zeros(256, dtype=np.int64)
    for y in range(H):
        for x in range(W):
            hist[imagen_gris[y, x]] += 1
            
    # 2. Función de Distribución Acumulada (CDF)
    cdf = np.zeros(256, dtype=np.float64)
    acumulado = 0
    for i in range(256):
        acumulado += hist[i]
        cdf[i] = acumulado
        
    # Encontrar CDF mínima no nula para estirar contraste correctamente
    cdf_min = cdf[cdf > 0].min()
    
    # 3. Mapeo Look-Up Table (LUT)
    lut = np.zeros(256, dtype=np.uint8)
    for i in range(256):
        if cdf[i] < cdf_min:
            lut[i] = 0
        else:
            lut[i] = np.clip(np.round(((cdf[i] - cdf_min) / (total_pixeles - cdf_min)) * 255.0), 0, 255)
            
    # 4. Asignación vectorizada en la imagen de salida
    imagen_ecualizada = lut[imagen_gris]
    return imagen_ecualizada
```

---

## Clase 4: Modelamiento Estocástico del Ruido en Imágenes, Momentos Estadísticos y Test de Kolmogorov-Smirnov

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Caracterización estocástica de degradaciones de señal, extracción de regiones homogéneas (ROI), formulación de los 4 momentos estadísticos y prueba de bondad de ajuste de Kolmogorov-Smirnov (KS).
* **Objetivo Académico:** Abandonar el paradigma empírico de adivinar el ruido; formular el ruido como una variable aleatoria espacial continua, extraer empíricamente la muestra en zonas isótropas y contrastar rigurosamente la hipótesis nula ($H_0$) de modelamiento frente a distribuciones Gaussianas, de Rayleigh y de Rician.

### 2. Explicación Teórica
#### 2.1. Naturaleza Físico-Estocástica del Ruido en Distintas Modalidades
El ruido no es un error informático aleatorio genérico; es la manifestación macroscópica de procesos físicos cuánticos, térmicos y electromagnéticos:
1. **Fotografía Óptica y Sensores CMOS/CCD (Ruido Gaussiano / Poisson):** Causado por la agitación térmica de los electrones en los amplificadores de lectura (Johnson-Nyquist) y la naturaleza discreta de los fotones al impactar los fotodiodos (Shot Noise). Es típicamente aditivo e independiente de la señal.
2. **Resonancia Magnética (Ruido Rician y Rayleigh):** En RM, la señal física se adquiere en el *K-Space* (dominio frecuencial) con receptores en cuadratura (canales en fase $I$ y cuadratura $Q$). Cada canal posee ruido Gaussiano incorrelacionado de media cero. La imagen final se forma tomando la magnitud euclidiana:
   $$M = \sqrt{I^2 + Q^2}$$
   * En el fondo (aire, donde no hay señal del paciente, $I \approx 0, Q \approx 0$), la transformación no lineal convierte el ruido Gaussiano en una distribución de **Rayleigh**.
   * Dentro del parénquima cerebral (donde existe señal de radiofrecuencia positiva), la variable aleatoria sigue una distribución de **Rician**.

#### 2.2. Protocolo de Extracción de la ROI Homogénea
Para modelar el ruido no se analiza toda la escena (los bordes y texturas actúan como falsos picos de alta varianza). Se debe aislar una Región de Interés (ROI) donde la intensidad subyacente deba ser conceptualmente constante:
* En imágenes de RM y TAC: El cuadrante exterior de aire libre (típicamente las esquinas $[0:50, 0:50]$).
* En fotografías planas: Una superficie lisa y uniforme sin sombras ni texturas proyectadas.

### 3. Algoritmos y Matemáticas
#### 3.1. Formulación de los 4 Momentos Estadísticos Centrales
Dada una muestra unidimensional $X = \{x_1, x_2, \dots, x_N\}$ proveniente de la ROI:
1. **Media ($\mu$ - Primer Momento):** Tendencia central del nivel de polarización o corriente oscura.
   $$\mu = \frac{1}{N} \sum_{i=1}^N x_i$$
2. **Varianza ($\sigma^2$ - Segundo Momento Central):** Dispersión de la energía del ruido.
   $$\sigma^2 = \frac{1}{N - 1} \sum_{i=1}^N (x_i - \mu)^2$$
3. **Asimetría / Skewness ($S$ - Tercer Momento Estandarizado):** Indica el sesgo de la cola de la distribución.
   $$S = \frac{\frac{1}{N}\sum_{i=1}^N (x_i - \mu)^3}{\sigma^3}$$
   * $S = 0 \implies$ Perfectamente simétrica (Gaussiana pura).
   * $S > 0 \implies$ Sesgada a la derecha con cola larga positiva (típica de Rayleigh y Rician).
4. **Curtosis / Kurtosis ($K$ - Cuarto Momento Estandarizado):** Medida de las colas y el escarpamiento del pico central comparado con la normal.
   $$K = \frac{\frac{1}{N}\sum_{i=1}^N (x_i - \mu)^4}{\sigma^4}$$
   * En una distribución Normal teórica, $K = 3$. La Curtosis en Exceso se define como $K_{\text{excess}} = K - 3$.

#### 3.2. Prueba de Bondad de Ajuste de Kolmogorov-Smirnov (Test KS)
El test KS determina si los datos de la ROI provienen de una distribución de probabilidad continua teórica $F_0(x)$ especificada.
* **Hipótesis Nula ($H_0$):** Los datos empíricos de la ROI siguen la distribución teórica evaluada.
* **Estadístico $D$ de Kolmogorov-Smirnov:** Es la distancia vertical suprema (máxima discrepancia absoluta) entre la función de distribución empírica $F_N(x)$ y la función acumulada teórica estimada $F_0(x)$:
  $$D = \sup_x |F_N(x) - F_0(x)|$$
  Donde:
  $$F_N(x) = \frac{1}{N} \sum_{i=1}^N \mathbf{1}_{x_i \le x}$$
* **Criterio de Decisión por $p$-valor:** Se fija un nivel de significancia $\alpha = 0.05$. Si el $p\text{-valor} > 0.05$, **no se rechaza $H_0$**, validando formalmente el modelo probabilístico del ruido.

### 4. Casos de Uso y Aplicación (Python + SciPy / NumPy)
Algoritmo completo que recorta una ROI homogénea, calcula sus cuatro momentos analíticos y contrasta estadísticamente la hipótesis de normalidad con Kolmogorov-Smirnov:

```python
import numpy as np
from scipy import stats

def modelar_ruido_roi(imagen: np.ndarray, y1: int, y2: int, x1: int, x2: int):
    """
    Extrae una ROI homogénea, calcula los 4 momentos estadísticos
    y ejecuta el test de Kolmogorov-Smirnov para contrastar normalidad.
    """
    # 1. Extracción de la ROI homogénea (esquina libre o fondo plano)
    roi = imagen[y1:y2, x1:x2].astype(np.float64)
    datos = roi.flatten()
    N = len(datos)
    
    # 2. Cálculo manual de momentos
    media = np.mean(datos)
    varianza = np.var(datos, ddof=1)
    desv_est = np.sqrt(varianza)
    
    # Skewness (Sesgo) y Kurtosis (Curtosis)
    diferencias = datos - media
    skewness = np.mean(diferencias**3) / (desv_est**3)
    kurtosis = np.mean(diferencias**4) / (desv_est**4) # Pearson kurtosis (Normal = 3.0)
    
    # 3. Test de Bondad de Ajuste de Kolmogorov-Smirnov contra Normal Teórica
    # F0(x) parametrizada con media y desviación estándar de la muestra
    d_stat, p_valor = stats.kstest(datos, 'norm', args=(media, desv_est))
    
    print("=== MODELAMIENTO ESTOCÁSTICO DEL RUIDO ===")
    print(f"Muestra N: {N} píxeles")
    print(f"Media (mu): {media:.4f}")
    print(f"Varianza (sigma^2): {varianza:.4f}")
    print(f"Asimetría (Skewness): {skewness:.4f} (Normal teórica = 0.0)")
    print(f"Curtosis (Kurtosis): {kurtosis:.4f} (Normal teórica = 3.0)")
    print(f"Estadístico KS (D): {d_stat:.4f}")
    print(f"p-valor: {p_valor:.4e}")
    
    if p_valor > 0.05:
        print("Conclusión: NO se rechaza H0. El ruido modelado es compatible con distribución Gaussiana.")
    else:
        print("Conclusión: Se rechaza H0 con significancia del 5%. El ruido no es Gaussiano puro (posible Rayleigh o Rician).")
        
    return {
        "media": media, "varianza": varianza, "skewness": skewness,
        "kurtosis": kurtosis, "d_stat": d_stat, "p_valor": p_valor
    }
```

---

## Clase 5: Motor Maestro de Convolución Bidimensional y Filtros Espaciales de Paso Bajo (Suavizado Lineal y No Lineal)

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Álgebra de sistemas lineales invariantes en el espacio (LSI), formulación rigurosa de convolución discreta 2D, condición de conservación de energía radiométrica, padding por reflexión y filtrado no lineal de mediana.
* **Objetivo Académico:** Desarrollar el motor maestro de convolución 2D desde cero (mediante bucles de traslación espacial), justificar la inversión espacial del kernel, comparar formalmente los efectos de suavizado de la media ponderada y la campana de Gauss, y demostrar por qué el filtro de mediana preserva bordes ante ruido impulsivo ("sal y pimienta").

### 2. Explicación Teórica
#### 2.1. Convolución Continua vs. Discreta e Inversión del Kernel
En el procesamiento de señales, la convolución matemática entre una imagen $f(x, y)$ y una respuesta al impulso / máscara / kernel $h(x, y)$ requiere invertir los ejes del kernel (rotación de $180^\circ$):
$$(f * h)(x, y) = \sum_{m=-a}^a \sum_{n=-b}^b f(x - m, y - n) \, h(m, n)$$
Si los signos en los índices fuesen positivos ($x+m, y+n$), la operación sería una **correlación cruzada**. Cuando los kernels son simétricos respecto al origen (como el Gaussiano, el promedio o el Laplaciano), la convolución y la correlación resultan matemáticamente idénticas.

#### 2.2. Condiciones de Conservación de Energía y Tratamiento de Bordes
Para que un filtro de paso bajo (suavizado) no altere el nivel de brillo medio ni introduzca sesgos artificiales en la escena, la suma de todos los coeficientes del kernel debe satisfacer la condición de normalización:
$$\sum_{m} \sum_{n} h(m, n) = 1.0$$
* Si la suma fuera $> 1$, la imagen filtrada convergería a saturación blanca.
* Si la suma fuera $< 1$, la imagen perdería luminancia progresivamente hacia negro.

**Manejo de Fronteras:** Al desplazar un kernel de dimensiones $k \times k$ (con radio $p = \lfloor k/2 \rfloor$), los píxeles periféricos quedan sin vecindario completo. Para evitar artefactos espurios:
* *Zero-padding:* Rodea la imagen de ceros. Provoca un borde negro artificial severo que distorsiona las derivadas.
* *Padding por reflexión (Espejo):* Refleja los píxeles interiores hacia el borde exterior: $I(-x) = I(x)$. Preserva la continuidad de las derivadas de primer orden y la varianza local del tejido.

#### 2.3. Suavizado Lineal (Gaussiano vs. Promedio) vs. Suavizado No Lineal (Mediana)
1. **Filtro Promedio (Box Blur):** Asigna el mismo peso $\frac{1}{k^2}$ a todos los vecinos. Su respuesta en frecuencia es una función $\text{sinc}$, lo que genera artefactos de difracción en los bordes y desenfoque severo de detalles finos.
2. **Filtro Gaussiano:** Pondera las intensidades de acuerdo a una función de probabilidad normal 2D isótropa. Los píxeles más cercanos al centro tienen mayor ponderación; decae asintóticamente a cero según el parámetro de escala $\sigma$. Es el filtro lineal óptimo en el sentido de que minimiza conjuntamente la incertidumbre espaciotemporal y espectral (Principio de Incertidumbre de Gabor).
3. **Filtro de Mediana (No Lineal):** Ordena las intensidades del vecindario y toma el elemento central. Elimina por completo valores extremos atípicos (ruido impulsivo o de sal y pimienta) sin promediarlos, lo que permite preservar las discontinuidades bruscas (los bordes no se atenúan).

### 3. Algoritmos y Matemáticas
#### 3.1. Ecuación Continua y Discretización del Kernel Gaussiano 2D
La función de densidad Gaussiana continua bidimensional circularmente simétrica centrada en el origen está gobernada por la desviación estándar $\sigma$:
$$G(x, y) = \frac{1}{2\pi \sigma^2} e^{-\frac{x^2 + y^2}{2\sigma^2}}$$
Para discretizar un kernel de tamaño impar $k \times k$ con coordenadas enteras $x, y \in \left[-\left\lfloor\frac{k}{2}\right\rfloor, \dots, \left\lfloor\frac{k}{2}\right\rfloor\right]$:
1. Se evalúa la matriz sin normalizar: $\widetilde{K}(x, y) = e^{-\frac{x^2 + y^2}{2\sigma^2}}$
2. Se impone analíticamente la conservación de masa:
   $$K(x, y) = \frac{\widetilde{K}(x, y)}{\sum_{u} \sum_{v} \widetilde{K}(u, v)}$$

#### 3.2. Complejidad Algorítmica del Operador de Mediana
Para una ventana de tamaño $k \times k$:
* En cada píxel se extraen $k^2$ valores.
* Ordenamiento por QuickSort o IntroSort toma $\mathcal{O}(k^2 \log(k^2))$.
* Para una imagen de $M \times N$, la complejidad total es $\mathcal{O}(M \cdot N \cdot k^2 \log(k^2))$.

### 4. Casos de Uso y Aplicación (Python + OpenCV / NumPy)
Implementación algorítmica desde cero de la convolución 2D con padding espejo y generación analítica del kernel Gaussiano:

```python
import numpy as np
import cv2

def crear_kernel_gaussiano_2d(ksize: int, sigma: float) -> np.ndarray:
    """
    Genera analíticamente una matriz de convolución Gaussiana normalizada de tamaño ksize x ksize.
    """
    if ksize % 2 == 0:
        raise ValueError("El tamaño del kernel debe ser un número impar.")
        
    radio = ksize // 2
    # Crear rejilla de coordenadas centradas en cero [-radio, radio]
    y, x = np.mgrid[-radio:radio+1, -radio:radio+1]
    
    # Evaluación de la exponencial Gaussiana
    exponente = -(x**2 + y**2) / (2.0 * sigma**2)
    kernel = np.exp(exponente)
    
    # Normalización unitaria (conservación de energía)
    kernel_normalizado = kernel / np.sum(kernel)
    return kernel_normalizado


def convolucion_2d_scratch(imagen: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Motor maestro de convolución discreta 2D implementado explícitamente con bucles
    y padding por reflexión de bordes.
    """
    H, W = imagen.shape
    k_h, k_w = kernel.shape
    pad_h = k_h // 2
    pad_w = k_w // 2
    
    # 1. Padding espejo (Border reflect)
    img_pad = np.pad(imagen, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect').astype(np.float64)
    
    # 2. Rotación de 180 grados del kernel (formalismo matemático estricto)
    kernel_rotado = np.flip(np.flip(kernel, 0), 1)
    
    salida = np.zeros((H, W), dtype=np.float64)
    
    # 3. Doble bucle espacial de convolución
    for y in range(H):
        for x in range(W):
            # Extraer vecindario
            vecindario = img_pad[y:y + k_h, x:x + k_w]
            # Producto punto elemento a elemento y acumulación
            salida[y, x] = np.sum(vecindario * kernel_rotado)
            
    return salida


def filtro_mediana_scratch(imagen: np.ndarray, ksize: int = 3) -> np.ndarray:
    """
    Implementación del filtro no lineal de mediana para mitigar ruido impulsivo.
    """
    H, W = imagen.shape
    radio = ksize // 2
    img_pad = np.pad(imagen, radio, mode='reflect')
    salida = np.zeros((H, W), dtype=imagen.dtype)
    
    for y in range(H):
        for x in range(W):
            vecindario = img_pad[y:y + ksize, x:x + ksize].flatten()
            salida[y, x] = np.median(vecindario)
            
    return salida
```

---

## Clase 6: Filtros Espaciales de Paso Alto, Deducción por Series de Taylor, Gradiente Diferencial (Sobel) y Laplaciano

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Cálculo diferencial aplicado a matrices discretas, deducción analítica de derivadas numéricas mediante series de Taylor, cálculo vectorial de gradiente bidimensional (Sobel) y operador Laplaciano.
* **Objetivo Académico:** Deducir formalmente cómo se transforma el cálculo diferencial continuo en operadores matriciales matriciales discretos, demostrar la regla cardinal de pre-suavizado para contener la amplificación del ruido y sintetizar los conceptos de magnitud y dirección del vector gradiente.

### 2. Explicación Teórica
#### 2.1. El Borde como Discontinuidad Diferencial
Un borde en una imagen representa una transición brusca o escalón en la función de intensidad luminosa. En el dominio continuo:
* Las **primeras derivadas** presentan un valor extremo (pico máximo o mínimo local) en el centro de la transición.
* Las **segundas derivadas** cruzan por cero (*Zero-Crossing*) en el punto de inflexión exacto de la rampa.

#### 2.2. Por qué la Derivación Amplifica el Ruido (Regla de Oro del Pre-suavizado)
En el dominio de Fourier, la derivada espacial continua de una señal $f(x)$ corresponde a multiplicar su espectro por la frecuencia espacial:
$$\mathcal{F}\left\{\frac{d^n f}{dx^n}\right\} = (j 2\pi u)^n F(u)$$
Dado que el ruido estocástico reside predominantemente en las componentes de alta frecuencia ($u \gg 0$), cualquier operación de diferenciación amplifica la energía del ruido de manera directamente proporcional a su frecuencia (e inversamente peligrosa para la segunda derivada $u^2$).

> [!CRITICAL]
> **Regla de Cátedra:** Jamás se aplica un operador diferencial (Sobel, Prewitt, Laplaciano) directamente sobre una imagen cruda con ruido. Se debe ejecutar **siempre** una etapa previa de filtrado de paso bajo (Gaussiano o Mediana).

#### 2.3. Operador de Sobel vs. Laplaciano
1. **Sobel:** Es un operador vectorial de primer orden basado en diferencias centrales combinadas con suavizado Gaussiano transversal (pesos $[1, 2, 1]$). Produce dos mapas: la magnitud de la tasa de cambio y el ángulo polar del vector gradiente.
2. **Laplaciano:** Es un operador escalar de segundo orden invariante a la rotación (isótropo). Mide la curvatura local de la intensidad. Al ser de segundo orden, es extremadamente sensible al ruido si no se estabiliza con un núcleo Gaussiano previo (Filtro Laplaciano del Gaussiano - LoG).

### 3. Algoritmos y Matemáticas
#### 3.1. Deducción Rigurosa de Derivadas Discretas por Series de Taylor
Expandiendo la función $f(x)$ alrededor del punto $x$ con un paso discreto $h = 1$ píxel:
$$f(x + 1) = f(x) + f'(x) + \frac{f''(x)}{2!} + \frac{f'''(x)}{3!} + \mathcal{O}(h^4) \quad \text{(Ecuación 1)}$$
$$f(x - 1) = f(x) - f'(x) + \frac{f''(x)}{2!} - \frac{f'''(x)}{3!} + \mathcal{O}(h^4) \quad \text{(Ecuación 2)}$$

##### Deducción de la Primera Derivada (Diferencia Central):
Restando la Ecuación 2 de la Ecuación 1:
$$f(x + 1) - f(x - 1) = 2 f'(x) + \mathcal{O}(h^3)$$
Despejando $f'(x)$:
$$f'(x) = \frac{f(x + 1) - f(x - 1)}{2} + \mathcal{O}(h^2)$$
Esto genera el kernel de gradiente horizontal básico $[-1, 0, 1]$.

##### Deducción de la Segunda Derivada (Laplaciano Unidimensional):
Sumando la Ecuación 1 y la Ecuación 2:
$$f(x + 1) + f(x - 1) = 2f(x) + f''(x) + \mathcal{O}(h^4)$$
Despejando $f''(x)$:
$$f''(x) = f(x + 1) - 2f(x) + f(x - 1) + \mathcal{O}(h^2)$$
Matricialmente, esto corresponde al kernel 1D: $[1, -2, 1]$.

##### Deducción del Laplaciano Bidimensional $\nabla^2 f$:
$$\nabla^2 f(x, y) = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2}$$
Discretizando ambas componentes con paso $h=1$:
$$\frac{\partial^2 f}{\partial x^2} \approx f(x+1, y) - 2f(x, y) + f(x-1, y)$$
$$\frac{\partial^2 f}{\partial y^2} \approx f(x, y+1) - 2f(x, y) + f(x, y-1)$$
Sumando ambas expresiones:
$$\nabla^2 f(x, y) \approx f(x+1, y) + f(x-1, y) + f(x, y+1) + f(x, y-1) - 4f(x, y)$$
Esto deduce analíticamente el kernel Laplaciano estándar de 4 vecinos:
$$K_{\text{Laplaciano}} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$$
Si se incorporan los términos diagonales cruzados del desarrollo de Taylor 2D, se obtiene la máscara de 8 vecinos:
$$K_{\text{Laplaciano 8}} = \begin{bmatrix} 1 & 1 & 1 \\ 1 & -8 & 1 \\ 1 & 1 & 1 \end{bmatrix}$$

#### 3.2. Kernels de Sobel y Campos Vectoriales del Gradiente
Sobel desacopla la estimación de la derivada ortogonal integrando un filtro suavizador $[1, 2, 1]^T$ para mitigar el ruido:
$$K_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix} = \begin{bmatrix} 1 \\ 2 \\ 1 \end{bmatrix} \begin{bmatrix} -1 & 0 & 1 \end{bmatrix}$$
$$K_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix} = \begin{bmatrix} -1 \\ 0 \\ 1 \end{bmatrix} \begin{bmatrix} 1 & 2 & 1 \end{bmatrix}$$
Para cada píxel se calculan:
1. **Magnitud del Gradiente:**
   $$M(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2} \quad \text{o la aproximación rápida:} \quad |G_x| + |G_y|$$
2. **Dirección u Orientación Angular del Gradiente:**
   $$\theta(x, y) = \arctan2(G_y(x, y), G_x(x, y)) \quad \in [-\pi, \pi] \text{ o } [-180^\circ, 180^\circ]$$

### 4. Casos de Uso y Aplicación (Python + OpenCV / NumPy)
Implementación integral del pre-suavizado, cálculo de gradientes de Sobel, magnitud analítica, ángulo y Laplaciano discreto:

```python
import numpy as np
import cv2

def calcular_sobel_y_laplaciano_scratch(imagen_gris: np.ndarray, sigma_previo: float = 1.0):
    """
    Aplica regla de oro de suavizado previo, ejecuta convolución con kernels
    de Sobel y Laplaciano deducidos por series de Taylor.
    """
    # 1. Regla de oro: Filtrado Gaussiano previo para amortiguar ruido de alta frecuencia
    img_suavizada = cv2.GaussianBlur(imagen_gris.astype(np.float64), (5, 5), sigma_previo)
    
    # 2. Definición formal de kernels
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float64)
                   
    Ky = np.array([[-1, -2, -1],
                   [ 0,  0,  0],
                   [ 1,  2,  1]], dtype=np.float64)
                   
    K_lap = np.array([[ 0,  1,  0],
                      [ 1, -4,  1],
                      [ 0,  1,  0]], dtype=np.float64)
                      
    # 3. Convoluciones espaciales
    Gx = cv2.filter2D(img_suavizada, -1, Kx)
    Gy = cv2.filter2D(img_suavizada, -1, Ky)
    Laplaciano = cv2.filter2D(img_suavizada, -1, K_lap)
    
    # 4. Magnitud y Dirección vectorial continua
    magnitud = np.sqrt(Gx**2 + Gy**2)
    # Dirección en grados [-180, 180]
    direccion_rad = np.arctan2(Gy, Gx)
    direccion_grados = np.rad2deg(direccion_rad)
    
    # 5. Normalización para inspección visual [0, 255]
    magnitud_visual = np.clip((magnitud / magnitud.max()) * 255.0, 0, 255).astype(np.uint8)
    laplaciano_visual = np.clip(np.abs(Laplaciano), 0, 255).astype(np.uint8)
    
    return {
        "Gx": Gx, "Gy": Gy,
        "magnitud": magnitud,
        "magnitud_visual": magnitud_visual,
        "direccion_grados": direccion_grados,
        "laplaciano": laplaciano_visual
    }
```

---

## Clase 7: Detección Avanzada de Bordes: Algoritmo Óptimo de Canny (Supresión No Máxima e Histéresis) y Operador Estadístico Local de Varianza

### 1. Título y Objetivo de la Clase
* **Tema Principal:** Criterios de optimalidad de John Canny, cuantización de sectores angulares, algoritmo de supresión de no máximos (NMS), umbralización con histéresis biumbral y operador alternativo de varianza local no lineal.
* **Objetivo Académico:** Comprender por qué los gradientes simples generan bordes gruesos y ruidosos, formalizar el adelgazamiento morfomático a un espesor unitario de 1 píxel guiado por el ángulo de máxima variación, conectar cadenas de bordes débiles mediante histéresis y presentar el detector no lineal basado en momentos estadísticos locales de varianza.

### 2. Explicación Teórica
#### 2.1. Criterios de Optimalidad de Canny
En 1986, John Canny formuló la detección de bordes como un problema de optimización matemática riguroso sujeto a tres criterios:
1. **Baja tasa de error:** Todos los bordes reales deben ser detectados; no deben generarse bordes espurios por ruido.
2. **Localización precisa:** La distancia euclidiana entre el borde detectado y el centro del borde real debe ser mínima.
3. **Respuesta única:** Una discontinuidad física no debe producir múltiples aristas falsas adyacentes; el borde debe tener **un grosor estricto de 1 píxel**.

#### 2.2. Supresión de No Máximos (Non-Maximum Suppression - NMS)
El mapa de magnitud del gradiente presenta crestas anchas debido al efecto del filtro Gaussiano y la extensión del operador Sobel. NMS es un algoritmo de adelgazamiento morfológico:
* En cada píxel, se consulta la dirección ortogonal al borde dada por el vector gradiente $\theta$.
* El ángulo se discretiza en cuatro sectores canónicos correspondientes a las direcciones cardinales de una cuadrícula de 8 vecinos:
  * Horizontal ($0^\circ$)
  * Diagonal principal ($45^\circ$)
  * Vertical ($90^\circ$)
  * Diagonal secundaria ($135^\circ$)
* Si la magnitud del píxel central es estrictamente mayor que la de sus dos vecinos a lo largo de esa recta direccional, se conserva; de lo contrario, se suprime fijándolo a $0$.

```
Direcciones de discretización angular (8-vecindario):
       90° (Vecinos: Norte, Sur)
        |
135°    |    45° (Vecinos: Diagonales)
   \    |   /
    \   |  /
0°   ------- 0° (Vecinos: Este, Oeste)
    /   |  \
   /    |   \
```

#### 2.3. Umbralización por Histéresis Biumbral
Un umbral global único genera un dilema insoluble: si se ajusta muy alto, se fragmentan los bordes tenues; si se ajusta muy bajo, el ruido inunda la imagen binaria.
Canny resuelve esto con **dos umbrales** ($T_{\text{alto}}$ y $T_{\text{bajo}}$, usualmente con relación $2:1$ o $3:1$):
* Píxeles con $M(x, y) \ge T_{\text{alto}}$ son clasificados inmediatamente como **Bordes Fuertes Seguros**.
* Píxeles con $M(x, y) < T_{\text{bajo}}$ son **descartados irreversiblemente**.
* Píxeles con $T_{\text{bajo}} \le M(x, y) < T_{\text{alto}}$ son **Bordes Débiles Candidatos**: se promueven a bordes definitivos **únicamente** si están conectados espacialmente (conectividad-8) con algún borde fuerte. Esto previene la rotura de contornos anatómicos sin admitir manchas aisladas de ruido.

#### 2.4. Operador Estadístico Local Basado en la Varianza (Edge Detection sin Convolución)
A diferencia de los filtros lineales o matriciales deducidos por Taylor, este operador examina la dispersión estadística de una ventana deslizante $W$ de $n \times n$:
* En regiones planas o tisularmente homogéneas, todos los píxeles tienen valores casi idénticos $\implies \sigma_W^2 \approx 0$.
* En zonas que cruzan un borde estructural, la coexistencia de valores claros y oscuros dispara la varianza $\implies \sigma_W^2 \gg 0$.

Para mapear esta varianza a una respuesta normalizada acotada estrictamente en el intervalo $[0, 1]$, se utiliza la función sigmoidal de respuesta:
$$R(x, y) = 1 - \frac{1}{1 + \sigma_W^2(x, y)}$$
* Si $\sigma_W^2 \to 0 \implies R \to 1 - \frac{1}{1} = 0$ (Negro absoluto, sin borde).
* Si $\sigma_W^2 \to \infty \implies R \to 1 - 0 = 1$ (Blanco máximo, borde detectado).

### 3. Algoritmos y Matemáticas
#### 3.1. Cuantización de los Sectores Angulares en NMS
El ángulo $\theta \in [-180^\circ, 180^\circ]$ se reduce al semiplano $[0^\circ, 180^\circ]$ sumando $180^\circ$ si $\theta < 0$. El mapeo a los 4 sectores de decisión es:
$$\text{Sector}(\theta) = \begin{cases} 
0^\circ (\text{Horizontal}), & \theta \in [0^\circ, 22.5^\circ) \cup [157.5^\circ, 180^\circ] \implies \text{Vecinos: } (x, y-1) \text{ y } (x, y+1) \\ 
45^\circ (\text{Diagonal Neg.}), & \theta \in [22.5^\circ, 67.5^\circ) \implies \text{Vecinos: } (x-1, y+1) \text{ y } (x+1, y-1) \\ 
90^\circ (\text{Vertical}), & \theta \in [67.5^\circ, 112.5^\circ) \implies \text{Vecinos: } (x-1, y) \text{ y } (x+1, y) \\ 
135^\circ (\text{Diagonal Pos.}), & \theta \in [112.5^\circ, 157.5^\circ) \implies \text{Vecinos: } (x-1, y-1) \text{ y } (x+1, y+1) 
\end{cases}$$

#### 3.2. Formulación de la Varianza Muestral Local
Para una ventana local $W$ de tamaño $k \times k$ centrada en $(x, y)$ con $N = k^2$:
$$\mu_W(x, y) = \frac{1}{N} \sum_{u=-a}^a \sum_{v=-a}^a I(x+u, y+v)$$
$$\sigma_W^2(x, y) = \frac{1}{N} \sum_{u=-a}^a \sum_{v=-a}^a \left(I(x+u, y+v) - \mu_W(x, y)\right)^2$$
Operador acotado:
$$R(x, y) = \frac{\sigma_W^2(x, y)}{1 + \sigma_W^2(x, y)}$$

### 4. Casos de Uso y Aplicación (Python + OpenCV / NumPy)
Implementación integral desde cero de la supresión de no máximos (NMS), la histéresis biumbral y el operador de varianza local:

```python
import numpy as np
import cv2

def supresion_no_maximos_scratch(magnitud: np.ndarray, angulo_grados: np.ndarray) -> np.ndarray:
    """
    Algoritmo de Supresión de No Máximos (NMS) para adelgazar bordes a 1 píxel de espesor.
    """
    H, W = magnitud.shape
    nms = np.zeros((H, W), dtype=np.float64)
    
    # Ajustar ángulos al rango [0, 180]
    angulo = angulo_grados.copy()
    angulo[angulo < 0] += 180.0
    
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            theta = angulo[y, x]
            mag_actual = magnitud[y, x]
            
            # Determinar vecinos de comparación según el sector angular
            # Sector 0: Horizontal (0 grados) -> vecinos Este y Oeste
            if (0.0 <= theta < 22.5) or (157.5 <= theta <= 180.0):
                v1 = magnitud[y, x + 1]
                v2 = magnitud[y, x - 1]
            # Sector 1: Diagonal 45 grados
            elif 22.5 <= theta < 67.5:
                v1 = magnitud[y - 1, x + 1]
                v2 = magnitud[y + 1, x - 1]
            # Sector 2: Vertical 90 grados -> vecinos Norte y Sur
            elif 67.5 <= theta < 112.5:
                v1 = magnitud[y - 1, x]
                v2 = magnitud[y + 1, x]
            # Sector 3: Diagonal 135 grados
            elif 112.5 <= theta < 157.5:
                v1 = magnitud[y - 1, x - 1]
                v2 = magnitud[y + 1, x + 1]
            else:
                v1, v2 = 0, 0
                
            # Conservar sólo si es un pico estricto local
            if mag_actual >= v1 and mag_actual >= v2:
                nms[y, x] = mag_actual
            else:
                nms[y, x] = 0.0
                
    return nms


def histeresis_biumbral_scratch(nms: np.ndarray, t_bajo: float, t_alto: float) -> np.ndarray:
    """
    Algoritmo de Umbralización con Histéresis y conectividad de 8 vecinos
    para preservar bordes débiles conectados a bordes fuertes.
    """
    H, W = nms.shape
    salida = np.zeros((H, W), dtype=np.uint8)
    
    # Identificar bordes fuertes y débiles
    fuertes_y, fuertes_x = np.where(nms >= t_alto)
    debiles_y, debiles_x = np.where((nms >= t_bajo) & (nms < t_alto))
    
    # 255: Borde fuerte, 75: Borde débil
    salida[fuertes_y, fuertes_x] = 255
    salida[debiles_y, debiles_x] = 75
    
    # Cola de propagación de conectividad a partir de los bordes fuertes
    pila = list(zip(fuertes_y, fuertes_x))
    
    # Desplazamientos de conectividad-8
    dx = [-1, -1, -1,  0, 0,  1, 1, 1]
    dy = [-1,  0,  1, -1, 1, -1, 0, 1]
    
    while pila:
        cy, cx = pila.pop()
        for i in range(8):
            ny, nx = cy + dy[i], cx + dx[i]
            if 0 <= ny < H and 0 <= nx < W:
                if salida[ny, nx] == 75: # Si el vecino es débil, se promueve a fuerte
                    salida[ny, nx] = 255
                    pila.append((ny, nx))
                    
    # Suprimir los bordes débiles que nunca se conectaron a uno fuerte
    salida[salida != 255] = 0
    return salida


def operador_bordes_varianza_local(imagen_suavizada: np.ndarray, ksize: int = 3) -> np.ndarray:
    """
    Detector de bordes estadístico no lineal basado en la varianza local:
    R = 1 - (1 / (1 + sigma^2))
    """
    H, W = imagen_suavizada.shape
    radio = ksize // 2
    img_pad = np.pad(imagen_suavizada, radio, mode='reflect').astype(np.float64)
    R_map = np.zeros((H, W), dtype=np.float64)
    
    for y in range(H):
        for x in range(W):
            ventana = img_pad[y:y + ksize, x:x + ksize]
            var_local = np.var(ventana)
            # Función de respuesta acotada [0, 1]
            R_map[y, x] = 1.0 - (1.0 / (1.0 + var_local))
            
    R_visual = np.clip(R_map * 255.0, 0, 255).astype(np.uint8)
    return R_visual
```

---

## Cuadro Sinóptico de Integración: Pipeline de Procesamiento Digital de Imágenes

Para consolidar las 7 sesiones en una arquitectura coherente, el siguiente diagrama de flujo resume el pipeline algorítmico global implementado a lo largo del curso:

```
[Datos de Entrada]
  ├── Imagen Plana (RGB, 8 bits)  ──────> [Descomposición Espectral / Gris Biológico] ─┐
  ├── Resonancia Magnética (16 bits) ──> [Extracción ROI Libre / Test KS Rayleigh]  ──┼──> [Modelado de Ruido]
  └── Tomografía Axial (DICOM / HU)  ──> [Ventaneo Clínico Tisular (WL / WW)] ────────┘            │
                                                                                                   ▼
                                                            ┌──────────────────────────────────────┴──────────────────────────────────────┐
                                                            │                   ETAPA 1: PRE-SUAVIZADO (PASO BAJO)                        │
                                                            │ (Regla de Oro: Condición sine qua non para contener amplificación de ruido)│
                                                            ├───────────────────────────────┬─────────────────────────────┬───────────────┤
                                                            │       Filtro Gaussiano        │       Filtro Promedio       │Filtro Mediana │
                                                            │(Minimiza producto de Gabor 2D)│(Box blur / Suma unitaria)   │ (No lineal)   │
                                                            └───────────────────────────────┴─────────────────────────────┴───────────────┘
                                                                                                   │
                                                                                                   ▼
                                                            ┌─────────────────────────────────────────────────────────────────────────────┐
                                                            │                 ETAPA 2: OPERADORES DIFERENCIALES Y ESTADÍSTICOS            │
                                                            ├─────────────────────────────────────────────┬───────────────────────────────┤
                                                            │     Sobel Discreto (Series de Taylor)       │   Operador Varianza Local     │
                                                            │   Gx, Gy ──> Magnitud y Dirección Angular   │     R = 1 - 1/(1 + sigma^2)   │
                                                            └─────────────────────────────────────────────┴───────────────────────────────┘
                                                                                                   │
                                                                                                   ▼
                                                            ┌─────────────────────────────────────────────────────────────────────────────┐
                                                            │                    ETAPA 3: OPTIMIZACIÓN DE BORDES (CANNY)                  │
                                                            ├─────────────────────────────────────────────────────────────────────────────┤
                                                            │ 1. Supresión de No Máximos (NMS): Adelgazamiento morfológico a 1 px         │
                                                            │ 2. Histéresis Biumbral: Conectividad-8 de candidatos débiles a fuertes      │
                                                            └─────────────────────────────────────────────────────────────────────────────┘
                                                                                                   │
                                                                                                   ▼
                                                                                   [Segmentación Anatómica Final]
```

---

## Conclusiones Pedagógicas y Recomendaciones de Examen / Laboratorio

1. **Rigor Numérico:** Nunca confíe en representaciones puramente visuales antes de inspeccionar la matriz numérica subyacente. Los monitores estándar distorsionan la profundidad radiológica real de 16 bits.
2. **Respeto a la Física de Adquisición:** Cada modalidad diagnóstica imprime su propia firma estocástica (Ruido Gaussiano en óptica/TAC; Rayleigh/Rician en RM). El filtro seleccionado debe responder a la física del sensor, no al azar.
3. **Invarianza y Estabilidad:** Los filtros de paso bajo siempre deben conservar la energía radiométrica ($\sum K = 1$), y los operadores diferenciales jamás deben aplicarse directamente sobre datos crudos sin un previo desacoplamiento del ruido.

