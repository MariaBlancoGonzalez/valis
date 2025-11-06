#!/bin/bash

# Directorio que contiene las carpetas por ID
BASE_DIR="/home/visilab/Workspace/valis/images"

# Verifica que exista
if [ ! -d "$BASE_DIR" ]; then
    echo "===== El directorio $BASE_DIR no existe. ====="
    exit 1
fi

echo "🔍 Buscando carpetas dentro de $BASE_DIR ..."

# Recorre todas las subcarpetas dentro de BASE_DIR
for folder in "$BASE_DIR"/*; do
    if [ -d "$folder" ]; then
        echo "🚀 Ejecutando register.py para carpeta: $folder"
        python3 scripts/rigid_reg.py --slide_src_dir "$folder"
        echo "===== Finalizado para: $folder ====="
        echo "-------------------------------------------"
    fi
done

echo "===== Todas las carpetas han sido procesadas. ====="