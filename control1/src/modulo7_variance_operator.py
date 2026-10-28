"""
Módulo 7: Operadores Estadísticos Locales (Detección de Bordes sin Convolución).
Implementación del Operador Basado en la Varianza Local:
    R = 1 - (1 / (1 + sigma^2))
"""

import numpy as np
from src.modulo5_convolution_filters import aplicar_padding_espejo


def detector_bordes_varianza(imagen_suavizada: np.ndarray, tamano_ventana: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """
    Detector de bordes estadístico no lineal basado en la varianza local (sin convolución).
    
    Fundamento matemático:
    - En regiones homogéneas (sin bordes), la varianza local sigma^2 es cercana a 0,
      por lo que R = 1 - 1/(1 + 0) = 0 (negro).
    - En bordes o transiciones de alta energía, la varianza local sigma^2 >> 0,
      por lo que 1/(1 + sigma^2) -> 0 y R -> 1 (blanco).
      
    Parámetros:
        imagen_suavizada: Matriz 2D previamente filtrada para mitigar varianza por ruido.
        tamano_ventana: Dimensión impar de la ventana deslizante (NxN, típicamente 3x3).
    Retorna:
        R_normalizado: Matriz con valores en rango continuo [0.0, 1.0].
        R_visual: Matriz reescalada a [0, 255] para visualización y comparación de bordes.
    """
    if tamano_ventana % 2 == 0:
        raise ValueError("El tamaño de la ventana debe ser impar.")
        
    img = imagen_suavizada.copy().astype(np.float64)
    H, W = img.shape
    pad = tamano_ventana // 2
    
    img_pad = aplicar_padding_espejo(img, pad)
    R_norm = np.zeros((H, W), dtype=np.float64)
    
    for i in range(H):
        for j in range(W):
            vecindad = img_pad[i:i + tamano_ventana, j:j + tamano_ventana]
            # Varianza local (segundo momento central)
            var_local = np.var(vecindad)
            # Función no lineal acotada en [0, 1)
            R_norm[i, j] = 1.0 - (1.0 / (1.0 + var_local))
            
    R_visual = np.clip(R_norm * 255.0, 0.0, 255.0).astype(np.uint8)
    return R_norm, R_visual

