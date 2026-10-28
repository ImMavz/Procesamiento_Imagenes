"""
Módulo 4: Modelamiento Estocástico del Ruido vía Histograma y Pruebas de Bondad de Ajuste.
Extracción de ROI homogéneo, cálculo de momentos estadísticos y test Kolmogorov-Smirnov.
"""

import numpy as np
from scipy import stats


def extraer_roi_homogenea(imagen: np.ndarray, y_min: int, y_max: int, 
                           x_min: int, x_max: int) -> np.ndarray:
    """
    Recorta una submatriz en una región homogénea sin bordes ni variaciones de textura:
    - En foto plana: pared lisa del fondo.
    - En RM y TAC: esquina superior izquierda [0:50, 0:50] de aire libre fuera del paciente.
    """
    roi = imagen[y_min:y_max, x_min:x_max].copy().astype(np.float64)
    return roi


def calcular_momentos_estadisticos(datos_roi: np.ndarray) -> dict:
    """
    Calcula los 4 momentos estadísticos de la región homogénea:
    1. Media (mu): Primer momento central / tendencia central.
    2. Varianza (sigma^2): Segundo momento central / dispersión de energía del ruido.
    3. Asimetría (Skewness): Tercer momento estandarizado (cola hacia la derecha o izquierda).
    4. Curtosis (Kurtosis): Cuarto momento estandarizado (escarpamiento del pico vs normal).
    """
    datos = datos_roi.flatten()
    n = len(datos)
    if n == 0:
        raise ValueError("El ROI extraído está vacío.")
        
    media = float(np.mean(datos))
    varianza = float(np.var(datos, ddof=1)) if n > 1 else 0.0
    desv_est = float(np.sqrt(varianza))
    
    # Asimetría (Skewness) calculada manualmente y verificada con scipy
    if desv_est > 0:
        z = (datos - media) / desv_est
        skewness_manual = float(np.mean(z**3))
        # Curtosis de Fisher (donde la normal pura da 0.0)
        kurtosis_manual = float(np.mean(z**4) - 3.0)
    else:
        skewness_manual = 0.0
        kurtosis_manual = 0.0
        
    skew_scipy = float(stats.skew(datos))
    kurt_scipy = float(stats.kurtosis(datos))
    
    return {
        'n': n,
        'media': media,
        'varianza': varianza,
        'desv_estandar': desv_est,
        'skewness_manual': skewness_manual,
        'skewness_scipy': skew_scipy,
        'kurtosis_manual': kurtosis_manual,
        'kurtosis_scipy': kurt_scipy
    }


def evaluar_distribucion_ruido(datos_roi: np.ndarray, tipo_modalidad: str = 'plana') -> dict:
    """
    Ejecuta pruebas de bondad de ajuste Kolmogorov-Smirnov (KS-test) usando scipy.stats
    para validar la hipótesis física de distribución del ruido:
    - Imagen Plana: Ruido Gaussiano (Normal N(mu, sigma^2)).
    - Resonancia Magnética (RM): Ruido Rayleigh o Rice (módulo de dos señales gaussianas ortogonales).
    - Tomografía (TAC): Ruido de Poisson (conteo cuántico de fotones de rayos X).
    
    Criterio de decisión:
    - Si p-value > 0.05: No se rechaza la hipótesis nula (los datos provienen de dicha distribución).
    - Si p-value <= 0.05: Se rechaza la hipótesis al 95% de confianza.
    """
    datos = datos_roi.flatten().astype(np.float64)
    mu = np.mean(datos)
    std = np.std(datos, ddof=1) if len(datos) > 1 else 1.0
    
    resultados = {
        'modalidad': tipo_modalidad,
        'mu': float(mu),
        'std': float(std)
    }
    
    if tipo_modalidad == 'plana':
        # Prueba contra distribución Normal N(mu, std)
        res = stats.kstest(datos, stats.norm(loc=mu, scale=std).cdf)
        stat, p_val = res.statistic, res.pvalue
        resultados['distribucion_evaluada'] = 'Gaussiana (Normal)'
        resultados['ks_stat'] = float(stat)
        resultados['p_value'] = float(p_val)
        resultados['conforme'] = bool(p_val > 0.05)
        resultados['conclusion'] = (
            f"p={p_val:.4e} > 0.05: Los datos siguen una distribución Gaussiana."
            if p_val > 0.05 else
            f"p={p_val:.4e} <= 0.05: Se rechaza normalidad estricta (posibles colas pesadas o artefactos)."
        )
        
    elif tipo_modalidad == 'rmi':
        # En RM el fondo negro (amplitud de magnitud) sigue distribución de Rayleigh
        datos_pos = datos - np.min(datos) + 1e-5
        param_scale = float(np.sqrt(np.mean(datos_pos**2) / 2.0))
        res = stats.kstest(datos_pos, stats.rayleigh(scale=param_scale).cdf)
        stat, p_val = res.statistic, res.pvalue
        resultados['distribucion_evaluada'] = 'Rayleigh'
        resultados['ks_stat'] = float(stat)
        resultados['p_value'] = float(p_val)
        resultados['conforme'] = bool(p_val > 0.05)
        resultados['conclusion'] = (
            f"p={p_val:.4e} > 0.05: Ruido de RM validado como distribución de Rayleigh."
            if p_val > 0.05 else
            f"p={p_val:.4e} <= 0.05: Posible transición a distribución Rician debido a señal residual de baja intensidad."
        )
        
    elif tipo_modalidad == 'tac':
        # En TAC el conteo de fotones de rayos X sigue un proceso de Poisson
        datos_pos = np.round(datos - np.min(datos)).astype(int)
        lambda_est = float(np.mean(datos_pos))
        res = stats.kstest(datos_pos, stats.poisson(mu=max(lambda_est, 1e-3)).cdf)
        stat, p_val = res.statistic, res.pvalue
        resultados['distribucion_evaluada'] = 'Poisson'
        resultados['ks_stat'] = float(stat)
        resultados['p_value'] = float(p_val)
        resultados['conforme'] = bool(p_val > 0.05)
        resultados['conclusion'] = (
            f"p={p_val:.4e} > 0.05: Ruido de Tomografía validado como Poisson (conteo cuántico de fotones)."
            if p_val > 0.05 else
            f"p={p_val:.4e} <= 0.05: La reconstrucción de retroproyección filtrada convolucionó los fotones gaussianizando el ruido."
        )
        
    return resultados
