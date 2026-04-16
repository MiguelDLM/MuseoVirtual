#!/bin/bash

# Directorio de trabajo
WORK_DIR="/home/miguel/Pictures/photogrammetry"
cd "$WORK_DIR" || exit

# Crear un entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar el entorno virtual
source venv/bin/activate

# Instalar rembg y Pillow si no están instalados
echo "Instalando dependencias (rembg)... esto puede tardar un momento."
pip install "rembg[gpu]" Pillow

# Crear directorio de salida
mkdir -p "$WORK_DIR/output_nobg"

echo "Procesando imágenes con rembg..."
# rembg tiene un comando (p) para procesar carpetas enteras de forma masiva
rembg p "$WORK_DIR" "$WORK_DIR/output_nobg"

echo "¡Proceso terminado! Las imágenes sin fondo están en: $WORK_DIR/output_nobg"

# Desactivar entorno
deactivate
