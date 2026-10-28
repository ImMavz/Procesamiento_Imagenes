"""
Módulo 6: Filtros Espaciales de Paso Alto (Detección de Bordes).
Operadores de Sobel (Gradiente y Dirección) y Laplaciano (Segunda Derivada / Taylor).
REGLA: Aplicar SIEMPRE sobre la imagen previamente suavizada para evitar amplificar el ruido.
"""

import numpy as np
from src.modulo5_convolution_filters import convolucion


def aplicar_sobel(imagen_suavizada: np.ndarray, recuperar_bordes: bool = True) -> dict[str, np.ndarray]:
    """
    Operador Diferencial de Sobel (Primera Derivada Discreta).
    Aplica kernels desacoplados para aproximar los gradientes direccionales:
        Kh = [[-1,  0,  1],
              [-2,  0,  2],
              [-1,  0,  1]]   (Derivada horizontal dI/dx)
              
        Kv = [[-1, -2, -1],
              [ 0,  0,  0],
              [ 1,  2,  1]]   (Derivada vertical dI/dy)
              
    Calcula:
        - Magnitud del Gradiente: M = sqrt(Gx^2 + Gy^2)
        - Dirección del Gradiente: Theta = arctan2(Gy, Gx) (en grados [-180°, 180°])
    """
    img = imagen_suavizada.copy().astype(np.float64)
    
    # Definición de kernels de Sobel 3x3
    Kh = np.array([
        [-1.0,  0.0,  1.0],
        [-2.0,  0.0,  2.0],
        [-1.0,  0.0,  1.0]
    ], dtype=np.float64)
    
    Kv = np.array([
        [-1.0, -2.0, -1.0],
        [ 0.0,  0.0,  0.0],
        [ 1.0,  2.0,  1.0]
    ], dtype=np.float64)
    
    # Aplicar convolución manual por separado
    Gx = convolucion(img, Kh, recuperar_bordes=recuperar_bordes)
    Gy = convolucion(img, Kv, recuperar_bordes=recuperar_bordes)
    
    # Magnitud euclidiana del vector gradiente
    magnitud = np.sqrt(Gx ** 2 + Gy ** 2)
    
    # Dirección angular del gradiente (ortogonal al borde)
    direccion_rad = np.arctan2(Gy, Gx)
    direccion_deg = np.degrees(direccion_rad)
    
    return {
        'Gx': Gx,
        'Gy': Gy,
        'Magnitud': magnitud,
        'Direccion_deg': direccion_deg
    }


def aplicar_laplaciano(imagen_suavizada: np.ndarray, tipo: str = '8_vecinos', 
                       alpha: float = 0.5, recuperar_bordes: bool = True) -> np.ndarray:
    """
    Operador Laplaciano (Segunda Derivada Escalar / Aproximación por Series de Taylor):
        nabla^2(I) = d^2I/dx^2 + d^2I/dy^2
        
    Tipos de kernel implementados:
    - '4_vecinos':
        [[ 0,  1,  0],
         [ 1, -4,  1],
         [ 0,  1,  0]]
         
    - '8_vecinos':
        [[ 1,  1,  1],
         [ 1, -8,  1],
         [ 1,  1,  1]]
         
    - 'parametrico':
        Ponderado con factor alpha in [0, 1] para equilibrar diagonales y componentes cardinales:
        (1 / (1 + alpha)) * [[    alpha, 1 - alpha,     alpha],
                             [1 - alpha,        -4, 1 - alpha],
                             [    alpha, 1 - alpha,     alpha]]
    """
    img = imagen_suavizada.copy().astype(np.float64)
    
    if tipo == '4_vecinos':
        kernel = np.array([
            [0.0,  1.0, 0.0],
            [1.0, -4.0, 1.0],
            [0.0,  1.0, 0.0]
        ], dtype=np.float64)
        
    elif tipo == '8_vecinos':
        kernel = np.array([
            [1.0,  1.0, 1.0],
            [1.0, -8.0, 1.0],
            [1.0,  1.0, 1.0]
        ], dtype=np.float64)
        
    elif tipo == 'parametrico':
        factor = 1.0 / (1.0 + alpha)
        kernel = factor * np.array([
            [alpha, 1.0 - alpha, alpha],
            [1.0 - alpha, -4.0, 1.0 - alpha],
            [alpha, 1.0 - alpha, alpha]
        ], dtype=np.float64)
        
    else:
        raise ValueError(f"Tipo de Laplaciano no reconocido: {tipo}")
        
    laplaciano = convolucion(img, kernel, recuperar_bordes=recuperar_bordes)
    return laplaciano

