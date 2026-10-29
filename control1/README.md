# GUÍA MAESTRA DE CONTROL 1: PROCESAMIENTO DIGITAL DE IMÁGENES (PDI)
**Ponderación:** 50% de la Calificación Final  
**Especialidad:** Visión por Computador, Procesamiento Matricial e Imágenes Médicas (DICOM/NIfTI)  
**Autor:** Joseph Herrera  
**Público Objetivo:** Estudiante preparándose para la sustentación oral en vivo ante el profesor y el jurado calificador.

---

# TABLA DE CONTENIDOS
1. [Introducción: La Gran Visión del Proyecto y las Reglas de Oro](#1-introducción-la-gran-visión-del-proyecto-y-las-reglas-de-oro)
2. [Las Tres Imágenes Protagonistas: Física, Números y Comparación](#2-las-tres-imágenes-protagonistas-física-números-y-comparación)
3. [Módulo 1: Carga, Exploración de Headers Físicos y Anonimización Clínica](#3-módulo-1-carga-exploración-de-headers-físicos-y-anonimización-clínica)
4. [Módulo 2: Descomposición Espectral y Espacios de Color (Exclusivo Imagen Plana)](#4-módulo-2-descomposición-espectral-y-espacios-de-color-exclusivo-imagen-plana)
5. [Módulo 3: Histograma, Curva CDF y Ecualización de Contraste](#5-módulo-3-histograma-curva-cdf-y-ecualización-de-contraste)
6. [Módulo 4: Modelamiento Estocástico del Ruido por ROI y Pruebas KS](#6-módulo-4-modelamiento-estocástico-del-ruido-por-roi-y-pruebas-ks)
7. [Módulo 5: Motor de Convolución 2D y Filtros de Paso Bajo (Suavizado)](#7-módulo-5-motor-de-convolución-2d-y-filtros-de-paso-bajo-suavizado)
8. [Módulo 6: Filtros Diferenciales de Paso Alto (Detección de Bordes)](#8-módulo-6-filtros-diferenciales-de-paso-alto-detección-de-bordes)
9. [Módulo 7: Operadores Basados en la Varianza Local (Detección sin Convolución)](#9-módulo-7-operadores-basados-en-la-varianza-local-detección-sin-convolución)
10. [Banco de Preguntas Típicas y Respuestas Letales para la Sustentación Oral](#10-banco-de-preguntas-típicas-y-respuestas-letales-para-la-sustentación-oral)

---

# 1. Introducción: La Gran Visión del Proyecto y las Reglas de Oro

### ¿De qué trata este Control y qué busca evaluar el profesor?
El objetivo general del curso de Procesamiento Digital de Imágenes (PDI) es llegar a segmentar estructuras anatómicas complejas (como el **sistema límbico cerebral**: amígdala, hipocampo y tálamo) y objetos del mundo real. 

Para lograrlo con rigor de ingeniería, este Control 1 evalúa si comprendemos que:
> **Una imagen digital NO es un dibujo ni una foto bonita en pantalla: es una matriz bidimensional o tridimensional de números crudos (*raw data*).**

La pantalla de tu computador es solo un dispositivo de despliegue que degrada o comprime obligatoriamente los datos a 8 bits ($0$ a $255$) para que el ojo humano los vea. Pero si un ingeniero procesa imágenes médicas degradándolas antes a 8 bits, destruye información clínica crucial que diferencia un tumor de un tejido sano.

### Las 4 Reglas de Oro del Profesor (Inviolables)
1. **PROHIBIDO usar librerías de alto nivel para los algoritmos:** Nada de OpenCV (`cv2`), nada de `skimage`, nada de `scipy.ndimage`. Todo algoritmo (espacios de color, histogramas, convolución, gaussiano, sobel, mediana) debe construirse **a mano (from scratch)** mediante ciclos `for` o álgebra de matrices básica en `numpy`. Usar librerías caja negra anula la sustentación.
2. **Inmutabilidad absoluta (Paso por Valor):** En Python, si haces `img_b = img_a`, ambas variables apuntan a la misma memoria; modificar una destruye la original. Por regla, **siempre** se debe clonar usando `img_original.copy()`.
3. **Respetar el rango dinámico crudo:** En Resonancia Magnética (16 bits) y Tomografía (Unidades Hounsfield con números negativos y positivos), todos los cálculos matemáticos (convoluciones, varianzas, histogramas) se hacen sobre los números reales, nunca convirtiendo a $0-255$.
4. **Truncamiento entero con función piso:** Las imágenes digitales operan sobre niveles de energía discretos. Por ello, tras acumular la convolución, el resultado se trunca con `np.floor()`.

---

# 2. Las Tres Imágenes Protagonistas: Física, Números y Comparación

El pipeline se evalúa comparativamente sobre tres modalidades con principios físicos de adquisición totalmente diferentes. Entender su física es el 50% de la sustentación:

| Propiedad | 1. Imagen Plana (`luna.jpg`) | 2. Resonancia Magnética (`RMI`) | 3. Tomografía Computarizada (`TAC`) |
| :--- | :--- | :--- | :--- |
| **Principio Físico** | Fotones de luz visible reflejados en una superficie. | Espines nucleares de hidrógeno bajo campo magnético y radiofrecuencia (tiempos $T_1 / T_2$). | Coeficiente lineal de atenuación de Rayos X al atravesar tejidos. |
| **Sensor de Adquisición** | Sensor CMOS/CCD con filtro Bayer (fotodiodos rojo, verde y azul). | Antenas / Bobinas de radiofrecuencia en cuadratura ($I$ y $Q$). | Tubo de rayos X giratorio y detectores cuánticos de gas o estado sólido. |
| **Estructuras Óptimas** | Formas y colores visibles en la superficie del objeto. | **Tejidos blandos:** Corteza cerebral, materia gris/blanca, hipocampo, amígdala. | **Tejidos densos:** Hueso cortical, cráneo, calcificaciones, hemorragias agudas. |
| **Tipo de Dato y Rango** | Enteros sin signo de 8 bits: $[0, 255]$ por cada canal. | Enteros de 16 bits crudos: $[0, 65535]$ (adimensional relativo). | Valores reales con signo en **Unidades Hounsfield (HU)**: $[-1024, +3000]$. |
| **Canales** | 3 canales (R, G, B) $\implies$ Matriz de forma $(H, W, 3)$. | 1 solo canal escalar $\implies$ Matriz 2D de forma $(H, W)$. | 1 solo canal escalar $\implies$ Matriz 2D de forma $(H, W)$. |
| **Distribución del Ruido** | **Gaussiano (Normal):** Ruido térmico de electrones en el sensor. | **Rayleigh / Rician:** Módulo de dos señales gaussianas ortogonales. | **Poisson:** Conteo cuántico de fotones de rayos X emitidos. |

### Explicación Sencilla de la Física de Cada Imagen:
* **La Imagen Plana:** Imagina tomar una foto con tu celular. La luz rebota en el perro o la pared, pasa por la lente y golpea millones de celditas diminutas (fotodiodos). Cada celdita mide la cantidad de luz y genera un número de 0 (oscuridad) a 255 (brillo máximo). Como hay 3 filtros de color (Rojo, Verde, Azul), tienes una matriz tridimensional.
* **La Resonancia Magnética (RM):** Tu cuerpo está hecho en un 70% de agua (átomos de hidrógeno con protones que giran como pequeños trompos). El resonador genera un campo magnético gigantesco que alinea esos trompos. Luego lanza pulsos de radio que los desvían; cuando el pulso se apaga, los protones se reacomodan liberando una señal de radio. El equipo mide cuánto tardan en volver a alinearse. Como el agua de la grasa, la sangre y el cerebro se reacomodan a velocidades muy distintas, la RM produce un contraste maravilloso entre tejidos blandos. Sus números van de 0 a miles sin unidades fijas.
* **La Tomografía Computarizada (TAC):** Es una máquina que dispara rayos X alrededor de la cabeza del paciente. El rayo X atraviesa el cuerpo y golpea un detector al otro lado. Si choca contra el aire, casi todo el rayo pasa libre; si choca contra el hueso duro, el hueso absorbe la mayoría de los rayos. Esta absorción se calibra usando una escala física inventada por Godfrey Hounsfield:
  * **Aire:** $-1000\text{ HU}$ (no frena casi nada de rayos X).
  * **Grasa corporal:** $-120$ a $-30\text{ HU}$.
  * **Agua pura:** $0\text{ HU}$ (punto cero de calibración).
  * **Músculo y cerebro:** $+30$ a $+60\text{ HU}$.
  * **Hueso compacto:** $+1000$ a $+2000\text{ HU}$ (frena fuertemente los rayos X).

---

# 3. Módulo 1: Carga, Exploración de Headers Físicos y Anonimización Clínica

### ¿Qué hace el código?
1. Carga la imagen plana `luna.jpg` con `PIL`. Si trae un cuarto canal (Alfa de transparencia), lo descarta automáticamente para dejar solo una matriz RGB limpia de dimensiones $(H, W, 3)$.
2. Lee los archivos médicos DICOM (`.dcm`) con `pydicom`. 
3. Extrae la información espacial y dimensional del encabezado (*header*):
   * `Rows` y `Columns`: Dimensiones de la matriz en píxeles.
   * `BitsAllocated` (16 bits): Espacio de memoria reservado en disco.
   * `BitsStored` (16 o 12 bits): Bits que realmente contienen señal.
   * `PixelSpacing` ($dy, dx$ en milímetros): Distancia física entre los centros de dos píxeles contiguos.
   * `SliceThickness` ($dz$ en milímetros): Grosor del corte anatómico.
4. Calcula el tamaño físico del mundo real:
   $$\text{Área del Píxel} = dy \times dx \quad (\text{mm}^2), \qquad \text{Volumen del Vóxel} = dy \times dx \times dz \quad (\text{mm}^3)$$
   *En nuestro caso:* En el TAC, cada píxel mide $0.3965 \times 0.3965\text{ mm}$, por lo que representa un área de $0.157\text{ mm}^2$. Con un grosor de corte de $2.44\text{ mm}$, cada vóxel es un bloque 3D de $0.383\text{ mm}^3$ de tejido humano real.
5. **Calibración radiométrica de la TAC a Unidades Hounsfield:**  
   Los archivos DICOM guardan enteros positivos por limitaciones de formatos antiguos. El header provee dos números: `RescaleSlope` (pendiente $m$) y `RescaleIntercept` (corte con el eje $b$). Se aplica la transformación lineal:
   $$\text{HU} = \text{pixel\_array} \times \text{RescaleSlope} + \text{RescaleIntercept}$$
   *Ejemplo real de nuestra TAC:* `Slope = 1.0`, `Intercept = -1024.0`. Si un vóxel de aire tiene valor numérico 24 en el array, al aplicar la fórmula: $24 \times 1.0 + (-1024.0) = -1000\text{ HU}$, recuperando su valor físico de atenuación.
6. **Anonimización Clínica:**  
   Según la norma internacional HIPAA y el estándar DICOM PS 3.15, es delito revelar la identidad de un paciente. Creamos la función `anonimizar_dicom()` que clona el dataset y sobreescribe con cadenas vacías `""` las etiquetas de identificación sensible: `PatientName`, `PatientID`, `PatientBirthDate`, `PatientSex`, `PatientAge`, `InstitutionName`, etc. Usar cadenas vacías `""` es el estándar porque evita errores de formato en fechas (`DA`) o edades (`AS`).

---

# 4. Módulo 2: Descomposición Espectral y Espacios de Color (Exclusivo Imagen Plana)

### ⚠️ La Gran Pregunta de Sustentación: ¿Por qué este módulo se aplica EXCLUSIVAMENTE a la imagen plana y NO a RM ni a TAC?
**Respuesta letal:**  
> *"Profesor, los espacios de color (Gris, YUV, HSV) existen únicamente para modelar la percepción visual tricromática humana, donde la retina tiene conos sensibles a longitudes de onda de luz roja, verde y azul. La imagen plana posee 3 canales RGB porque fue capturada por un sensor con filtro Bayer bajo luz visible.  
> Por el contrario, la Resonancia Magnética y la Tomografía son imágenes univariadas que capturan propiedades biofísicas puras (relajación electromagnética de protones y coeficiente de atenuación de rayos X). Producen un único escalar numérico por vóxel. Descomponer una RM o una TAC en canales de color sería un error conceptual gravísimo, pues allí no existe cromaticidad ni luz."*

---

### Las 3 Conversiones Desarrolladas desde Cero:

#### 1. Escala de Grises Biológica
* **Fórmula:**
  $$\text{Gris} = 0.299 \cdot R + 0.5876 \cdot G + 0.114 \cdot B$$
* **¿Por qué NO se promedia dividiendo entre 3 (`(R+G+B)/3`)?**  
  Porque el ojo humano no es una máquina uniforme. La evolución dotó a nuestra fóvea con abundantes conos tipo L y M, teniendo la máxima sensibilidad en la longitud de onda verde ($\approx 555\text{ nm}$). Somos casi ciegos al azul en comparación con el verde. Si promediáramos entre 3, la imagen se vería artificialmente oscura y desbalanceada.

#### 2. Espacio YUV (Luminancia y Crominancia)
* **Concepto:** Desacopla la energía de brillo o luz ($Y$) de la información de color ($U$ y $V$). Fue inventado históricamente para que los televisores a color pudieran transmitir una señal compatible con los televisores en blanco y negro (los cuales solo leían el canal $Y$).
* **Fórmulas Matriciales:**
  $$\begin{aligned}
  Y &= 0.299 \cdot R + 0.5876 \cdot G + 0.114 \cdot B \quad &&\text{(Luminancia / Brillo percibido)} \\
  U &= -0.147 \cdot R - 0.289 \cdot G + 0.436 \cdot B \quad &&\text{(Crominancia Azul: proporcional a } B - Y\text{)} \\
  V &= 0.615 \cdot R - 0.515 \cdot G - 0.100 \cdot B \quad &&\text{(Crominancia Rojo: proporcional a } R - Y\text{)}
  \end{aligned}$$

#### 3. Espacio HSV (Hue, Saturation, Value)
* **Concepto:** Es el modelo más intuitivo para el cerebro humano.
  * **$H$ (Hue / Matiz):** Es el tipo de color puro en un círculo cromático de $0^\circ$ a $360^\circ$ ($0^\circ=$ Rojo, $120^\circ=$ Verde, $240^\circ=$ Azul).
  * **$S$ (Saturation / Saturación):** La pureza del color de $0.0$ (gris descolorido) a $1.0$ (color vivo e intenso).
  * **$V$ (Value / Brillo):** La luminosidad general del píxel de $0.0$ (negro absoluto) a $1.0$ (máxima intensidad).
* **Fórmula a Trozos (Implementada from scratch sin OpenCV):**
  Normalizamos $r, g, b \in [0, 1]$ dividiendo por $255$. Hallamos $C_{\max} = \max(r, g, b)$, $C_{\min} = \min(r, g, b)$ y $\Delta = C_{\max} - C_{\min}$.
  $$H = \begin{cases} 
  0^\circ & \text{si } \Delta = 0 \text{ (escala de grises, no hay matiz)} \\
  60^\circ \times \left(\frac{g - b}{\Delta} \bmod 6\right) & \text{si } C_{\max} = r \\
  60^\circ \times \left(\frac{b - r}{\Delta} + 2\right) & \text{si } C_{\max} = g \\
  60^\circ \times \left(\frac{r - g}{\Delta} + 4\right) & \text{si } C_{\max} = b 
  \end{cases}$$
  Si $H < 0^\circ$, le sumamos $360^\circ$ para cerrar el círculo.  
  $$S = \begin{cases} 0 & \text{si } C_{\max} = 0 \\ \frac{\Delta}{C_{\max}} & \text{si } C_{\max} > 0 \end{cases}, \qquad V = C_{\max}$$

### ¿Qué canal elegimos para continuar el pipeline y por qué?
Para nuestro pipeline de filtrado y detección de bordes, **elegimos el canal de Gris Biológico (equivalente al canal $Y$ de YUV)**.  
*Justificación:* Los algoritmos de gradiente (Sobel, Laplaciano) buscan variaciones espaciales en la energía fotométrica. El canal de gris biológico preserva el mayor contraste anatómico y estructural con la mejor relación señal-ruido. *(Nota para el estudiante: Si el profesor preguntara "¿cuándo usarías el canal H?", respondes: "Usaría el canal H si el objetivo fuera segmentar un objeto de un color específico ignorando las sombras, porque una sombra cambia el brillo $V$ pero no altera el matiz $H$")*.

---

# 5. Módulo 3: Histograma, Curva CDF y Ecualización de Contraste

### 1. El Histograma Manual
Un histograma es una tabla de conteo de frecuencias: en el eje X colocamos los niveles de intensidad y en el eje Y cuántos píxeles de la imagen tienen esa intensidad exacta.
* **El reto en RM y TAC:** En una imagen plana hay 256 niveles ($0$ a $255$). Pero en RM los números van de $0$ a más de $10,000$, y en TAC de $-1024$ a $+2000$.  
* **Exclusión de Fondo (Filtro de Aire):** En las imágenes médicas, más del $50\%$ de la matriz es aire negro exterior al paciente. Si graficas el histograma completo, verás una barra monstruosa en el primer bin que aplasta a los tejidos cerebrales. Nuestra función implementa el parámetro `excluir_fondo=True` para analizar la distribución real de la materia gris, materia blanca y ventrículos.

### 2. La Curva CDF (Función de Distribución Acumulada)
La CDF es la suma progresiva del histograma normalizada de $0\%$ a $100\%$:
$$\text{CDF}(k) = \frac{\sum_{i=0}^k H(i)}{\text{Total de Píxeles}} \times 100\%$$
* **Cómo leer un percentil en la sustentación (OBLIGATORIO):**  
  > *"Profesor, para leer el **Percentil 80 ($P_{80}$)** en nuestra curva CDF, nos ubicamos en el $80\%$ del eje vertical (Y), trazamos una línea horizontal imaginaria hasta cortar la curva roja, y bajamos perpendicularmente al eje horizontal (X). Si el corte da en $181$, la lectura formal es:  
  > **El 80% de los píxeles de la escena poseen una intensidad igual o menor a 181 niveles.**"*

### 3. Ecualización Global vs. Ecualización Adaptativa (CLAHE manual)
* **¿Qué hace la ecualización?** Busca "estirar" y redistribuir el histograma usando la curva CDF para que las intensidades ocupen todo el rango dinámico disponible, maximizando el contraste visual.
* **El Fracaso de la Ecualización Global en Medicina:**  
  Como el aire/fondo negro tiene millones de píxeles, la CDF acumulada salta de $0\%$ a $60\%$ en un instante. La ecualización global asigna la mitad de los tonos de salida a ese aire negro. El resultado es devastador: el fondo se vuelve blanco o gris ruidoso y los tejidos cerebrales internos se "queman" (saturación total), perdiendo todo valor diagnóstico.
* **El Rescate con CLAHE Manual (Contrast Limited Adaptive Histogram Equalization):**  
  Programamos CLAHE desde cero dividiendo la imagen en una cuadrícula de bloques ($8 \times 8$ tiles):
  1. Calcula el histograma de cada bloque de forma independiente.
  2. **Clip Limit (Limitación de Contraste):** Si un tono se repite más de un umbral máximo, recorta ese pico excedente y reparte esos píxeles equitativamente entre todos los demás bins (evita que el ruido se amplifique).
  3. Calcula la CDF local de cada bloque.
  4. **Interpolación Bilineal:** En lugar de dejar bordes cuadrados feos entre bloques, calcula para cada píxel un promedio ponderado suave entre los 4 bloques vecinos.  
  *Resultado visual:* En el cerebro de RM y en el cráneo de TAC, el fondo permanece negro puro, pero el hipocampo, los ventrículos y las estructuras óseas se realzan con un contraste perfecto.

---

# 6. Módulo 4: Modelamiento Estocástico del Ruido por ROI y Pruebas KS

### ¿Por qué NO se modela el ruido sobre toda la imagen?
Si tomas toda la imagen para calcular estadísticas de ruido, la varianza estará dominada por los bordes entre el cerebro y el cráneo. Estarías midiendo la anatomía, no el ruido del instrumento.  
*La Solución:* Extraer una submatriz pequeña ($50 \times 50$ píxeles) llamada **ROI (Región de Interés)** en una zona completamente lisa y sin bordes:
* En la Imagen Plana: Una sección uniforme de la pared del fondo.
* En RM y TAC: La esquina superior izquierda $[0:50, 0:50]$ de puro aire vacío donde idealmente debería haber silencio numérico absoluto.

### Los 4 Momentos Estadísticos del Ruido
1. **Media ($\mu$):** Nivel promedio de corriente oscura o valor base.
2. **Varianza ($\sigma^2$) y Desviación Estándar ($\sigma$):** La potencia o energía de dispersión del ruido alrededor de la media.
3. **Asimetría (*Skewness* $\gamma_1$):** Mide la simetría de la campana.  
   * $\gamma_1 = 0$: Perfectamente simétrica como la Gaussiana.
   * $\gamma_1 > 0$: Cola alargada hacia la derecha (valores altos poco frecuentes).
4. **Curtosis de Fisher (*Kurtosis* $\gamma_2$):** Mide qué tan puntiagudo es el pico central comparado con una distribución normal pura (donde vale $0.0$).
   * $\gamma_2 > 0$ (Leptocúrtica): Pico muy empinado y colas pesadas con valores atípicos.
   * $\gamma_2 < 0$ (Platicúrtica): Campana aplanada con hombros anchos.

### La Física del Ruido según el Hardware del Sensor
* **Imagen Plana $\implies$ Ruido Gaussiano (Normal):**  
  En un sensor fotográfico CMOS/CCD, los electrones vibran aleatoriamente por la temperatura (efecto térmico Johnson-Nyquist) y por el amplificador analógico-digital. Esta suma de millones de perturbaciones aleatorias independientes converge, por el Teorema del Límite Central, en una **distribución Gaussiana**.
* **Resonancia Magnética $\implies$ Ruido de Rayleigh / Rice:**  
  La RM captura dos señales de radio desfasadas $90^\circ$ llamadas en fase ($I$) y en cuadratura ($Q$). Ambas señales sufren ruido térmico gaussiano independiente. La imagen final de magnitud se reconstruye mediante la raíz cuadrada de la suma de cuadrados:
  $$M = \sqrt{I^2 + Q^2}$$
  En el fondo negro exterior (donde no hay tejido ni señal biológica: $I \approx 0, Q \approx 0$), la magnitud de dos gaussianas ortogonales se convierte matemáticamente en una **distribución de Rayleigh**. Cuando hay tejido con señal fuerte, pasa a llamarse **distribución de Rice**.
* **Tomografía Computarizada $\implies$ Ruido de Poisson:**  
  Los rayos X no son un flujo continuo, sino un bombardeo de partículas discretas llamadas fotones. La probabilidad de que un número entero discreto de fotones impacte un detector en un intervalo de tiempo sigue un proceso estocástico cuántico de **conteo de Poisson**.

### La Prueba de Bondad de Ajuste Kolmogorov-Smirnov (KS-Test)
Usamos `scipy.stats.kstest` para comparar formalmente el histograma de nuestro ROI contra la fórmula matemática teórica (Gauss, Rayleigh, Poisson).
* **Criterio de Decisión Clínica:** Se fija un nivel de significancia de $\alpha = 0.05$.
  * Si **$p\text{-value} > 0.05$**: **No se rechaza la hipótesis nula**. Los datos empíricos del sensor coinciden con el modelo físico teórico del hardware.
  * Si **$p\text{-value} \le 0.05$**: Se rechaza la distribución estricta pura.  
  *(Pregunta de sustentación: ¿Por qué en nuestras imágenes médicas reales el p-value a veces es muy pequeño? Respuesta: "Porque los escáneres hospitalarios modernos aplican internamente filtros de cuantización en enteros y algoritmos de retroproyección filtrada convolutiva que alteran ligeramente la pureza estocástica del ruido crudo")*.

---

# 7. Módulo 5: Motor de Convolución 2D y Filtros de Paso Bajo (Suavizado)

### ¿Qué es la Convolución Discreta 2D?
Es una operación donde tomas una ventanita pequeña con pesos numéricos (llamada **kernel** o máscara de $N \times N$, donde $N$ debe ser impar para que tenga un centro exacto, ej. $3\times 3, 5\times 5$) y la deslizas píxel por píxel sobre toda la imagen. En cada posición, multiplicas cada vecino por su peso correspondiente, sumas todo y colocas el resultado en el píxel central.

### ¿Cómo está programada nuestra función `convolucion()`?
Cumple el 100% de la exigencia del profesor mediante **4 ciclos `for` anidados**:
```python
# Ciclos 1 y 2: Recorren cada fila (i) y columna (j) de la imagen
for i in range(H_out):
    for j in range(W_out):
        suma_acumulada = 0.0
        # Ciclos 3 y 4: Recorren cada fila (u) y columna (v) del kernel
        for u in range(Kh):
            for v in range(Kw):
                suma_acumulada += imagen_pad[i + u, j + v] * kernel_flip[u, v]
        imagen_salida[i, j] = np.floor(suma_acumulada)
```
* **Padding Espejo (Reflexión):** Si pones un kernel $3\times 3$ en la esquina de una imagen, se "cae" por fuera porque le faltan vecinos. Si usas ceros (*zero-padding*), creas un borde negro artificial espantoso. Nuestra función `aplicar_padding_espejo()` refleja los píxeles de los extremos como si fueran un espejo con grosor $\lfloor N/2 \rfloor$, manteniendo las dimensiones originales intactas ($H \times W$).
* **Truncamiento a Entero:** Como las intensidades digitales representan cuantos de energía discretos, se aplica la función piso `np.floor()`.

---

### Los Tres Filtros de Suavizado:

#### 1. Filtro Promedio (Media)
Kernel cuadrado donde todas las celdas valen lo mismo: $1 / (N^2)$ (ej. en $3\times 3$, cada celda vale $1/9 \approx 0.111$). Suaviza rápido, pero borra los bordes de manera tosca y deja un efecto "borroso cuadrado".

#### 2. Filtro Gaussiano 2D
Evalúa la campana de Gauss bidimensional continua centrada en el origen $(0,0)$:
$$G(x, y) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)$$
*Los vecinos cercanos tienen pesos altos; los vecinos lejanos tienen pesos casi nulos.*
* **⚠️ REGLA CRÍTICA DE NORMALIZACIÓN (Pregunta de Sustentación):**  
  Al muestrear una campana gaussiana en una rejilla discreta pequeña (ej. $3\times 3$ con $\sigma=1.0$), la suma de sus 9 celdas da $\approx 0.779$, ¡no da 1.0! Si no normalizas, cada vez que aplicas la convolución estarías multiplicando la imagen por $0.78$, haciendo que se oscurezca artificialmente. Es **obligatorio** dividir cada celda entre `np.sum(kernel)` para garantizar que la suma total sea exactamente $1.0$ (ganancia unitaria, no altera el brillo global).

#### 3. El Experimento Obligatorio de Hiperparámetros Gaussianos (Rúbrica)
Evaluamos una cuadrícula cruzando 3 tamaños de kernel ($3\times 3, 5\times 5, 7\times 7$) contra 3 valores de sigma ($\sigma \in \{0.5, 1.0, 2.0\}$):
* **$\sigma = 0.5$ (Campana muy empinada):** Más del $60\%$ del peso queda en el píxel central. Casi no suaviza el ruido.
* **$\sigma = 1.0$ y kernel $3\times 3$ (Punto Dulce ÓPTIMO):** Suaviza el ruido de fondo eficazmente pero conserva los bordes nítidos.
* **$\sigma = 2.0$ y kernel $7\times 7$ (Campana muy aplanada / Sobresuavizado):** Promedia violentamente con vecinos a 3 píxeles de distancia. Reduce muchísimo la varianza del ruido, pero **destruye los bordes y fusiona microestructuras cerebrales**.  
  *(Metáfora de sustentación: Las estructuras del sistema límbico, como el hipocampo y la amígdala, son como las pepitas diminutas de una mora; un sigma de 2.0 aplasta la mora y la convierte en mermelada homogénea, haciendo imposible su segmentación diagnóstica)*.

#### 4. Filtro de la Mediana (No Lineal)
No usa convolución. Toma la vecindad de $3\times 3$ (9 píxeles), los ordena de menor a mayor y coloca en el centro el valor de la posición central (la mediana).
* **¿Por qué supera a los filtros lineales en imágenes médicas?**  
  Porque no promedia números. Si hay un píxel quemado por ruido de sal y pimienta ($0$ o $65535$), el promedio lo arrastra y crea un parche borroso; la mediana simplemente manda ese píxel extremo al final de la fila y toma el valor del tejido real. Además, **preserva los bordes en escalón con perfecta nitidez**.

---

# 8. Módulo 6: Filtros Diferenciales de Paso Alto (Detección de Bordes)

### ⚠️ Regla de Oro de la Sustentación:
> **Los filtros de detección de bordes NUNCA se aplican sobre la imagen original ruidosa, SIEMPRE se aplican sobre la imagen previamente suavizada en el Módulo 5.**

*¿Por qué?* Porque matemáticamente la derivada espacial es un filtro de paso alto que multiplica las frecuencias proporcionales a $\omega$. Si derivas una imagen ruidosa, amplificas el ruido de alta frecuencia hasta el infinito, y tu detector de bordes reportará millones de bordes falsos en el aire y en el fondo homogéneo.

---

### 1. Operador de Sobel (Primera Derivada / Gradiente)
Aplica dos kernels de $3\times 3$ desacoplados usando nuestra función `convolucion()`:
$$K_h = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix} \implies G_x \quad (\text{Bordes verticales: diferencia izquierda-derecha})$$
$$K_v = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix} \implies G_y \quad (\text{Bordes horizontales: diferencia arriba-abajo})$$
* **Magnitud del Gradiente (Fuerza del borde en cualquier dirección):**
  $$M = \sqrt{G_x^2 + G_y^2}$$
* **Dirección del Gradiente (Ángulo ortogonal al borde):**
  $$\theta = \arctan2(G_y, G_x) \quad (\text{en grados } [-180^\circ, +180^\circ])$$
  Nos dice hacia dónde apunta la máxima variación de brillo (útil en visión artificial para seguir trayectorias de bordes).

### 2. Operador Laplaciano (Segunda Derivada / Series de Taylor)
Mide la curvatura o segunda derivada escalar:
$$\nabla^2 I = \frac{\partial^2 I}{\partial x^2} + \frac{\partial^2 I}{\partial y^2}$$
Aproximada por series de Taylor discretas:
* **Kernel de 4 Vecinos:** $\begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$ (evalúa solo vecinos cardinales: arriba, abajo, izq, der).
* **Kernel de 8 Vecinos:** $\begin{bmatrix} 1 & 1 & 1 \\ 1 & -8 & 1 \\ 1 & 1 & 1 \end{bmatrix}$ (agrega las diagonales, logrando una respuesta más isotrópica e independiente de la orientación).
* **Kernel Paramétrico $\alpha$:** Permite ajustar mediante un factor continuo $\alpha \in [0, 1]$ el peso entre diagonales y cardinales.
* **Propiedad en Sustentación:** Mientras Sobel genera un único pico ancho en el borde, el Laplaciano genera un cruce por cero (un pico positivo seguido de un valle negativo), lo que permite localizar el centro del borde con precisión subpíxel.

---

# 9. Módulo 7: Operadores Basados en la Varianza Local (Detección sin Convolución)

### ¿Cómo funciona la detección de bordes por varianza local?
A diferencia de Sobel y Laplaciano (que son operadores lineales basados en sumas ponderadas con signos negativos), este detector es **estadístico no lineal**.
1. Desliza una ventanita de $N \times N$ (ej. $3\times 3$) sobre la imagen suavizada.
2. Calcula la varianza estadística $\sigma^2$ (segundo momento central) de los píxeles contenidos dentro de esa ventana:
   $$\sigma^2 = \frac{1}{N^2} \sum_{k=1}^{N^2} (x_k - \mu)^2$$
3. Asigna al píxel central el valor transformado por la función acotada vista en clase:
   $$R = 1 - \frac{1}{1 + \sigma^2}$$
4. Multiplica por $255.0$ para generar la imagen visualizable.

### Comportamiento Matemático y Asintótico:
* **En una región homogénea (pared lisa, fondo de aire, interior de un ventrículo):**  
  Todos los píxeles vecinos valen casi lo mismo $\implies$ La varianza local es prácticamente cero ($\sigma^2 \approx 0$).  
  $$R = 1 - \frac{1}{1 + 0} = 1 - 1 = \mathbf{0} \quad \implies \text{Negro absoluto (sin bordes).}$$
* **En un borde o transición de alto contraste (límite entre hueso y cerebro):**  
  La mitad de los vecinos son muy oscuros y la otra mitad muy brillantes $\implies$ La dispersión o varianza es enorme ($\sigma^2 \gg 0$).  
  $$\frac{1}{1 + \sigma^2} \to 0 \implies R \approx 1 - 0 = \mathbf{1} \quad \implies \text{Blanco nítido (borde detectado).}$$

### Ventaja Crucial frente a Sobel y Laplaciano (Para la Sustentación):
> *"Profesor, la gran ventaja del operador de varianza es que es **perfectamente isotrópico por construcción** (no depende de una dirección X o Y como Sobel) y es **inmune al signo del gradiente**: da exactamente la misma respuesta si pasas de negro a blanco que si pasas de blanco a negro, sin cancelar energía por desfases de signo."*

---

# 10. Banco de Preguntas Típicas y Respuestas Letales para la Sustentación Oral

Aquí tienes las 15 preguntas más frecuentes con las que los profesores evalúan si el estudiante realmente entiende el código o si solo copió y pegó:

#### 1. ¿Por qué la convolución se programa con 4 bucles for y no con 2?
**Respuesta:** Porque una imagen es una matriz bidimensional (2 bucles para recorrer todas las filas y columnas donde depositamos el resultado) y el kernel es otra matriz bidimensional (otros 2 bucles para recorrer los vecinos locales multiplicando cada píxel por su peso de la máscara). $2 + 2 = 4$ bucles.

#### 2. ¿Por qué se invierte el kernel (`np.flipud(np.fliplr(kernel))`) antes de convolucionar?
**Respuesta:** Porque formalmente, por definición matemática, la convolución continua es $f(t) * g(t) = \int f(\tau) g(t - \tau) d\tau$. Ese signo menos en $\tau$ implica que el kernel debe estar invertido espacialmente (efecto espejo vertical y horizontal). Si no se invierte, la operación se llama *correlación cruzada*, no convolución. (Aunque en kernels simétricos como el Gaussiano o Laplaciano da igual porque son idénticos a su reflejo, en Sobel el signo sí importa).

#### 3. ¿Por qué no usamos `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`?
**Respuesta:** Porque la regla de oro del curso exige programación algorítmica desde cero (*from scratch*) para comprender la sensibilidad espectral biológica del ojo humano ($0.299R + 0.5876G + 0.114B$). Usar librerías caja negra anula la validez del laboratorio.

#### 4. ¿Por qué las imágenes médicas no se convirtieron a 8 bits al inicio?
**Respuesta:** Porque la pantalla solo puede desplegar 256 niveles, pero el hardware médico adquiere 16 bits crudos (RM) o Unidades Hounsfield de $-1024$ a $+2000$ (TAC). Si comprimimos a 8 bits antes de procesar, colapsamos decenas de densidades anatómicas distintas en un solo número entero, destruyendo bordes finos que diferencian patologías. Las operaciones matemáticas se realizan sobre el tipo numérico real y solo se mapea a la pantalla al invocar `plt.imshow()`.

#### 5. ¿Qué significa físicamente que un vóxel en TAC tenga un valor de $-1000\text{ HU}$?
**Respuesta:** Significa que ese vóxel está ocupado por aire (baja densidad molecular), el cual prácticamente no atenúa los rayos X. El valor $0\text{ HU}$ representa el agua pura destilada, y valores superiores a $+1000\text{ HU}$ representan hueso compacto o calcio denso.

#### 6. ¿Qué ocurre si no normalizo el kernel Gaussiano dividiendo por su suma?
**Respuesta:** Como el kernel discreto (ej. $3\times 3$ con $\sigma=1.0$) suma aproximadamente $0.779$, cada convolución multiplicaría la energía global de la imagen por un factor menor a 1, atenuando la ganancia y oscureciendo progresivamente la escena. La normalización garantiza ganancia unitaria ($\sum K = 1.0$).

#### 7. ¿Por qué la ecualización de histograma global fracasa en la Resonancia Magnética?
**Respuesta:** Porque el fondo negro de aire representa más del $50\%$ del área total de la imagen. Esto genera un pico gigantesco en el nivel cero del histograma, provocando que la función de distribución acumulada (CDF) salte abruptamente al inicio. La ecualización global asigna casi toda la escala dinámica de salida a estirar el fondo, quemando y saturando los tejidos cerebrales internos. Por eso se requiere CLAHE adaptativo local.

#### 8. ¿Cómo lee usted el Percentil 80 en la gráfica de la CDF?
**Respuesta:** *"Trazamos una línea horizontal en el $80\%$ del eje Y, buscamos la intersección con la curva acumulada de la CDF y bajamos verticalmente al eje X. Si el valor es $181$, significa rigurosamente que el $80\%$ de los píxeles de toda la imagen poseen una intensidad igual o menor a 181 niveles."*

#### 9. ¿Por qué en la prueba de ruido en RM esperamos una distribución de Rayleigh y no Gaussiana?
**Respuesta:** Porque la imagen de RM se reconstruye calculando la magnitud euclidiana de dos canales ortogonales en cuadratura ($M = \sqrt{I^2 + Q^2}$). En el fondo negro no hay tejido ni señal de radiofrecuencia, por lo que $I$ y $Q$ son dos variables aleatorias Gaussianas puras de media cero. La raíz cuadrada de la suma de dos variables gaussianas al cuadrado sigue matemáticamente una distribución de Rayleigh.

#### 10. ¿Por qué el ruido de Tomografía sigue una distribución de Poisson?
**Respuesta:** Porque la tomografía funciona mediante la emisión y absorción de partículas cuánticas discretas (fotones de rayos X). El conteo de partículas discretas emitidas por unidad de tiempo en física cuántica es un proceso estocástico puro de Poisson.

#### 11. ¿Cuál es la diferencia entre el filtro de la media y el filtro de la mediana?
**Respuesta:** La media es un filtro lineal que promedia todos los valores vecinos; es muy vulnerable a valores atípicos (ruido impulsivo) y difumina fuertemente los bordes. La mediana es un filtro no lineal de ordenamiento estadístico: toma el valor central de la lista ordenada de vecinos, por lo que ignora completamente los valores extremos de sal y pimienta y preserva los bordes escalón con absoluta nitidez.

#### 12. ¿Por qué en el experimento de hiperparámetros no escogemos simplemente el kernel más grande con el mayor sigma posible para eliminar todo el ruido?
**Respuesta:** Porque existe un compromiso fundamental (*trade-off*): a mayor tamaño de kernel y mayor sigma, se reduce la varianza del ruido pero se destruye la resolución espacial de los bordes. En medicina, un sigma excesivo fusionaría las circunvoluciones del hipocampo y la amígdala (que son microestructuras tipo pepitas de mora), imposibilitando su delimitación diagnóstica.

#### 13. ¿Qué información nos aporta el cálculo de `np.arctan2(Gy, Gx)` en Sobel?
**Respuesta:** Nos da la dirección angular $\theta$ del vector gradiente en grados o radianes. Este ángulo indica la dirección de máxima variación de intensidad, la cual es exactamente perpendicular (ortogonal) a la frontera o borde físico del objeto.

#### 14. ¿Cuál es la diferencia matemática entre el operador de Sobel y el Laplaciano?
**Respuesta:** Sobel aproxima la primera derivada (un vector con magnitud y dirección), produciendo un máximo de energía centrado en el borde. El Laplaciano es la segunda derivada escalar ($\nabla^2 I$), produciendo una transición que pasa por cero (cruce por cero) entre un pico positivo y uno negativo, lo que permite ubicar bordes delgados de un píxel de grosor.

#### 15. ¿Cómo funciona el operador de detección de bordes basado en la varianza local?
**Respuesta:** Recorre la imagen con una ventana deslizante y calcula la varianza local $\sigma^2$. En zonas planas u homogéneas la varianza es cercana a cero y la fórmula $R = 1 - \frac{1}{1 + \sigma^2}$ da cero (negro). En las fronteras entre tejidos la dispersión es muy alta ($\sigma^2 \gg 0$), la fracción tiende a cero y $R$ tiende a 1 (blanco). Es un operador isotrópico e independiente del signo del contraste.

---

# 11. Guía de Ejecución Rápida en VS Code / Jupyter

1. Abre tu terminal en la carpeta del proyecto y activa el entorno:
   ```bash
   source .venv/bin/activate
   ```
2. Abre VS Code en la carpeta del proyecto:
   ```bash
   code .
   ```
3. En la barra lateral izquierda, abre:
   * [control1/notebooks/prueba1.ipynb](file:///home/joseph-herrera/Documentos/Procesamiento_Imagenes/control1/notebooks/prueba1.ipynb) o [control1/notebooks/Control_1_PDI.ipynb](file:///home/joseph-herrera/Documentos/Procesamiento_Imagenes/control1/notebooks/Control_1_PDI.ipynb).
4. En la esquina superior derecha del notebook en VS Code, asegúrate de seleccionar el kernel:
   * **`Python (.venv)`** o **`Python (PDI Control 1)`**.
5. Haz clic en **"Run All"** (Ejecutar todo) o avanza celda por celda usando `Shift + Enter`.
   * Todo el pipeline se ejecuta en menos de 15 segundos.
   * Todas las salidas gráficas, histogramas con CDF, tablas comparativas y métricas de ruido se desplegarán inmediatamente en pantalla de manera impecable para tu sustentación.

