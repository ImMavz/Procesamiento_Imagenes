# Guía Maestra y Estratégica: El Pipeline de Procesamiento Digital de Imágenes (PDI)
**De la Adquisición Radiométrica al Extractor de Características Morfológicas**  
*Cátedra de Procesamiento de Imágenes y Visión Artificial — 9.° Semestre, Ingeniería de Sistemas*  
*Guía Definitiva de Estudio y Libreto de Sustentación para Exposición Oral*

---

## 1. Visión General del Pipeline (El "Big Picture")

En la visión artificial y el análisis bioinformático profesional, el procesamiento de imágenes no es un conjunto de filtros decorativos aislados ni la llamada ciega a cajas negras de librerías. Es una **cadena secuencial de transformaciones estocásticas y algebraicas**, donde el resultado de cada etapa es la condición matemática indispensable para la siguiente.

```
       +-----------------------------------------------------------------------------------+
       |                 MODALIDADES DE ENTRADA HETEROGÉNEAS CRUDA                         |
       |  1. Imagen Plana (RGB, 8 bits)  2. Resonancia (RM, 16 bits)  3. Tomografía (HU)   |
       +-----------------------------------------------------------------------------------+
                                                 |
                                                 v
   [ETAPA 1: I/O, HEADERS Y ANONIMIZACIÓN] ──> Valida calibración física y Ley 1581 (Disociación)
                                                 |
                                                 v
   [ETAPA 2: DESACOPLAMIENTO ESPECTRAL]   ──> Gris biológico retiniano (ITU-R BT.601) o YUV/HSV
                                                 |
                                                 v
   [ETAPA 3: DINÁMICA RADIOMÉTRICA]       ──> Ventaneo Tisular (HU) y Ecualización por CDF / CLAHE
                                                 |
                                                 v
   [ETAPA 4: MODELAMIENTO DE RUIDO]       ──> Extracción ROI homogénea, 4 Momentos y Test K-S
                                                 |
                                                 v
   [ETAPA 5: PRE-SUAVIZADO (PASO BAJO)]   ──> Gaussiano / Mediana (REGLA DE ORO DE ESTABILIZACIÓN)
                                                 |
                                                 v
   [ETAPA 6: GRADIENTE DIFERENCIAL 2D]    ──> Derivadas discretas por Taylor (Sobel: Gx, Gy, Mag, Dir)
                                                 |
                                                 v
   [ETAPA 7: EXTRACCIÓN DE BORDES]        ──> Varianza Local: R = 1 - 1/(1 + sigma^2) / Canny (NMS)
```

### ¿Por qué existe este orden exacto?
1. **No se puede calcular gradientes sin conocer la escala física:** Si procesamos una Tomografía sin convertirla a Unidades Hounsfield (HU), un píxel con valor numérico $1200$ podría ser aire o hueso dependiendo del fabricante del tomógrafo.
2. **No se puede filtrar sin modelar el ruido:** Aplicar un filtro de promedio a un ruido impulsivo (sal y pimienta) o a un ruido Rician solo dispersa la mancha en una región más amplia; hay que conocer la función de probabilidad del ruido para escoger el filtro óptimo.
3. **Regla de Oro de la Cátedra (Pre-suavizado obligatorio):** La derivación espacial en el dominio de Fourier amplifica las altas frecuencias de forma proporcional ($\mathcal{F}\{\nabla f\} = j2\pi \mathbf{u} F(\mathbf{u})$). Si calculamos bordes directamente sobre la imagen cruda sin suavizar, la derivada no detectará la anatomía, sino las fluctuaciones cuánticas del sensor (la "pelusa" del ruido).
4. **Delimitación Unitaria:** Una vez obtenidos los gradientes continuos, se refinan los contornos mediante operadores de varianza local o supresión de no máximos para entregar un espesor unitario (1 píxel) apto para el diagnóstico clínico o la segmentación automática.

---

## 2. Paso a Paso del Pipeline: Teoría, Analogías y Transformación Matricial

---

### Módulo 1: Carga de Datos, Exploración de Headers y Anonimización Ético-Legal

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (La Ficha Médica en el Sobre de Seguridad):**  
  Imaginar que un archivo JPEG o PNG común es como una fotografía impresa pegada en la nevera: muestra un paisaje visual, pero nadie sabe con qué lente se tomó, ni a qué distancia, ni qué significa físicamente cada tono de gris.  
  Un archivo **DICOM** o **NIfTI**, en cambio, es una historia clínica completa dentro de un sobre sellado de hospital. No contiene únicamente la imagen; engloba una etiqueta de calibración física (cuántos milímetros reales mide cada píxel) y los datos confidenciales del paciente.  
  El proceso de **anonimización** es equivalente a pasar un marcador negro indeleble sobre el nombre, cédula y fecha de nacimiento antes de que el archivo salga del archivo central a los laboratorios de cómputo, cumpliendo con la Ley Estatutaria 1581 de 2012 de Colombia y las normas internacionales HIPAA.

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  * **Imagen Plana:** Matriz tridimensional $(H, W, 3)$ de tipo `uint8` ($[0, 255]$). Si contiene canal Alfa (RGBA, 4 canales), se trunca a 3 canales para descartar la máscara de opacidad de software.
  * **Resonancia Magnética (RM):** Matriz 2D de tipo `uint16` con valores crudos de intensidad entre $[0, 65535]$.
  * **Tomografía (TAC):** Almacenada inicialmente en memoria como enteros sin signo (`uint16`). Se le aplica la función de transferencia lineal definida en el encabezado DICOM:
    $$\text{HU} = \text{StoredValue} \times \text{RescaleSlope} + \text{RescaleIntercept}$$
    La matriz pasa de enteros positivos $[0, 4095]$ a números en coma flotante con signo $[ -1024.0, +3071.0 ]$, donde $-1000\text{ HU}$ representa el aire atmosférico, $0\text{ HU}$ el agua pura y $>+400\text{ HU}$ las estructuras óseas compactas.
* **Impacto Visual:** La matriz pasa de ser un mapa numérico arbitrario a una representación físicamente calibrada en densidades radiológicas universales.

---

### Módulo 2: Descomposición Espectral y Espacios de Color (Exclusivo Imagen Plana)

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (El Ojo Humano como un Receptor Selectivo):**  
  Nuestros ojos no son sensores fotográficos imparciales; son receptores biológicos afinados durante millones de años de evolución. En la retina, los conos encargados de la visión diurna y del color están sintonizados con longitudes de onda rojas ($L$), verdes ($M$) y azules ($S$). Sin embargo, la mayor concentración y sensibilidad espectral se encuentra alrededor de los $555\text{ nm}$ (el verde de la vegetación diurna).  
  Si calculáramos el nivel de gris promediando $\frac{R+G+B}{3}$, estaríamos asumiendo que vemos el azul con la misma fuerza que el verde. En la práctica, el azul nos resulta mucho más oscuro.  
  Convertir a **YUV** o **HSV** equivale a separar el dibujo a lápiz (la luminancia o el brillo) de la acuarela (el tono y la saturación). Esto permite analizar formas y bordes sin que los cambios en el color o las sombras distorsionen el algoritmo.

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  La matriz tridimensional $(H, W, 3)$ de enteros `uint8` se desacopla:
  1. **Gris Biológico (ITU-R BT.601):**
     $$\text{Gris}(y, x) = \lfloor 0.299 \cdot R + 0.5876 \cdot G + 0.1140 \cdot B \rfloor$$
     El canal Verde absorbe casi el $59\%$ de la intensidad, reflejando fielmente la fisiología humana. La matriz se compacta a $(H, W)$ en rango $[0, 255]$.
  2. **YUV:** La matriz RGB se multiplica píxel a píxel por la matriz de transformación 3x3 de telecomunicaciones:
     $$\begin{bmatrix} Y \\ U \\ V \end{bmatrix} = \begin{bmatrix} 0.299 & 0.5876 & 0.114 \\ -0.1471 & -0.2889 & 0.4360 \\ 0.6150 & -0.5150 & -0.1000 \end{bmatrix} \begin{bmatrix} R \\ G \\ B \end{bmatrix}$$
     $Y$ queda acotado en $[0, 255]$ (Luminancia pura), mientras que $U$ y $V$ representan la diferencia cromática con signo.
  3. **HSV:** El canal $H$ (Hue/Matiz) transforma el espacio cartesiano en un ángulo polar $[0^\circ, 360^\circ]$ (mapeado en OpenCV a $[0, 179]$).
* **Impacto Visual:** La imagen a color se descompone en un mapa monocromático de alta fidelidad perceptual y mapas de color independientes de la iluminación.

---

### Módulo 3: Histograma, Función de Distribución Acumulada (CDF) y Dinámica de Contraste

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (El Censo Poblacional y el Estiramiento de un Acordeón):**  
  El **histograma** es el censo demográfico de la imagen: cuenta cuántos píxeles viven en cada nivel de brillo. Si todos los píxeles están amontonados en un rincón oscuro (como personas apiñadas en una esquina de una habitación), la imagen se ve opaca, lavada y sin contraste.  
  La **Función de Distribución Acumulada (CDF)** actúa como un ranking percentil: le dice a cada píxel qué porcentaje de la población total es más oscuro que él.  
  La **Ecualización de Histograma** es como tomar un acordeón comprimido y estirarlo a lo largo de todo el teclado disponible: obliga a que los tonos de gris se repartan de manera equitativa por todo el rango dinámico.  
  En Tomografía, el **Ventaneo ($WL/WW$)** es como usar una lupa de aumento radiológico: en lugar de intentar ver toda la escala desde el aire hasta el hueso, centramos la mirada exclusivamente en el rango donde vive el cerebro o el tejido blando.

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  * **Cálculo de Frecuencias:** Se calcula el vector $h(r_k) = \sum \mathbf{1}_{\{I(x,y)=r_k\}}$, y su versión acumulada normalizada:
    $$\text{CDF}(k) = \frac{\sum_{j=0}^k h(r_j)}{M \cdot N}$$
  * **Mapeo LUT (Look-Up Table):** Cada píxel con valor $k$ es reasignado según:
    $$s_k = \left\lfloor \frac{\text{CDF}(k) - \text{CDF}_{\min}}{1 - \text{CDF}_{\min}} \times (L - 1) \right\rfloor$$
  * **Ventaneo en TAC:** A partir de los parámetros clínicos $WL$ (Nivel) y $WW$ (Ancho), los vóxeles se recortan y proyectan a 8 bits:
    $$I_{\text{visual}}(x,y) = \text{clip}\left(\left\lfloor \frac{I_{\text{HU}}(x,y) - (WL - WW/2)}{WW} \times 255 \right\rfloor, 0, 255\right)$$
* **Impacto Visual:** Una tomografía cerebral que cruda parecía una silueta grisácea plana e incomprensible revela con nitidez asombrosa la diferenciación entre los surcos corticales, la sustancia gris ($+40\text{ HU}$) y la sustancia blanca ($+30\text{ HU}$).

---

### Módulo 4: Modelamiento Estocástico del Ruido en Imágenes y Test de Kolmogorov-Smirnov

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (Escuchar el Silencio para Reconocer el Tipo de Micrófono):**  
  Para saber si un micrófono tiene estática eléctrica o interferencia de radio, el ingeniero de sonido no analiza la voz de un cantante en pleno concierto, sino que graba el silencio absoluto de la sala.  
  En una imagen digital ocurre exactamente lo mismo: no podemos modelar el ruido donde hay bordes u objetos, porque las variaciones del dibujo se confundirían con el ruido. Se debe buscar una **Región Homogénea (ROI)** donde la escena sea teóricamente plana (como la esquina superior exterior de una resonancia magnética, donde solo hay aire libre).  
  El **Test de Kolmogorov-Smirnov (K-S)** es como una auditoría de control de calidad: compara la curva acumulada empírica del ruido contra la curva matemática de una distribución Gaussiana o Rayleigh ideal. Si la distancia máxima ($D$) es pequeña, la auditoría aprueba el modelo ($p > 0.05$).

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  Se aísla una submatriz $\Omega_{\text{ROI}}$ de $50 \times 50$ píxeles y se calculan sus 4 momentos estadísticos centrales:
  1. Media ($\mu = \frac{1}{N}\sum x_i$): Nivel basal de señal térmica.
  2. Varianza ($\sigma^2 = \frac{1}{N-1}\sum (x_i - \mu)^2$): Potencia energética del ruido.
  3. Asimetría / Skewness ($S = \frac{E[(x-\mu)^3]}{\sigma^3}$): Si $S \approx 0$, es simétrico (Gaussiano). Si $S > 0$, tiene cola larga hacia la derecha.
  4. Curtosis ($K = \frac{E[(x-\mu)^4]}{\sigma^4}$): Escarpamiento del pico central.
  
  *En Resonancia Magnética:* Los datos crudos provienen de antenas en fase y cuadratura ($I, Q$). La magnitud $M = \sqrt{I^2 + Q^2}$ transforma el ruido Gaussiano de fondo en una distribución de **Rayleigh** con asimetría positiva pronunciada ($S > 0$).
* **Impacto Visual:** Este paso no modifica los píxeles; genera el diagnóstico matemático que dictamina cuál filtro de paso bajo debe aplicarse en la siguiente etapa.

---

### Módulo 5: Motor de Convolución 2D y Filtros Espaciales de Paso Bajo (Suavizado)

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (Mirar a Través de un Vidrio Esmerilado vs. Un Juez Imparcial):**  
  La **convolución** es como deslizar una pequeña lupa con aumento de $3 \times 3$ ventanas sobre cada punto de una cuadrícula. En cada celda de la lupa hay grabados unos números (los pesos del kernel). Miramos lo que hay debajo, multiplicamos cada valor por su peso correspondiente y anotamos la suma en una nueva hoja.  
  * **El Filtro Promedio (Box Blur):** Trata a todos los vecinos por igual. Es como una votación comunal donde todos los vecinos tienen el mismo peso: el resultado es un desenfoque tosco y nublado.  
  * **El Filtro Gaussiano:** Es una campana centrada: le da el máximo valor al píxel central y va reduciendo el peso de los vecinos a medida que se alejan. Produce un suavizado elegante que atenúa el ruido sin destrozar la estructura de los objetos.  
  * **El Filtro de Mediana (No Lineal):** Es como un juez que ignora los extremos absurdos en una competencia. Si 8 vecinos tienen intensidades alrededor de $100$ y un píxel de ruido vale $65000$ (un pixel quemado blanco), el filtro de mediana ordena los números de menor a mayor y se queda con el del centro ($100$). El ruido desaparece instantáneamente sin que el borde se difumine.

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  1. **Padding Espejo (Reflexión de Bordes):** Para procesar una imagen de $H \times W$ con un kernel de $k \times k$ (radio $p = \lfloor k/2 \rfloor$), la matriz se expande a $(H + 2p, W + 2p)$ reflejando las filas y columnas limítrofes ($I(-x) = I(x)$). Esto evita el borde negro artificial que provocaría el zero-padding.
  2. **Convolución Lineal:** Se rota el kernel $180^\circ$ y se calcula la sumatoria:
     $$I_{\text{out}}(y, x) = \left\lfloor \sum_{m=-p}^p \sum_{n=-p}^p I_{\text{pad}}(y+p-m, x+p-n) \cdot K(m, n) \right\rfloor$$
     Condición de conservación radiométrica: $\sum \sum K(m,n) = 1.0$.
  3. **Filtrado de Mediana:**
     $$I_{\text{mediana}}(y, x) = \text{Mediana}\left(\{ I_{\text{pad}}(y+u, x+v) \mid -p \le u, v \le p \}\right)$$
* **Impacto Visual:** Los granos aislados de sal y pimienta o la estática de alta frecuencia desaparecen. Las transiciones anatómicas se vuelven continuas y estables.

---

### Módulo 6: Filtros Espaciales de Paso Alto (Detección de Bordes por Sobel y Laplaciano)

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (Caminar con un Bastón en la Penumbra):**  
  Imaginar que caminamos por una habitación oscura tocando el piso con un bastón. Mientras el piso sea plano y continuo, no sentimos cambios bruscos. Pero si de pronto hay un escalón, la punta del bastón registra una caída abrupta en la altura.  
  Eso es una **derivada espacial**: mide qué tan rápido cambia la intensidad entre un paso y el siguiente.  
  * El **Gradiente de Sobel** nos dice dos cosas fundamentales: la altura del escalón (la **Magnitud**, qué tan fuerte es el borde) y hacia dónde está orientada la rampa de caída (la **Dirección** del ángulo $\theta$).  
  * El **Laplaciano** mide la curvatura (la segunda derivada). Es el punto exacto de inflexión donde la caída cambia de cóncava a convexa (*cruce por cero*).

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  La imagen suavizada $I_{\text{smooth}}$ es sometida a convolución con los kernels discretos deducidos analíticamente por series de Taylor:
  $$K_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad K_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$
  * Se obtienen dos matrices de derivadas con signo (`float64`): $G_x$ (bordes verticales) y $G_y$ (bordes horizontales).
  * **Magnitud Euclidiana:** Matriz continua no negativa:
    $$M(y, x) = \sqrt{G_x(y, x)^2 + G_y(y, x)^2}$$
  * **Dirección Angular Polar:** Matriz continua en grados $[-180^\circ, 180^\circ]$:
    $$\theta(y, x) = \arctan2(G_y(y, x), G_x(y, x)) \times \frac{180}{\pi}$$
  * **Laplaciano Discreto ($\nabla^2 I$):** Kernel de 8 vecinos con suma cero ($\sum K = 0$):
    $$K_{\text{Lap}} = \begin{bmatrix} 1 & 1 & 1 \\ 1 & -8 & 1 \\ 1 & 1 & 1 \end{bmatrix}$$
* **Impacto Visual:** Las zonas homogéneas (el interior del cerebro o las paredes) se vuelven completamente negras ($M \approx 0$). Solo las líneas divisorias, membranas celulares, cráneo y contornos de objetos resaltan como trazos brillantes.

---

### Módulo 7: Operadores Estadísticos Locales (Detector Basado en la Varianza) y Canny

#### 1. Teoría Explicada con Analogía
* **La Analogía Cotidiana (El Sensor de Diversidad Local y el Adelgazamiento Morfológico):**  
  En lugar de multiplicar números por una máscara fija como en Sobel, el **Operador de Varianza** toma una pequeña lupa de $3 \times 3$ y se pregunta: *"¿Qué tan parecidos son los píxeles aquí dentro?"*.  
  Si todos los vecinos son casi iguales (como una pared blanca o el fondo negro), la varianza local es cero y la respuesta es negro. Pero si la ventana cruza el borde entre una zona negra y una blanca, la varianza estalla hacia el infinito.  
  El **Algoritmo de Canny** es el escultor final: toma esa cordillera montañosa de bordes gruesos generada por el gradiente y, mirando hacia la dirección del ángulo, elimina todo aquel píxel que no sea la cúspide absoluta de la montaña (**Supresión de No Máximos**). Luego, aplica un biumbral (**Histéresis**) que funciona como una cadena de rescate: conserva los bordes débiles únicamente si están agarrados de la mano de un borde fuerte principal.

#### 2. Qué le Ocurre a la Imagen a Nivel de Píxeles y Matrices
* **Valores y Tipos de Datos:**  
  1. **Varianza Local:** Para cada ventana de $3 \times 3$, se calcula la varianza muestral $\sigma_W^2(y, x)$. Se aplica la función de saturación sigmoidal normalizada a $[0, 1]$:
     $$R(y, x) = 1 - \frac{1}{1 + \sigma_W^2(y, x)} = \frac{\sigma_W^2(y, x)}{1 + \sigma_W^2(y, x)}$$
     Se multiplica por $255.0$ para generar una máscara `uint8`.
  2. **Supresión de No Máximos (NMS):** La matriz de magnitud $M(y, x)$ se compara exclusivamente contra sus dos vecinos en la recta ortogonal discretizada en $0^\circ, 45^\circ, 90^\circ$ o $135^\circ$. Si $M(y, x)$ no es estrictamente mayor que ambos, se fija en $0$.
  3. **Histéresis Biumbral:** Clasificación ternaria ($0, 75, 255$) y propagación por cola con conectividad-8.
* **Impacto Visual:** Los bordes difusos y gruesos de $3$ a $5$ píxeles de espesor colapsan en aristas delgadísimas y perfectas de **exactamente 1 píxel de ancho**, listas para alimentar un clasificador morfológico o un modelo de aprendizaje automático.

---

## 3. Entendiendo los Notebooks: Desglose de Código Paso a Paso

El notebook principal del proyecto (`Control_1_PDI.ipynb`) fue diseñado siguiendo una arquitectura de ingeniería de software limpia: desacoplamiento modular, programación algorítmica desde cero (*from scratch*) y visualización de matrices intermedias.

```
+--------------------------------------------------------------------------------------------------+
|                              ESTRUCTURA DEL NOTEBOOK CONTROL_1_PDI.IPYNB                         |
+--------------------------------------------------------------------------------------------------+
| Célula 1 & 3: Inicialización, importaciones permitidas y resolución dinámica de rutas            |
| Célula 4 & 5: Carga cruda, rescale físico (Slope/Intercept) y visualización multi-modal          |
| Célula 7 & 8: Espacios de color (RGB a Gris ITU-R BT.601, YUV, HSV manual)                      |
| Célula 10 & 11: Histogramas discretos, CDF normalizada y percentil 80                            |
| Célula 14 & 15: Extracción de ROIs homogéneas en fondo libre y Test Kolmogorov-Smirnov           |
| Célula 17 & 18: Padding espejo, Motor de convolución 2D (4 ciclos for) y experimento Gaussiano  |
| Célula 19: Comparativa de filtrado paso bajo: Gaussiano vs Mediana en las 3 imágenes             |
| Célula 21 & 22: Operadores diferenciales de Sobel desacoplado (Taylor) y Laplaciano              |
| Célula 24 & 25: Operador no lineal basado en la varianza local: R = 1 - 1/(1 + sigma^2)          |
| Célula 26: Matriz de síntesis comparativa multimodal y banco de preguntas de sustentación        |
+--------------------------------------------------------------------------------------------------+
```

### Bloque 1: Carga Robusta y Desacoplamiento de Formatos (Células 3, 4 y 5)
```python
# Carga de la imagen plana descartando canal Alfa
img = Image.open(ruta_archivo)
arr = np.array(img)
if arr.ndim == 3 and arr.shape[2] == 4:
    arr = arr[:, :, :3] # Se asegura tener una matriz pura de 3 canales RGB
```
* **¿Por qué se programó así?**  
  Las imágenes PNG a menudo cargan un cuarto canal de transparencia que rompería cualquier multiplicación matricial 3D de color posterior.  
  Para la Tomografía (`pydicom`), el código no lee simplemente píxeles; extrae `ds.RescaleSlope` y `ds.RescaleIntercept` para transformar los números a la escala física de Hounsfield:
  ```python
  img_tac_hu = raw_tac.astype(np.float64) * slope + intercept
  ```

### Bloque 2: Conversión a Gris Biológico vs. Simple Promedio (Célula 7)
```python
def rgb_a_gris_biologico(img_rgb: np.ndarray) -> np.ndarray:
    img = img_rgb.copy().astype(np.float64)
    gris = 0.299 * img[:, :, 0] + 0.5876 * img[:, :, 1] + 0.114 * img[:, :, 2]
    return np.floor(gris).astype(np.uint8)
```
* **¿Por qué se programó así?**  
  Se utiliza `np.floor()` en lugar de un simple casteo truncado para respetar la discretización hacia el entero inferior más próximo del nivel de cuantización. Se implementó sin utilizar `cv2.cvtColor()` para demostrar al profesor la deducción manual de los pesos de luminancia fotópica retiniana.

### Bloque 3: Cálculo del Histograma y CDF desde Cero (Célula 10)
```python
# Histograma manual sin librerías
hist = np.zeros(bins, dtype=np.int64)
for val in img:
    # mapeo lineal del valor al bin correspondiente
    idx = int((val - rango_min) / (rango_max - rango_min) * (bins - 1))
    hist[idx] += 1
```
* **¿Por qué se programó así?**  
  En lugar de invocar `np.histogram` o `cv2.calcHist`, se recorre el array linealizado para evidenciar el principio de la suma acumulada discreta. Para el cálculo del Percentil 80:
  ```python
  def interpolar_percentil(cdf: np.ndarray, bin_edges: np.ndarray, percentil: float) -> float:
      target = percentil / 100.0
      idx = np.searchsorted(cdf, target)
      return bin_edges[idx]
  ```
  Permite responder analíticamente qué valor de atenuación acumula el $80\%$ de la energía espectral de la imagen sin depender de funciones prefabricadas.

### Bloque 4: Modelamiento Estocástico del Ruido con Test K-S (Célula 14)
```python
# Extracción de la ROI en aire libre (fondo negro de la esquina)
roi = imagen[0:50, 0:50].copy().astype(np.float64)
# Cálculo de momentos: Varianza, Skewness (Sesgo) y Kurtosis
skewness = stats.skew(roi.flatten())
kurtosis = stats.kurtosis(roi.flatten(), fisher=True)
d_stat, p_val = stats.kstest(roi.flatten(), 'norm', args=(media, desv))
```
* **¿Por qué se programó así?**  
  El notebook recorta intencionalmente la ventana $[0:50, 0:50]$ en RM y TAC porque en esa zona el cuerpo del paciente no existe; es aire puro exterior. Los momentos estadísticos revelan la física del receptor:
  * Si la muestra exhibe $p\text{-valor} > 0.05$, se valida la hipótesis nula de **Ruido Gaussiano**.
  * En Resonancia Magnética, la prueba contra Gaussiano falla ($p < 0.05$) debido a la asimetría de la distribución de **Rayleigh** generada por el cálculo de la magnitud en cuadratura.

### Bloque 5: Motor de Convolución 2D con Padding Espejo (Célula 17)
```python
def aplicar_padding_espejo(imagen: np.ndarray, pad: int) -> np.ndarray:
    # Refleja filas superiores e inferiores
    for p in range(pad):
        out[pad - 1 - p, pad:pad + W] = imagen[p, :]
        out[pad + H + p, pad:pad + W] = imagen[H - 1 - p, :]
```
* **¿Por qué se programó así?**  
  Un `zero-padding` (relleno con ceros) alteraría la varianza en los límites del cráneo simulando un falso borde negro de alta intensidad. El padding por reflexión mantiene intacta la continuidad de la superficie.  
  El motor de convolución utiliza los 4 ciclos anidados clásicos requeridos en la rúbrica de la cátedra:
  1. Dos bucles exteriores para recorrer cada fila $y$ y columna $x$ de la imagen de salida.
  2. Dos bucles interiores para calcular el producto punto local entre la submatriz y el kernel volteado espacialmente.

### Bloque 6: Detección de Bordes por Sobel y Laplaciano (Célula 21)
```python
Kh = np.array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]], dtype=np.float64)
Kv = np.array([[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]], dtype=np.float64)
Gx = convolucion(img, Kh)
Gy = convolucion(img, Kv)
magnitud = np.sqrt(Gx ** 2 + Gy ** 2)
direccion = np.arctan2(Gy, Gx) * (180.0 / np.pi)
```
* **¿Por qué se programó así?**  
  Sobel desacopla la diferenciación central $[-1, 0, 1]$ con una campana de suavizado triangular $[1, 2, 1]^T$ perpendicular. Al aplicar `np.arctan2(Gy, Gx)`, se obtiene el cuadrante polar exacto en grados $[-180^\circ, 180^\circ]$, suministrando la orientación del vector normal al borde.

### Bloque 7: Operador de Varianza Local sin Convolución (Célula 24)
```python
# Cálculo local no lineal
var_local = np.var(ventana)
R = 1.0 - (1.0 / (1.0 + var_local))
```
* **¿Por qué se programó así?**  
  Demuestra un paradigma alternativo a los filtros lineales basados en derivadas. La función $R = \frac{\sigma^2}{1 + \sigma^2}$ mapea asintóticamente la dispersión local al intervalo continuo $[0, 1]$, evitando desbordamientos numéricos y entregando bordes orgánicos estables sin calcular productos punto matriciales.

---

## 4. Puntos Clave para la Presentación (Cheat-Sheet de 5 Viñetas)

Usa estos cinco argumentos fundamentales durante la sustentación oral para demostrar absoluto dominio conceptual y técnico ante el profesor:

1. **La Coherencia Arquitectural del Pipeline Multimodal:**  
   *"Profesor, el pipeline no es un recetario genérico; está calibrado según la física de adquisición de cada modalidad. La imagen plana opera en 8 bits ($[0, 255]$) donde desacoplamos el color con la fórmula retiniana ITU-R BT.601; la Resonancia Magnética opera en 16 bits sin signo ($[0, 65535]$); y la Tomografía requiere reescalado físico a Unidades Hounsfield (HU) con su respectivo ventaneo de tejido blando ($WL=40, WW=80$), demostrando que el procesamiento digital inicia en la escala física del sensor y no en la visualización."*

2. **La Justificación Estocástica del Ruido (K-S Test):**  
   *"No adivinamos qué ruido tenía cada imagen. Recortamos una Región de Interés (ROI) en el fondo de aire libre y contrastamos la hipótesis nula con la prueba de Kolmogorov-Smirnov. Demostramos que mientras la imagen plana es compatible con ruido Gaussiano aditivo ($p > 0.05$), la Resonancia Magnética sigue una distribución de Rayleigh en el fondo debido a que la magnitud de la transformada de Fourier combina componentes en cuadratura en el K-Space."*

3. **La Regla de Oro del Pre-suavizado (Fourier y Estabilidad Numérica):**  
   *"La derivación espacial multiplica el espectro de Fourier por la frecuencia ($j 2\pi u$). Por lo tanto, calcular bordes sobre una imagen sin filtrar amplifica de forma explosiva las componentes de alta frecuencia correspondientes al ruido. El pre-suavizado con filtro Gaussiano o Mediana no es opcional; es una condición matemática sine qua non para que los operadores de Sobel o Laplaciano detecten límites anatómicos reales y no artefactos térmicos del sensor."*

4. **Deducción Rigurosa de Kernels por Series de Taylor:**  
   *"Los kernels de Sobel y Laplaciano no son matrices mágicas arbitrarias. Surgen de truncar la expansión de Taylor bidimensional con paso unitario $h=1$. La diferencia central $f(x+1) - f(x-1) = 2f'(x)$ deduce el vector de gradiente de primer orden $[-1, 0, 1]$, mientras que la suma de expansiones $f(x+1) - 2f(x) + f(x-1) = f''(x)$ deduce analíticamente el operador Laplaciano $\nabla^2 I$ de 4 y 8 vecinos con suma cero para garantizar conservación en zonas planas."*

5. **Optimalidad de Canny y Operador de Varianza Local:**  
   *"Para obtener bordes diagnósticos de espesor unitario (1 píxel), el gradiente de Sobel debe refinarse con la Supresión de No Máximos (NMS) guiada por el ángulo $\arctan2(Gy, Gx)$ y una histéresis biumbral conectada en conectividad-8. Alternativamente, nuestro operador estadístico local $R = 1 - \frac{1}{1 + \sigma^2}$ detecta bordes sin realizar convoluciones matriciales, transformando directamente la dispersión de varianza local del tejido en una respuesta sigmoidal normalizada."*

---

## Cuadro Sinóptico de Consulta Rápida para la Sustentación

| Etapa del Pipeline | Entrada | Transformación Principal | Salida | Función Crítica en Código |
| :--- | :--- | :--- | :--- | :--- |
| **1. Carga y Headers** | Archivo crudo (.jpg, .dcm) | Descarte de canal alfa / Slope & Intercept | Matriz calibrada | `cargar_imagen_plana()`, `dcmread()` |
| **2. Espacios de Color** | RGB $(H, W, 3)$ | Ponderación $0.299R + 0.587G + 0.114B$ | Gris $(H, W)$ / HSV / YUV | `rgb_a_gris_biologico()`, `rgb_a_yuv()` |
| **3. Contraste y CDF** | Matriz de intensidades | Mapeo LUT por distribución acumulada | Contraste expandido | `calcular_histograma()`, `calcular_cdf()` |
| **4. Análisis de Ruido** | ROI homogénea | Momentos ($\mu, \sigma^2, S, K$) y test K-S | Modelo estocástico validado | `calcular_momentos_estadisticos()`, `kstest()` |
| **5. Suavizado 2D** | Imagen ruidosa | Convolución Gaussiana / Mediana | Imagen suavizada estable | `aplicar_padding_espejo()`, `convolucion()` |
| **6. Gradientes (Sobel)** | Imagen suavizada | Expansión en series de Taylor | Magnitud y Dirección $\theta$ | `aplicar_sobel()`, `arctan2()` |
| **7. Bordes Finales** | Magnitud / Varianza | $R = \frac{\sigma^2}{1 + \sigma^2}$ o Canny NMS | Borde nítido (espesor 1 px) | `detector_bordes_varianza()`, NMS / Histéresis |

