#!/usr/bin/env bash
# ============================================================
# fotogrametria-workflow.sh
# Workflow completo: VisualSFM SfM → CMVS → PMVS2
# Uso:  ./fotogrametria-workflow.sh <carpeta_de_fotos> [nombre_proyecto]
# ============================================================
set -e

# ---------- configuración ----------
VSFM_DIR="${VSFM_DIR:-$HOME/VisualSFM}"   # ruta a los binarios
VSFM="$VSFM_DIR/VisualSFM"
CMVS="$VSFM_DIR/cmvs"
PMVS="$VSFM_DIR/pmvs2"
GENOPTION="$VSFM_DIR/genOption"

# parámetros CMVS/PMVS2
CMVS_MAXIMAGE=100   # máx. imágenes por cluster (bajar si hay poca RAM)
PMVS_LEVEL=1        # 0=máxima resolución (lento), 1=media, 2=baja
PMVS_CSIZE=2        # tamaño de celda de muestra
PMVS_THRESHOLD=0.7  # umbral de consistencia fotométrica (0-1)
PMVS_WSIZE=7        # ventana de comparación (píxeles)
PMVS_MINIMAGE=3     # mínimo de vistas que deben ver un punto
# -----------------------------------

usage() {
    echo "Uso:  $0 <carpeta_de_fotos> [nombre_proyecto]"
    echo "Ejemplo: $0 ./fotos_fosil mammuthus_molar"
    exit 1
}

[[ $# -lt 1 ]] && usage

FOTOS_DIR="$(realpath "$1")"
PROYECTO="${2:-proyecto}"
TRABAJO_DIR="$(pwd)/${PROYECTO}_output"
NVM_FILE="$TRABAJO_DIR/${PROYECTO}.nvm"

# ---------- validaciones ----------
if [[ ! -d "$FOTOS_DIR" ]]; then
    echo "Error: la carpeta '$FOTOS_DIR' no existe."
    exit 1
fi

NFOTOS=$(find "$FOTOS_DIR" -maxdepth 1 -iname "*.jpg" -o -iname "*.jpeg" \
         -o -iname "*.png" -o -iname "*.tif" | wc -l)
if [[ "$NFOTOS" -lt 3 ]]; then
    echo "Error: se necesitan al menos 3 imágenes en '$FOTOS_DIR' (encontradas: $NFOTOS)."
    exit 1
fi

for BIN in "$VSFM" "$CMVS" "$PMVS" "$GENOPTION"; do
    if [[ ! -x "$BIN" ]]; then
        echo "Error: no se encontró el ejecutable '$BIN'."
        echo "Instala VisualSFM con:  ./instalar-vsfm.sh"
        exit 1
    fi
done

# ---------- inicio ----------
mkdir -p "$TRABAJO_DIR"
LOG="$TRABAJO_DIR/workflow.log"
exec > >(tee -a "$LOG") 2>&1

echo "======================================================"
echo " Workflow VisualSFM + CMVS/PMVS2"
echo " Proyecto : $PROYECTO"
echo " Fotos    : $FOTOS_DIR ($NFOTOS imágenes)"
echo " Salida   : $TRABAJO_DIR"
echo " Inicio   : $(date)"
echo "======================================================"

# ---------- PASO 1: SfM (Structure from Motion) ----------
echo ""
echo "--- PASO 1/4: SfM — orientación de cámaras y nube dispersa ---"
echo "Esto puede tardar varios minutos según la cantidad de fotos..."

"$VSFM" sfm "$FOTOS_DIR"/*.jpg "$NVM_FILE" 2>&1 || \
"$VSFM" sfm "$FOTOS_DIR"/*.JPG "$NVM_FILE" 2>&1 || \
"$VSFM" sfm "$FOTOS_DIR"/*.png "$NVM_FILE" 2>&1

if [[ ! -f "$NVM_FILE" ]]; then
    echo "Error: no se generó el archivo .nvm. Revisa las fotos y vuelve a intentarlo."
    exit 1
fi
echo "✔  Nube dispersa generada: $NVM_FILE"

# ---------- PASO 2: CMVS (clustering) ----------
echo ""
echo "--- PASO 2/4: CMVS — agrupación de vistas para PMVS2 ---"
NVM_DIR="$TRABAJO_DIR/${PROYECTO}.nvm.cmvs"
mkdir -p "$NVM_DIR"

"$CMVS" "$TRABAJO_DIR/${PROYECTO}.nvm/" "$CMVS_MAXIMAGE"
echo "✔  CMVS completado"

# ---------- PASO 3: genOption ----------
echo ""
echo "--- PASO 3/4: genOption — generando parámetros PMVS2 ---"
# genOption genera el archivo option-xxxx para cada cluster
BUNDLE_DIR="$TRABAJO_DIR/${PROYECTO}.nvm.cmvs/00/"
"$GENOPTION" "$BUNDLE_DIR" \
    $PMVS_LEVEL $PMVS_CSIZE $PMVS_THRESHOLD $PMVS_WSIZE $PMVS_MINIMAGE
echo "✔  Opciones generadas"

# ---------- PASO 4: PMVS2 (nube densa) ----------
echo ""
echo "--- PASO 4/4: PMVS2 — reconstrucción de nube densa ---"
echo "Esta es la etapa más lenta. Monitorea temperatura del CPU."

for OPTION in "$BUNDLE_DIR"option-*.txt; do
    echo "  Procesando cluster: $(basename "$OPTION")"
    "$PMVS" "$BUNDLE_DIR" "$(basename "$OPTION")"
done

# ---------- resultado ----------
echo ""
echo "======================================================"
echo " Workflow completado: $(date)"
RESULT=$(find "$TRABAJO_DIR" -name "*.ply" 2>/dev/null | head -5)
if [[ -n "$RESULT" ]]; then
    echo " Archivos .ply generados:"
    echo "$RESULT" | sed 's/^/   /'
    echo ""
    echo " Siguiente paso:"
    echo "   Abrir los .ply en MeshLab para reconstruir la malla"
    echo "   Filtros recomendados:"
    echo "     1. Poisson Surface Reconstruction"
    echo "     2. Remove Isolated pieces"
    echo "     3. Close Holes"
else
    echo " Advertencia: no se encontraron archivos .ply."
    echo " Revisa el log en: $LOG"
fi
echo "======================================================"
