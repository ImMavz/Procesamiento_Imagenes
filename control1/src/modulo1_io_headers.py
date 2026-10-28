"""
Módulo 1: Carga de Datos, Exploración Física de Headers y Anonimización Clínica.
Manejo de imágenes planas (8 bits), Resonancia Magnética (16 bits) y Tomografía (HU).
"""

import os
import numpy as np
from PIL import Image
import pydicom
import nibabel as nib


def cargar_imagen_plana(ruta_archivo: str) -> np.ndarray:
    """
    Carga una imagen plana convencional de 8 bits por canal usando PIL.
    Si contiene canal alfa (RGBA), lo descarta para garantizar matriz RGB pura.
    
    Parámetros:
        ruta_archivo: Ruta al archivo JPG o PNG.
    Retorna:
        Matriz numpy de dimensiones (H, W, 3) y tipo uint8 (clonada).
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
        
    img_pil = Image.open(ruta_archivo)
    img_np = np.array(img_pil)
    
    # Descartar canal Alfa si la imagen es RGBA
    if img_np.ndim == 3 and img_np.shape[2] == 4:
        print("[INFO Plana] Canal Alfa detectado y descartado. Conservando solo RGB.")
        img_np = img_np[:, :, :3]
        
    if img_np.ndim != 3 or img_np.shape[2] != 3:
        raise ValueError("[ERROR] La imagen plana debe poseer 3 canales de color (RGB).")
        
    return img_np.copy()


def explorar_y_cargar_dicom(ruta_archivo: str) -> tuple[pydicom.FileDataset, np.ndarray, dict]:
    """
    Lee un archivo DICOM, extrae los metadatos de adquisición física y retorna
    el objeto dataset junto a la matriz cruda en su profundidad nativa (16 bits / HU).
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo DICOM: {ruta_archivo}")
        
    dcm = pydicom.dcmread(ruta_archivo)
    raw_array = dcm.pixel_array.copy()
    
    # Extracción de metadatos clínicos y geométricos
    filas = int(getattr(dcm, 'Rows', raw_array.shape[0]))
    columnas = int(getattr(dcm, 'Columns', raw_array.shape[1]))
    bits_alloc = int(getattr(dcm, 'BitsAllocated', 16))
    bits_stored = int(getattr(dcm, 'BitsStored', bits_alloc))
    modalidad = str(getattr(dcm, 'Modality', 'Desconocida'))
    
    # Resolución espacial (PixelSpacing en mm)
    pixel_spacing = getattr(dcm, 'PixelSpacing', [1.0, 1.0])
    dy, dx = float(pixel_spacing[0]), float(pixel_spacing[1])
    area_pixel_mm2 = dy * dx
    
    # Grosor de corte
    slice_thickness = float(getattr(dcm, 'SliceThickness', 1.0))
    volumen_voxel_mm3 = area_pixel_mm2 * slice_thickness
    
    # Factores de conversión radiométrica
    rescale_slope = float(getattr(dcm, 'RescaleSlope', 1.0))
    rescale_intercept = float(getattr(dcm, 'RescaleIntercept', 0.0))
    
    metadatos = {
        'Modalidad': modalidad,
        'Dimensiones': (filas, columnas),
        'BitsAllocated': bits_alloc,
        'BitsStored': bits_stored,
        'PixelSpacing_mm': (dy, dx),
        'AreaPixel_mm2': area_pixel_mm2,
        'SliceThickness_mm': slice_thickness,
        'VolumenVoxel_mm3': volumen_voxel_mm3,
        'RescaleSlope': rescale_slope,
        'RescaleIntercept': rescale_intercept,
        'RangoCrudo': (int(raw_array.min()), int(raw_array.max()))
    }
    
    return dcm, raw_array, metadatos


def convertir_tac_a_hu(raw_array: np.ndarray, rescale_slope: float, rescale_intercept: float) -> np.ndarray:
    """
    Aplica la calibración radiométrica de Rayos X para transformar intensidades de
    almacenamiento a Unidades Hounsfield (HU) reales:
        HU = ValorPixel * RescaleSlope + RescaleIntercept
    Retorna la matriz en float64 para preservar números negativos y valores de atenuación.
    """
    img_hu = (raw_array.astype(np.float64) * rescale_slope) + rescale_intercept
    return img_hu.copy()


def anonimizar_dicom(dcm_dataset: pydicom.FileDataset) -> pydicom.FileDataset:
    """
    Protocolo de Desidentificación Clínica según norma HIPAA / DICOM PS 3.15.
    Limpia etiquetas con información de salud protegida (PHI) asignándoles cadena vacía ""
    para cumplir rigurosamente con los Value Representations (VR) de DICOM (DA, AS, PN, etc.).
    """
    dcm_anon = dcm_dataset.copy()
    
    tags_sensibles = [
        'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
        'PatientAge', 'PatientWeight', 'PatientAddress', 'InstitutionName',
        'InstitutionalDepartmentName', 'ReferringPhysicianName',
        'PerformingPhysicianName', 'OperatorsName', 'StudyID',
        'AccessionNumber', 'OtherPatientIDs'
    ]
    
    for tag in tags_sensibles:
        if tag in dcm_anon:
            setattr(dcm_anon, tag, "")
            
    return dcm_anon


def cargar_corte_nifti(ruta_archivo: str, corte_idx: int = None) -> tuple[np.ndarray, dict]:
    """
    Carga un volumen NIfTI (.nii o .nii.gz) e inspecciona su header para extraer
    la resolución espacial nativa (pixdim) y seleccionar un corte axial representativo.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo NIfTI: {ruta_archivo}")
        
    nii = nib.load(ruta_archivo)
    hdr = nii.header
    volumen = nii.get_fdata().copy()
    
    # pixdim: [0]=qfac, [1]=dx, [2]=dy, [3]=dz (en milímetros)
    pixdim = hdr['pixdim']
    dx, dy, dz = float(pixdim[1]), float(pixdim[2]), float(pixdim[3])
    
    if corte_idx is None:
        corte_idx = volumen.shape[2] // 2
        
    corte_2d = volumen[:, :, corte_idx].copy()
    
    metadatos = {
        'DimensionVolumen': volumen.shape,
        'CorteSeleccionado': corte_idx,
        'Resolucion_mm': (dx, dy, dz),
        'VolumenVoxel_mm3': dx * dy * dz,
        'RangoIntensidad': (float(corte_2d.min()), float(corte_2d.max()))
    }
    
    return corte_2d, metadatos
