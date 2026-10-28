"""
Módulo 3: Histograma, Función de Distribución Acumulada (CDF) y Ecualización de Contraste.
Implementación manual desde cero para imágenes de 8 bits, 16 bits (RM) y TAC (HU).
"""

import numpy as np


def calcular_histograma(imagen: np.ndarray, bins: int = 256, 
                        rango: tuple[float, float] = None, 
                        excluir_fondo: bool = False, 
                        umbral_fondo: float = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula el histograma de frecuencias absolutas desde cero.
    
    Parámetros:
        imagen: Matriz 2D de intensidades.
        bins: Cantidad de intervalos de discretización.
        rango: Tupla (min, max). Si es None, toma los extremos de la imagen.
        excluir_fondo: Si True, ignora valores <= umbral_fondo (útil para aislar cerebro en RM/TAC).
        umbral_fondo: Valor de corte para fondo negro o aire.
    Retorna:
        hist: Array 1D con las frecuencias de cada bin.
        bin_edges: Bordes de los intervalos.
    """
    img = imagen.copy().astype(np.float64).flatten()
    
    if excluir_fondo and umbral_fondo is not None:
        img = img[img > umbral_fondo]
        
    if len(img) == 0:
        return np.zeros(bins, dtype=np.int64), np.zeros(bins + 1, dtype=np.float64)
        
    val_min = float(img.min()) if rango is None else float(rango[0])
    val_max = float(img.max()) if rango is None else float(rango[1])
    
    if val_min == val_max:
        val_max += 1.0
        
    bin_width = (val_max - val_min) / bins
    bin_edges = np.linspace(val_min, val_max, bins + 1)
    
    # Asignación manual de bin a cada píxel: bin_idx = floor((val - val_min) / bin_width)
    indices = np.floor((img - val_min) / bin_width).astype(np.int64)
    # Truncar casos límite iguales a val_max en el último bin
    indices = np.clip(indices, 0, bins - 1)
    
    hist = np.zeros(bins, dtype=np.int64)
    # Conteo vectorial de frecuencias
    np.add.at(hist, indices, 1)
    
    return hist, bin_edges


def calcular_cdf(histograma: np.ndarray) -> np.ndarray:
    """
    Calcula la Función de Distribución Acumulada (CDF) normalizada en porcentaje [0%, 100%]:
        CDF[k] = (sum_{i=0}^k hist[i] / total_pixeles) * 100
    """
    hist = histograma.copy().astype(np.float64)
    total_pixeles = np.sum(hist)
    
    if total_pixeles == 0:
        return np.zeros_like(hist)
        
    cdf = np.cumsum(hist) / total_pixeles * 100.0
    return cdf


def interpolar_percentil(cdf: np.ndarray, bin_edges: np.ndarray, percentil: float) -> float:
    """
    Calcula la intensidad exacta correspondiente a un percentil dado en la CDF (0 a 100%).
    """
    # Centros de los bins
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    idx = np.searchsorted(cdf, percentil)
    if idx == 0:
        return float(bin_centers[0])
    if idx >= len(bin_centers):
        return float(bin_centers[-1])
        
    # Interpolación lineal simple entre los puntos
    c0, c1 = cdf[idx - 1], cdf[idx]
    v0, v1 = bin_centers[idx - 1], bin_centers[idx]
    if c1 == c0:
        return float(v0)
    frac = (percentil - c0) / (c1 - c0)
    return float(v0 + frac * (v1 - v0))


def ecualizar_histograma_global(imagen: np.ndarray, bins: int = 256) -> np.ndarray:
    """
    Aplica Ecualización Global de Histograma redistribuyendo las intensidades
    mediante la CDF acumulada:
        T(k) = floor( (CDF[k] - CDF_min) / (1 - CDF_min) * (L - 1) )
    Preserva el tipo y rango proporcional de la matriz de entrada.
    """
    img = imagen.copy().astype(np.float64)
    orig_min, orig_max = img.min(), img.max()
    
    if orig_max == orig_min:
        return imagen.copy()
        
    # Normalizar temporalmente a rango [0, bins - 1]
    img_norm = np.clip((img - orig_min) / (orig_max - orig_min) * (bins - 1), 0, bins - 1)
    indices = np.floor(img_norm).astype(np.int64)
    
    hist = np.zeros(bins, dtype=np.int64)
    np.add.at(hist, indices.flatten(), 1)
    
    cdf = np.cumsum(hist) / np.sum(hist)
    # Encontrar el valor mínimo no nulo de la CDF
    cdf_no_cero = cdf[cdf > 0]
    cdf_min = cdf_no_cero[0] if len(cdf_no_cero) > 0 else 0.0
    
    # Mapeo de ecualización
    denom = 1.0 - cdf_min
    if denom == 0:
        return imagen.copy()
        
    tabla_mapeo = np.round(((cdf - cdf_min) / denom) * (bins - 1))
    img_eq_norm = tabla_mapeo[indices]
    
    # Reescalar al rango físico original
    img_ecualizada = orig_min + (img_eq_norm / (bins - 1)) * (orig_max - orig_min)
    return img_ecualizada


def ecualizar_histograma_adaptativo_clahe(imagen: np.ndarray, num_bloques: int = 8, 
                                          clip_limit: float = 3.0, bins: int = 256) -> np.ndarray:
    """
    Implementación desde cero de Ecualización Adaptativa con Limitación de Contraste (CLAHE).
    Divide la matriz en una cuadrícula de bloques (tiles), limita el contraste recortando picos
    del histograma y redistribuyendo el exceso uniformemente, y luego interpola bilinealmente
    entre bloques vecinos para evitar artefactos de frontera.
    """
    img = imagen.copy().astype(np.float64)
    H, W = img.shape
    orig_min, orig_max = img.min(), img.max()
    if orig_max == orig_min:
        return imagen.copy()
        
    # Normalizar a escala discreta [0, bins - 1]
    img_d = np.clip(np.floor((img - orig_min) / (orig_max - orig_min) * (bins - 1)), 0, bins - 1).astype(np.int64)
    
    tile_h = int(np.ceil(H / num_bloques))
    tile_w = int(np.ceil(W / num_bloques))
    
    # Calcular tablas de mapeo (CDFs recortadas) para cada tile
    mapas_cdf = np.zeros((num_bloques, num_bloques, bins), dtype=np.float64)
    
    for bi in range(num_bloques):
        for bj in range(num_bloques):
            r0, r1 = bi * tile_h, min((bi + 1) * tile_h, H)
            c0, c1 = bj * tile_w, min((bj + 1) * tile_w, W)
            bloque = img_d[r0:r1, c0:c1].flatten()
            num_pixeles_tile = len(bloque)
            
            if num_pixeles_tile == 0:
                mapas_cdf[bi, bj] = np.linspace(0, bins - 1, bins)
                continue
                
            # Histograma local
            h_local = np.zeros(bins, dtype=np.float64)
            np.add.at(h_local, bloque, 1.0)
            
            # Limitación de contraste (Clip Limit)
            limite_conteo = clip_limit * (num_pixeles_tile / bins)
            exceso = np.sum(np.maximum(h_local - limite_conteo, 0.0))
            h_local = np.minimum(h_local, limite_conteo)
            # Redistribución uniforme del exceso
            h_local += exceso / bins
            
            # CDF local normalizada
            cdf_local = np.cumsum(h_local) / np.sum(h_local)
            mapas_cdf[bi, bj] = np.round(cdf_local * (bins - 1))
            
    # Interpolación Bilineal suave entre tiles
    img_out = np.zeros((H, W), dtype=np.float64)
    
    for i in range(H):
        # Coordenada flotante en la grilla de bloques
        y = (i - tile_h / 2.0) / tile_h
        y1 = int(np.floor(y))
        y2 = y1 + 1
        ay = y - y1
        y1 = max(0, min(num_bloques - 1, y1))
        y2 = max(0, min(num_bloques - 1, y2))
        
        for j in range(W):
            x = (j - tile_w / 2.0) / tile_w
            x1 = int(np.floor(x))
            x2 = x1 + 1
            ax = x - x1
            x1 = max(0, min(num_bloques - 1, x1))
            x2 = max(0, min(num_bloques - 1, x2))
            
            v = img_d[i, j]
            
            # Valores transformados en las 4 esquinas de los tiles vecinos
            val11 = mapas_cdf[y1, x1, v]
            val12 = mapas_cdf[y1, x2, v]
            val21 = mapas_cdf[y2, x1, v]
            val22 = mapas_cdf[y2, x2, v]
            
            # Interpolación bilineal
            val_interp = (1.0 - ay) * ((1.0 - ax) * val11 + ax * val12) + \
                         ay * ((1.0 - ax) * val21 + ax * val22)
                         
            img_out[i, j] = val_interp
            
    # Restaurar al rango original
    img_res = orig_min + (img_out / (bins - 1)) * (orig_max - orig_min)
    return img_res

