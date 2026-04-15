# Guía: VisualSFM + CMVS/PMVS2 en Linux

**Flujo completo de fotogrametría open-source para Linux x86_64**

---

## Requisitos

| Componente | Mínimo | Recomendado |
|---|---|---|
| SO | Ubuntu 20.04 x86_64 | Ubuntu 22.04 / 24.04 |
| RAM | 4 GB | 16 GB+ |
| GPU | Cualquiera (CPU fallback) | NVIDIA con CUDA |
| Espacio | 10 GB | 50 GB+ |
| Fotos | 20 imágenes JPG/PNG | 60–150 imágenes |

> **Nota:** VisualSFM usa CUDA si hay una GPU NVIDIA disponible. En CPU puro el proceso es más lento pero funciona.

---

## Instalación rápida

```bash
# 1. Dependencias de compilación
sudo apt-get install -y build-essential git wget unzip \
    libgtk2.0-dev freeglut3-dev libdevil-dev libglew-dev libglu1-mesa-dev

# 2. Clonar los build scripts (Moult)
git clone --depth=1 https://github.com/Moult/vsfm-linux-x86_64.git ~/VisualSFM

# 3. Descargar fuentes y compilar (~5–15 min)
cd ~/VisualSFM
make

# 4. Crear alias cómodo
echo "alias vsfm='cd ~/VisualSFM && ./visualsfm.sh'" >> ~/.bashrc
source ~/.bashrc

# 5. Abrir VisualSFM
vsfm
```

> **Nota:** El repo de Moult es un sistema de build que descarga VisualSFM desde
> `ccwu.me` y compila SiftGPU + PBA localmente. Los binarios quedan en
> `~/VisualSFM/vsfm/bin/`. Para lanzarlo siempre usa `./visualsfm.sh` desde esa
> carpeta (necesita las libs locales en `vsfm/bin/`).

O usar el script incluido:

```bash
chmod +x instalar-vsfm.sh
./instalar-vsfm.sh
```

---

## El workflow paso a paso

```
Fotos JPG/PNG
     │
     ▼
[PASO 1] VisualSFM — SfM
     Detecta puntos SIFT en cada foto
     Empareja puntos entre fotos
     Calcula posición y orientación de cada cámara
     → genera nube de puntos DISPERSA (.nvm)
     │
     ▼
[PASO 2] CMVS — Clustering
     Agrupa las imágenes en subconjuntos manejables
     Necesario cuando hay más de ~50 fotos
     → genera estructura de directorios para PMVS2
     │
     ▼
[PASO 3] genOption
     Genera el archivo de parámetros para PMVS2
     │
     ▼
[PASO 4] PMVS2 — Multi-View Stereo
     Usa los grupos de CMVS para generar
     una nube de puntos DENSA
     → genera archivos .ply (nube densa)
     │
     ▼
[PASO 5] MeshLab
     Reconstrucción de malla (Poisson)
     Limpieza y cierre de agujeros
     Texturizado
     → modelo 3D final .obj / .ply / .stl
```

---

## Uso de la interfaz gráfica (VisualSFM GUI)

### 1. Cargar imágenes

```
File → Open+ Multi Images   (seleccionar todas las fotos)
```

Las fotos aparecen en la parte inferior de la pantalla.

### 2. Detectar y emparejar características

```
SfM → Pairwise Matching → Compute Missing Match
```

Equivalente en menú: `Ctrl+M`  
El proceso buscará puntos SIFT en cada imagen y los emparejará. Puede tardar entre 2 y 20 minutos.

### 3. Reconstruir (SfM)

```
SfM → Reconstruct Sparse → Reconstruct
```

Equivalente: `Ctrl+R`  
La interfaz mostrará las cámaras orientadas (pirámides azules) y la nube dispersa.

### 4. Guardar el proyecto

```
File → Save NView Match
```

Guarda el archivo `.nvm` con todas las posiciones de cámara.

### 5. Ejecutar CMVS + PMVS2

```
SfM → Reconstruct Dense → Run CMVS/PMVS
```

Equivalente: `Ctrl+D`  
VisualSFM ejecutará CMVS y PMVS2 automáticamente. El tiempo varía de 20 minutos a varias horas.

---

## Uso desde la línea de comandos (modo batch)

```bash
# Workflow completo en un solo comando
VisualSFM sfm+cmvs /ruta/a/fotos/ proyecto.nvm

# O paso a paso:

# Solo SfM (nube dispersa)
VisualSFM sfm /ruta/a/fotos/*.jpg proyecto.nvm

# CMVS (clustering, necesario si hay >50 fotos)
cmvs proyecto.nvm/ 100   # 100 = máx. imágenes por cluster

# genOption (genera parámetros PMVS2)
genOption proyecto.nvm.cmvs/00/ 1 2 0.7 7 3
#                               ^nivel ^csize ^threshold ^wsize ^minimage

# PMVS2 (nube densa)
pmvs2 proyecto.nvm.cmvs/00/ option-0000.txt
```

O usar el script incluido:

```bash
chmod +x fotogrametria-workflow.sh
./fotogrametria-workflow.sh ./mis_fotos/ nombre_proyecto
```

---

## Parámetros clave de PMVS2

| Parámetro | Valor | Efecto |
|---|---|---|
| `level` | `0` | Máxima resolución (muy lento, mucha RAM) |
| `level` | `1` | Equilibrio calidad/velocidad **(recomendado)** |
| `level` | `2` | Rápido, menor detalle |
| `csize` | `1–4` | Tamaño de celda de muestreo (menor = más denso) |
| `threshold` | `0.7` | Consistencia fotométrica (0=permisivo, 1=estricto) |
| `wsize` | `7` | Ventana de comparación en píxeles |
| `minimage` | `3` | Mínimo de vistas para aceptar un punto |

**Perfil para fósiles pequeños (alta calidad):**
```bash
genOption carpeta/ 0 1 0.6 7 3
```

**Perfil para modelos grandes / poca RAM:**
```bash
genOption carpeta/ 2 4 0.8 7 4
```

---

## Paso 5: MeshLab (reconstrucción de malla)

Abrir el archivo `.ply` generado por PMVS2:

```
File → Import Mesh → seleccionar modelo.ply
```

### Filtros recomendados (en orden)

1. **Limpiar la nube:**
   ```
   Filters → Cleaning and Repairing → Remove Isolated pieces (wrt Face Num.)
   ```

2. **Reconstruir la malla (Poisson):**
   ```
   Filters → Remeshing → Surface Reconstruction: Screened Poisson
   Depth: 10–12 (mayor = más detalle, más lento)
   ```

3. **Cerrar agujeros:**
   ```
   Filters → Remeshing → Close Holes
   ```

4. **Simplificar (opcional):**
   ```
   Filters → Remeshing → Quadric Edge Collapse Decimation
   Percentage reduction: 0.5 (reduce a la mitad)
   ```

5. **Exportar:**
   ```
   File → Export Mesh As → .obj / .ply / .stl
   ```

---

## Solución de problemas comunes

### VisualSFM no abre / error de librerías

```bash
# Verificar librerías faltantes
ldd ~/VisualSFM/VisualSFM | grep "not found"

# Instalar lo que falte
sudo apt-get install -y libgfortran5 libgomp1 libglew2.2 libdevil1c2
```

### "CMVS command failed"

- Verificar que `cmvs`, `pmvs2` y `genOption` estén en la misma carpeta que `VisualSFM`
- Verificar permisos: `chmod +x ~/VisualSFM/cmvs ~/VisualSFM/pmvs2`

### Pocas cámaras orientadas (< 50% de las fotos)

- Las fotos tienen poco traslape → fotografiar con >60% de superposición
- Demasiado movimiento de cámara → mover la cámara en pasos pequeños
- Objeto sin textura → aplicar puntos de referencia (marcadores ArUco)

### PMVS2 genera nube muy dispersa

- Bajar `level` a `0` para máxima resolución
- Bajar `threshold` a `0.6`
- Aumentar el número de fotos (60–100 para objetos pequeños)

### Se cuelga o consume toda la RAM

- Subir `level` a `2`
- Subir `csize` a `4`
- Reducir `CMVS_MAXIMAGE` a `50`
- Cerrar otras aplicaciones

---

## Estructura de archivos de salida

```
proyecto_output/
├── proyecto.nvm              ← posiciones de cámara (SfM)
├── proyecto.nvm.cmvs/
│   └── 00/
│       ├── models/
│       │   └── option-*.ply  ← nubes densas por cluster  ← RESULTADO
│       ├── txt/              ← parámetros de cámara
│       ├── visualize/        ← imágenes reprocesadas
│       └── option-0000.txt   ← parámetros PMVS2
└── workflow.log              ← log del proceso (si se usó el script)
```

---

## Referencias

- VisualSFM (Wu, 2011): http://ccwu.me/vsfm/
- Binarios Linux x86_64 (Moult): https://github.com/Moult/vsfm-linux-x86_64
- CMVS/PMVS2 (Furukawa & Ponce, 2010): https://www.di.ens.fr/pmvs/
- MeshLab: https://www.meshlab.net/
- Tutorial de referencia (Bezděk): https://www.youtube.com/watch?v=v5p8yCZv7j8
