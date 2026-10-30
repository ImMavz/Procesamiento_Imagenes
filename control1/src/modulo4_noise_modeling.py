"""
Módulo 4: Modelamiento Estocástico del Ruido vía Histograma y Física de Sensores.
Extracción de ROI homogéneo, cálculo de momentos estadísticos y modelado estocástico.
REGLA: Prohibido scipy.stats, cv2, skimage y scipy.ndimage. Todo en pure NumPy.
"""

import numpy as np


def extraer_roi_homogenea(imagen: np.ndarray, y_min: int, y_max: int, 
                           x_min: int, x_max: int) -> np.ndarray:
    """
    Recorta una submatriz en una región homogénea sin bordes ni variaciones de textura:
    - En foto plana: pared o superficie lisa del fondo.
    - En RM y TAC: esquina de aire libre fuera del paciente (señal cercana a 0 o ~ -1000 HU).
    """
    roi = imagen[y_min:y_max, x_min:x_max].copy().astype(np.float64)
    return roi


def calcular_momentos_estadisticos(datos_roi: np.ndarray) -> dict:
    """
    Calcula los momentos estadísticos de la región homogénea usando exclusivamente NumPy:
    1. Media (mu): np.mean (tendencia central).
    2. Varianza (sigma^2): np.var (energía y dispersión cuadrática del ruido).
    3. Desviación Estándar (sigma): np.std.
    4. Asimetría (Skewness): Tercer momento estandarizado E[((X-mu)/sigma)^3].
    5. Curtosis de Fisher: Cuarto momento estandarizado E[((X-mu)/sigma)^4] - 3.0.
    """
    datos = datos_roi.flatten()
    n = len(datos)
    if n == 0:
        raise ValueError("El ROI extraído está vacío.")
        
    media = float(np.mean(datos))
    varianza = float(np.var(datos, ddof=1)) if n > 1 else 0.0
    desv_est = float(np.std(datos, ddof=1)) if n > 1 else 0.0
    
    if desv_est > 0:
        z = (datos - media) / desv_est
        skewness = float(np.mean(z**3))
        kurtosis = float(np.mean(z**4) - 3.0)
    else:
        skewness = 0.0
        kurtosis = 0.0
        
    return {
        'n': n,
        'media': media,
        'varianza': varianza,
        'desv_estandar': desv_est,
        'skewness': skewness,
        'kurtosis': kurtosis
    }


def pdf_gaussiana(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Función de densidad de probabilidad Gaussiana (Normal) en NumPy."""
    if sigma <= 0:
        return np.zeros_like(x)
    return (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def pdf_rayleigh(x: np.ndarray, sigma: float, x0: float = 0.0) -> np.ndarray:
    """Función de densidad de probabilidad Rayleigh en NumPy."""
    if sigma <= 0:
        return np.zeros_like(x)
    dx = np.maximum(x - x0, 0.0)
    return (dx / (sigma ** 2)) * np.exp(- (dx ** 2) / (2.0 * (sigma ** 2)))


def pdf_poisson_continua(x: np.ndarray, lam: float, x0: float = 0.0) -> np.ndarray:
    """Aproximación de densidad para conteo de fotones Poisson centrada en lambda."""
    if lam <= 0:
        return np.zeros_like(x)
    # Para conteo amplio de fotones, Poisson tiende a Normal(lambda, lambda)
    sigma = np.sqrt(lam)
    return pdf_gaussiana(x, lam + x0, sigma)


def caracterizar_ruido_fisico(datos_roi: np.ndarray, modalidad: str) -> dict:
    """
    Caracteriza el ruido de la ROI según la física del instrumento:
    - 'plana': Ruido térmico Gaussiano en sensor CCD/CMOS.
    - 'rmi': Ruido de Rayleigh (magnitud de señales en cuadratura en k-space con baja señal).
    - 'tac': Ruido de Poisson (fluctuaciones cuánticas en el conteo de fotones de rayos X).
    """
    stats = calcular_momentos_estadisticos(datos_roi)
    mod = modalidad.lower()
    
    if mod == 'plana':
        teorica = "Gaussiana (Normal)"
        explicacion = "Ruido térmico / Johnson-Nyquist simétrico en los fotodiodos del sensor óptico."
    elif mod in ['rmi', 'mr', 'rm']:
        teorica = "Rayleigh"
        explicacion = "Magnitud M = sqrt(I^2 + Q^2) de señales en cuadratura complejas en k-space cuando no hay señal tisular (fondo de aire)."
    elif mod in ['tac', 'ct']:
        teorica = "Poisson"
        explicacion = "Fluctuaciones en el conteo cuántico de fotones de rayos X emitidos por el tubo y capturados por los detectores."
    else:
        teorica = "Desconocida"
        explicacion = "Modalidad no tipificada."
        
    stats['distribucion_teorica'] = teorica
    stats['explicacion_fisica'] = explicacion
    return stats
