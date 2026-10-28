---
name: pdi-core-rules
description: Reglas estrictas de programación desde cero (from scratch), manejo de memoria y prohibición de librerías de alto nivel para Procesamiento Digital de Imágenes.
---

# Reglas de Implementación PDI (From Scratch)

Al generar código en Python para este proyecto, debes cumplir sin excepción las siguientes reglas:

1. **Restricción Absoluta de Librerías Caja Negra:**
   - PROHIBIDO importar o usar `cv2` (OpenCV), `skimage` (scikit-image) o `scipy.ndimage`.
   - Todo algoritmo debe implementarse explícitamente usando ciclos `for` o álgebra de matrices base con `numpy`.

2. **Protección de Datos de Entrada (Paso por Valor):**
   - En Python/NumPy, la asignación `img_nueva = img_original` hace paso por referencia y destruye los datos de entrada.
   - SIEMPRE debes clonar la matriz antes de operarla usando `img_nueva = img_original.copy()`.

3. **Motor de Convolución Manual (`convolucion`):**
   - Debe recibir `(imagen, kernel, recuperar_bordes=True)`.
   - El kernel siempre debe ser cuadrado y de dimensión impar ($N \times N$, ej. 3x3, 5x5, 7x7) para que exista una coordenada central definida.
   - Si `recuperar_bordes=False`, la imagen resultante pierde $\lfloor N/2 \rfloor$ filas arriba/abajo y $\lfloor N/2 \rfloor$ columnas a izquierda/derecha.
   - Si `recuperar_bordes=True`, aplica *padding* replicando los bordes (efecto espejo) con grosor $\lfloor N/2 \rfloor$ antes de los 4 ciclos `for` anidados (2 para recorrer la imagen, 2 para el kernel).
   - Las imágenes manejan valores enteros: aplica siempre función piso (`np.floor`) al resultado de la convolución antes de asignarlo al píxel central.

4. **Fórmulas Exactas de Espacios de Color (Solo Imágenes Planas):**
   - **Gris:** `0.299*R + 0.5876*G + 0.114*B` (nunca promediar dividiendo entre 3).
   - **YUV:** Producto matricial usando las constantes exactas:
     - `Y = 0.299*R + 0.5876*G + 0.114*B`
     - `U = -0.147*R - 0.289*G + 0.436*B`
     - `V = 0.615*R - 0.515*G - 0.100*B`
   - **HSV:** Función a trozos evaluando el máximo y mínimo de `(R, G, B)` por píxel, con `H` en grados `[0, 360]`, `S` en `[0, 1]` y `V = max(R,G,B)`.