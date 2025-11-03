import os
import shutil

# Directorios de origen
dirs = ["er", "he", "her2", "ki67", "pr"]

# Directorio de salida
output_dir = "organization_output"
os.makedirs(output_dir, exist_ok=True)

# Recorrer cada directorio de entrada
for d in dirs:
    for file_name in os.listdir(d):
        if file_name.endswith(".svs"):
            # Extraer el ID (antes del primer '_')
            id_part = file_name.split('_')[0]
            
            # Crear carpeta destino con el nombre del ID
            id_folder = os.path.join(output_dir, id_part)
            os.makedirs(id_folder, exist_ok=True)
            
            # Rutas completas
            src = os.path.join(d, file_name)
            dst = os.path.join(id_folder, file_name)
            
            # Copiar archivo (no sobrescribe si ya existe)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                print(f"Copiado: {file_name} → {id_folder}")
            else:
                print(f"Ya existe: {dst}")
