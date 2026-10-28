---
name: medical-imaging-domain
description: Manejo técnico y físico de imágenes médicas (RM y TAC), unidades Hounsfield, profundidad de 16 bits, resolución espacial y anonimización DICOM.
---

# Dominio de Imágenes Médicas (RM y TAC)

1. **Diferenciación Física y Numérica:**
   - **Imagen Plana (JPG/PNG):** Captura luz reflejada. 8 bits (`0` a `255`). 3 canales (RGB).
   - **Resonancia Magnética (RM / MRI - `.nii.gz` o `.dcm`):** Captura tiempos de eco en campos electromagnéticos (sin luz ni color). 16 bits de profundidad (`0` a `65,535` sin unidades). Ideal para tejidos blandos (corteza cerebral, sistema límbico: amígdala, hipocampo, tálamo).
   - **Tomografía Computarizada (TAC / CT - `.dcm`):** Captura atenuación de rayos X medida en **Unidades Hounsfield (HU)**. Posee valores negativos y positivos:
     - Aire: `-1000` a `-2000 HU`
     - Agua / Líquidos: `0 HU`
     - Tejido adiposo / Grasa: `-190` a `-30 HU`
     - Músculo esquelético: `-29` a `+150 HU`
     - Calcio / Hueso duro: `+100` a `+2000 HU`

2. **Prohibición de Degradación a 8 bits durante el Procesamiento:**
   - Los monitores solo muestran 8 bits (`0-255`), pero NUNCA debes convertir ni comprimir los datos crudos de RM o TAC a `0-255` para aplicarles filtros o calcular histogramas. Opera siempre sobre la matriz original en `int16`/`float64` y deja que `matplotlib` escale solo al momento de graficar (`plt.imshow`).

3. **Resolución Espacial y Vóxeles:**
   - Extrae siempre del header el espaciamiento físico (`PixelSpacing` en DICOM o `pixdim[1:4]` en NIfTI) expresado en milímetros (mm). Documenta cuánto mide en el mundo real cada píxel/vóxel para eventuales cálculos de volumen/área anatómica.

4. **Buenas Prácticas Clínicas (Anonimización):**
   - Al leer un archivo `.dcm` con `pydicom`, verifica y limpia cualquier atributo sensible del diccionario (`PatientName`, `PatientID`, `PatientBirthDate`, `PatientSex`) asignándoles `""` antes de guardar o exponer metadatos.