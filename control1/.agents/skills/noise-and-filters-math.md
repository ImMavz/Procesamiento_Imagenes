---
name: noise-and-filters-math
description: Formulación matemática exacta para modelamiento de ruido por ROI, normalización de kernels gaussianos, detección de bordes y operadores de varianza.
---

# Matemática de Ruido y Filtrado Espacial

1. **Modelamiento Estadístico del Ruido en ROI Homogénea:**
   - Para modelar el ruido, NUNCA uses la imagen completa. Recorta una submatriz pequeña (`20x20` a `50x50`) en una zona sin bordes ni texturas (pared lisa en foto plana; esquina superior izquierda `0:50, 0:50` de puro aire negro en RM y TAC).
   - Evalúa asimetría (`skew`), curtosis (`kurtosis`) y aplica la prueba de Kolmogorov-Smirnov (`scipy.stats.kstest`).
   - Criterio estadístico: Si `p-value > 0.05`, los datos siguen la distribución evaluada; si `p-value <= 0.05`, se rechaza.
   - Distribuciones esperadas por hardware:
     - Cámara convencional -> **Gaussiana (Normal)**.
     - Resonancia Magnética -> **Rayleigh / Rician** (raíz de la suma de cuadrados de 2 señales).
     - Tomografía (TAC) -> **Poisson** (conteo de fotones).

2. **Construcción y Normalización de Filtros de Paso Bajo (Suavizado):**
   - **Media:** Matriz $N \times N$ donde cada valor es $1 / N^2$.
   - **Gaussiano 2D:** Evaluar en coordenadas cartesianas centradas en `(0,0)`:
     $$G(x,y) = \frac{1}{2\pi\sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)$$
     **REGLA CRÍTICA:** La suma de la rejilla discreta no da 1 (ej. en 3x3 con $\sigma=1$ suma $\approx 0.779$). Es OBLIGATORIO dividir cada elemento del kernel entre `np.sum(kernel)` para que sume exactamente `1.0` y no oscurezca la imagen.
   - **Mediana (No lineal):** No usa convolución. Ordena los $N \times N$ vecinos y reemplaza el centro por el valor mediano.

3. **Filtros de Paso Alto (Detección de Bordes):**
   - Aplicar SIEMPRE sobre la imagen previamente suavizada (nunca sobre la imagen ruidosa original).
   - **Sobel:** Aplicar por separado $K_h = [[-1,0,1],[-2,0,2],[-1,0,1]]$ y $K_v = [[-1,-2,-1],[0,0,0],[1,2,1]]$. Calcular:
     - Magnitud: $M = \sqrt{G_x^2 + G_y^2}$
     - Dirección (en grados o radianes): $\theta = \arctan2(G_y, G_x)$
   - **Laplaciano:** Basado en series de Taylor de segunda derivada. Implementar kernel básico `[[0,1,0],[1,-4,1],[0,1,0]]`, kernel de 8 vecinos `[[1,1,1],[1,-8,1],[1,1,1]]` y versión parametrizada con factor $\alpha$.

4. **Operador Basado en la Varianza (Sin Convolución):**
   - En cada vecindario $N \times N$, calcular la varianza estadística $\sigma^2$ de los píxeles vecinos y asignar al centro:
     $$R = 1 - \frac{1}{1 + \sigma^2}$$
   - Donde zonas homogéneas ($\sigma^2 = 0$) dan $R = 0$ (negro) y bordes de alto contraste ($\sigma^2 \to \infty$) tienden a $R = 1$. Multiplicar por el rango visual (`255`) para graficar.