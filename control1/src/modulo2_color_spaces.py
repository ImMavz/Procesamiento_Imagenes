"""
Módulo 2: Descomposición Espectral y Espacios de Color.
Exclusivo para la imagen plana convencional (RGB).
Implementaciones manuales de Gris Biológico, YUV y HSV desde cero en NumPy.
"""

import numpy as np


def rgb_a_gris_biologico(img_rgb: np.ndarray) -> np.ndarray:
    """
    Convierte RGB a Escala de Grises aplicando la sensibilidad fotópica del ojo humano:
        Gris = 0.299*R + 0.5876*G + 0.114*B
    Los conos L (rojos) y M (verdes) en la retina dominan la percepción de luminancia;
    el ojo humano posee una sensibilidad máxima cerca a los 555 nm (verde).
    """
    img = img_rgb.copy().astype(np.float64)
    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]
    
    gris = 0.299 * R + 0.5876 * G + 0.114 * B
    return np.floor(gris).astype(np.uint8)


def rgb_a_yuv(img_rgb: np.ndarray) -> dict[str, np.ndarray]:
    """
    Convierte RGB al espacio YUV mediante producto matricial exacto píxel a píxel:
        [Y]   [ 0.299   0.5876   0.114 ]   [R]
        [U] = [-0.147  -0.289    0.436 ] * [G]
        [V]   [ 0.615  -0.515   -0.100 ]   [B]
        
    Y: Luminancia (energía monocromática percibida).
    U: Diferencia de croma azul (B - Y).
    V: Diferencia de croma rojo (R - Y).
    """
    img = img_rgb.copy().astype(np.float64)
    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]
    
    Y = 0.299 * R + 0.5876 * G + 0.114 * B
    U = -0.147 * R - 0.289 * G + 0.436 * B
    V = 0.615 * R - 0.515 * G - 0.100 * B
    
    return {
        'Y': Y.copy(),
        'U': U.copy(),
        'V': V.copy()
    }


def rgb_a_hsv_manual(img_rgb: np.ndarray) -> dict[str, np.ndarray]:
    """
    Convierte RGB al espacio HSV (Hue, Saturation, Value) mediante evaluación a trozos
    from scratch (vectorizada en NumPy, sin ninguna llamada a OpenCV ni skimage).
    
    Formulación matemática:
        r, g, b = R/255, G/255, B/255
        c_max = max(r, g, b), c_min = min(r, g, b), delta = c_max - c_min
        
        Matiz (H):
            Si delta == 0        -> H = 0°
            Si c_max == r        -> H = 60° * (((g - b)/delta) mod 6)
            Si c_max == g        -> H = 60° * (((b - r)/delta) + 2)
            Si c_max == b        -> H = 60° * (((r - g)/delta) + 4)
            Garantizar H en [0, 360]°
            
        Saturación (S):
            Si c_max == 0        -> S = 0
            Si c_max > 0         -> S = delta / c_max   (en [0, 1])
            
        Brillo/Valor (V):
            V = c_max                                    (en [0, 1])
    """
    img = img_rgb.copy().astype(np.float64) / 255.0
    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]
    
    # Extremos por píxel
    c_max = np.maximum(np.maximum(r, g), b)
    c_min = np.minimum(np.minimum(r, g), b)
    delta = c_max - c_min
    
    # Matrices destino
    H = np.zeros_like(c_max)
    S = np.zeros_like(c_max)
    V = c_max.copy()
    
    # Máscaras booleanas para evaluación a trozos
    mask_delta_no_cero = (delta != 0.0)
    mask_r_max = (c_max == r) & mask_delta_no_cero
    mask_g_max = (c_max == g) & mask_delta_no_cero & (~mask_r_max)
    mask_b_max = (c_max == b) & mask_delta_no_cero & (~mask_r_max) & (~mask_g_max)
    
    # 1. Cálculo de Matiz (H)
    H[mask_r_max] = 60.0 * (((g[mask_r_max] - b[mask_r_max]) / delta[mask_r_max]) % 6.0)
    H[mask_g_max] = 60.0 * (((b[mask_g_max] - r[mask_g_max]) / delta[mask_g_max]) + 2.0)
    H[mask_b_max] = 60.0 * (((r[mask_b_max] - g[mask_b_max]) / delta[mask_b_max]) + 4.0)
    H[H < 0.0] += 360.0
    
    # 2. Cálculo de Saturación (S)
    mask_cmax_pos = (c_max > 0.0)
    S[mask_cmax_pos] = delta[mask_cmax_pos] / c_max[mask_cmax_pos]
    S[~mask_cmax_pos] = 0.0
    
    return {
        'H': H.copy(),  # [0°, 360°]
        'S': S.copy(),  # [0.0, 1.0]
        'V': V.copy()   # [0.0, 1.0]
    }

