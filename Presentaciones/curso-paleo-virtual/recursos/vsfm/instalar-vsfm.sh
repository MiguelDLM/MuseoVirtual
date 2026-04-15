#!/usr/bin/env bash
# ============================================================
# instalar-vsfm.sh
# Descarga, compila y configura VisualSFM en Linux x86_64
# Basado en: https://github.com/Moult/vsfm-linux-x86_64
# Probado en Ubuntu 22.04 / 24.04
# ============================================================
set -e

INSTALL_DIR="$HOME/VisualSFM"
VSFM_REPO="https://github.com/Moult/vsfm-linux-x86_64.git"
ALIAS_CMD="cd $INSTALL_DIR && ./visualsfm.sh"

echo "=== Instalando dependencias del sistema ==="
sudo apt-get update -qq
sudo apt-get install -y \
    build-essential \
    git \
    wget \
    unzip \
    libgtk2.0-dev \
    freeglut3-dev \
    libdevil-dev \
    libglew-dev \
    libglu1-mesa-dev

echo ""
echo "=== Clonando build scripts de Moult ==="
if [[ -d "$INSTALL_DIR/.git" ]]; then
    echo "Directorio ya existe — actualizando..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    git clone --depth=1 "$VSFM_REPO" "$INSTALL_DIR"
fi

echo ""
echo "=== Compilando VisualSFM (SiftGPU + PBA + VisualSFM) ==="
echo "Esto descargará ~80 MB y puede tardar 5–15 minutos..."
cd "$INSTALL_DIR"
make

echo ""
echo "=== Creando alias global 'vsfm' ==="
SHELL_RC="$HOME/.bashrc"
[[ "$SHELL" == *zsh ]] && SHELL_RC="$HOME/.zshrc"

if ! grep -q "alias vsfm=" "$SHELL_RC" 2>/dev/null; then
    echo ""                                                     >> "$SHELL_RC"
    echo "# VisualSFM"                                         >> "$SHELL_RC"
    echo "alias vsfm='cd $INSTALL_DIR && ./visualsfm.sh'"     >> "$SHELL_RC"
fi

echo ""
echo "=== Verificando instalación ==="
if [[ -x "$INSTALL_DIR/vsfm/bin/VisualSFM" ]]; then
    echo "✔  VisualSFM compilado en: $INSTALL_DIR/vsfm/bin/VisualSFM"
    echo "✔  Listo para usar"
else
    echo "✘  No se encontró el ejecutable. Revisa los errores anteriores."
    exit 1
fi

echo ""
echo "=== Instalación completa ==="
echo "Reinicia la terminal o ejecuta:  source $SHELL_RC"
echo "Luego abre VisualSFM con:        vsfm"
echo ""
echo "O siempre puedes ejecutar directamente:"
echo "  cd $INSTALL_DIR && ./visualsfm.sh"
echo ""
echo "Para el workflow automático usa: ./fotogrametria-workflow.sh <carpeta_fotos>"
