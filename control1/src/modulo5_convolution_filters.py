"""
Módulo 5: Motor Maestro de Convolución 2D y Filtros Espaciales de Paso Bajo (Suavizado).
Implementación estricta con 4 ciclos for anidados, padding espejo, normalización gaussiana
y filtro de mediana no lineal.
"""

import numpy as np


def aplicar_padding_espejo(imagen: np.ndarray, pad_size: int) -> np.ndarray:
    """
    Aplica padding por reflexión de bordes (efecto espejo) de grosor pad_size
    en las 4 fronteras de la matriz 2D.
    """
    H, W = imagen.shape
    pad_h = H + 2 * pad_size
    pad_w = W + 2 * pad_size
    
    img_pad = np.zeros((pad_h, pad_w), dtype=imagen.dtype)
    
    # 1. Copiar región central
    img_pad[pad_size:pad_size + H, pad_size:pad_size + W] = imagen
    
    # 2. Reflejar filas superior e inferior
    for p in range(pad_size):
        # Fila superior reflejada
        img_pad[pad_size - 1 - p, pad_size:pad_size + W] = imagen[p, :]
        # Fila inferior reflejada
        img_pad[pad_size + H + p, pad_size:pad_size + W] = imagen[H - 1 - p, :]
        
    # 3. Reflejar columnas izquierda y derecha (incluyendo las esquinas ya reflejadas)
    for p in range(pad_size):
        # Columna izquierda reflejada
        img_pad[:, pad_size - 1 - p] = img_pad[:, pad_size + p]
        # Columna derecha reflejada
        img_pad[:, pad_size + W + p] = img_pad[:, pad_size + W - 1 - p]
        
    return img_pad


def convolucion(imagen: np.ndarray, kernel: np.ndarray, recuperar_bordes: bool = True) -> np.ndarray:
    """
    Motor Maestro de Convolución Discreta 2D programado estrictamente from scratch
    mediante 4 ciclos 'for' anidados:
        - 2 ciclos para recorrer filas y columnas de la imagen de salida.
        - 2 ciclos para evaluar el kernel KxK en el vecindario local.
        
    Parámetros:
        imagen: Matriz 2D de entrada.
        kernel: Matriz cuadrada de dimensión impar NxN (ej. 3x3, 5x5, 7x7).
        recuperar_bordes:
            Si True: aplica padding espejo de tamano floor(N/2), conservando las dimensiones originales.
            Si False: la imagen de salida pierde floor(N/2) filas y columnas en los bordes.
    Retorna:
        Matriz resultante con la función piso (np.floor) aplicada al resultado acumulado.
    """
    img = imagen.copy().astype(np.float64)
    Kh, Kw = kernel.shape
    if Kh != Kw or (Kh % 2 == 0):
        raise ValueError("[ERROR] El kernel debe ser cuadrado y de dimensión impar (NxN).")
        
    pad = Kh // 2
    
    # Invertir el kernel espacialmente (convolución formal: f(x, y) * g(-x, -y))
    kernel_flip = np.flipud(np.fliplr(kernel)).astype(np.float64)
    
    if recuperar_bordes:
        img_trabajo = aplicar_padding_espejo(img, pad)
        H_out, W_out = img.shape
        img_salida = np.zeros((H_out, W_out), dtype=np.float64)
        
        # 4 Ciclos for anidados explícitos
        for i in range(H_out):
            for j in range(W_out):
                suma_acumulada = 0.0
                for u in range(Kh):
                    for v in range(Kw):
                        pixel_vecino = img_trabajo[i + u, j + v]
                        peso_kernel = kernel_flip[u, v]
                        suma_acumulada += pixel_vecino * peso_kernel
                img_salida[i, j] = np.floor(suma_acumulada)
                
    else:
        H_orig, W_orig = img.shape
        H_out = H_orig - 2 * pad
        W_out = W_orig - 2 * pad
        img_salida = np.zeros((H_out, W_out), dtype=np.float64)
        
        # 4 Ciclos for anidados sin padding
        for i in range(H_out):
            for j in range(W_out):
                suma_acumulada = 0.0
                for u in range(Kh):
                    for v in range(Kw):
                        pixel_vecino = img[i + u, j + v]
                        peso_kernel = kernel_flip[u, v]
                        suma_acumulada += pixel_vecino * peso_kernel
                img_salida[i, j] = np.floor(suma_acumulada)
                
    return img_salida


def generar_kernel_media(tamano: int) -> np.ndarray:
    """
    Genera un kernel promedio rectangular NxN donde cada celda vale 1 / (N^2).
    """
    if tamano % 2 == 0:
        raise ValueError("El tamaño del kernel debe ser impar.")
    peso = 1.0 / (tamano * tamano)
    return np.full((tamano, tamano), peso, dtype=np.float64)


def generar_kernel_gaussiano(tamano: int, sigma: float) -> np.ndarray:
    """
    Genera un kernel Gaussiano 2D simétrico evaluado en coordenadas cartesianas centradas en (0,0):
        G(x, y) = (1 / (2 * pi * sigma^2)) * exp(-(x^2 + y^2) / (2 * sigma^2))
        
    REGLA CRÍTICA:
    La discretización espacial de la campana en una grilla finita no suma 1.0.
    Es obligatorio normalizar dividiendo entre np.sum(kernel) para conservar la energía lumínica
    y no oscurecer la imagen.
    """
    if tamano % 2 == 0:
        raise ValueError("El tamaño del kernel debe ser impar.")
        
    radio = tamano // 2
    y, x = np.mgrid[-radio:radio + 1, -radio:radio + 1]
    
    coeficiente = 1.0 / (2.0 * np.pi * (sigma ** 2))
    exponente = -(x ** 2 + y ** 2) / (2.0 * (sigma ** 2))
    kernel = coeficiente * np.exp(exponente)
    
    # Normalización obligatoria
    suma_total = np.sum(kernel)
    kernel_normalizado = kernel / suma_total
    return kernel_normalizado


def filtro_mediana(imagen: np.ndarray, tamano: int = 3) -> np.ndarray:
    """
    Filtro de Mediana (Operador No Lineal).
    Recorre el vecindario NxN, extrae los píxeles locales, los ordena ascendentemente
    y asigna el valor mediano al píxel central.
    Excelente para eliminar ruido impulsivo (sal y pimienta) preservando bordes nítidos.
    """
    if tamano % 2 == 0:
        raise ValueError("El tamaño de vecindario debe ser impar.")
        
    img = imagen.copy().astype(np.float64)
    H, W = img.shape
    pad = tamano // 2
    img_pad = aplicar_padding_espejo(img, pad)
    
    img_salida = np.zeros((H, W), dtype=np.float64)
    idx_mediana = (tamano * tamano) // 2
    
    for i in range(H):
        for j in range(W):
            vecindario = img_pad[i:i + tamano, j:j + tamano].flatten()
            vecindario_ordenado = np.sort(vecindario)
            img_salida[i, j] = vecindario_ordenado[idx_mediana]
            
    return img_salida

