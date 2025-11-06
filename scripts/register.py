""" Registration of whole slide images (WSI) using higher resolution images
This example shows how to register the slides using higher resolution images.
An initial rigid transform is found using low resolition images, but the
`MicroRigidRegistrar` can be used to update that transform using feature matches
found in higher resoltion images. This can be followed up by the high resolution
non-rigid registration (i.e. micro-registration).
"""
import sys
sys.path.append("/Users/gatenbcd/Dropbox/Documents/image_processing/valis_project/valis")
# Force Valis / PyTorch to use CPU: hide CUDA devices before importing valis or torch.
# This prevents tensors being created on cuda:0 which then fail when converted to numpy.

import os

import time
import torch
import argparse

import numpy as np

from valis import registration
from valis.micro_rigid_registrar import MicroRigidRegistrar # For high resolution rigid registration

# Quitar y asegurar que los tensores se copien en CPU
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
os.environ.setdefault("VALIS_USE_CUDA", "1")

# Para usar GPU correctamente: parche runtime que hace .cpu() antes de .numpy()
# Esto evita el TypeError cuando una librería (valis) llama `.numpy()` sobre un
# tensor que vive en CUDA.
try:
    
    _orig_tensor_numpy = getattr(torch.Tensor, 'numpy', None)
    if _orig_tensor_numpy is not None:
        def _tensor_numpy_cpu(self, *args, **kwargs):
            # Si el tensor está en GPU, se mueve a CPU antes de convertir a numpy
            try:
                dev = getattr(self, 'device', None)
                if dev is not None and getattr(dev, 'type', None) != 'cpu':
                    return _orig_tensor_numpy(self.cpu(), *args, **kwargs)
            except Exception:
                # en caso de cualquier problema, fallback al comportamiento original
                pass
            return _orig_tensor_numpy(self, *args, **kwargs)
        torch.Tensor.numpy = _tensor_numpy_cpu
except Exception:
    # Si torch no está disponible, seguimos sin parche
    pass

# Leer esto por linea de comandos
parser = argparse.ArgumentParser(description="Procesar carpetas de slides")
parser.add_argument(
    "--slide_src_dir",
    type=str,
    required=True,
    help="Ruta a la carpeta que contiene los archivos .svs"
)

# Parsear argumentos
args = parser.parse_args()
slide_src_dir = args.slide_src_dir

# Comprobación
if not os.path.isdir(slide_src_dir):
    raise ValueError(f"La ruta {slide_src_dir} no existe o no es un directorio.")

results_dst_dir = "./register/"
micro_reg_fraction = 0.25 # Fraction full resolution used for non-rigid registration

# Perform high resolution rigid registration using the MicroRigidRegistrar
start = time.time()
registrar = registration.Valis(slide_src_dir, results_dst_dir, micro_rigid_registrar_cls=MicroRigidRegistrar)
rigid_registrar, non_rigid_registrar, error_df = registrar.register()

# Calculate what `max_non_rigid_registration_dim_px` needs to be to do non-rigid registration on an image that is 25% full resolution.
img_dims = np.array([slide_obj.slide_dimensions_wh[0] for slide_obj in registrar.slide_dict.values()])
min_max_size = np.min([np.max(d) for d in img_dims])
img_areas = [np.multiply(*d) for d in img_dims]
max_img_w, max_img_h = tuple(img_dims[np.argmax(img_areas)])
micro_reg_size = np.floor(min_max_size*micro_reg_fraction).astype(int)

# Perform high resolution non-rigid registration
micro_reg, micro_error = registrar.register_micro(max_non_rigid_registration_dim_px=micro_reg_size)

stop = time.time()
elapsed = stop - start
print(f"registration time is {elapsed/60} minutes")

# We can also plot the high resolution matches using `Valis.draw_matches`:
matches_dst_dir = os.path.join(registrar.dst_dir, "hi_rez_matches")
registrar.draw_matches(matches_dst_dir)

# ============================================================================
# Guardar las imágenes registradas en formato OME-TIFF
# ============================================================================

# Crear directorio para los archivos OME-TIFF
ome_tiff_dir = os.path.join(results_dst_dir, "ome_tiff_slides")
os.makedirs(ome_tiff_dir, exist_ok=True)

print("\n" + "="*60)
print("Guardando slides registrados en formato OME-TIFF...")
print("="*60)

# Guardar cada slide registrado como OME-TIFF
for slide_name, slide_obj in registrar.slide_dict.items():
    # Crear nombre del archivo de salida
    base_name = os.path.splitext(os.path.basename(slide_obj.src_f))[0]
    dst_f = os.path.join(ome_tiff_dir, f"{base_name}_registered.ome.tiff")
    
    print(f"\nGuardando {base_name}...")
    
    try:
        # Guardar el slide registrado en formato OME-TIFF
        # level=0 significa usar la resolución completa
        # non_rigid=True aplica las transformaciones no rígidas
        # crop=True recorta la imagen al área común
        # pyramid=True crea una pirámide de resoluciones
        # compression="jpeg" o "lzw" son opciones comunes
        slide_obj.warp_and_save_slide(
            dst_f=dst_f,
            level=0,  # Nivel de resolución (0 = máxima resolución)
            non_rigid=True,  # Aplicar transformación no rígida
            crop=True,  # Recortar al área de overlap
            interp_method="bicubic",  # Método de interpolación
            tile_wh=256,  # Tamaño de tile (importante para BigTIFF)
            compression="jpeg",  # Opciones: "jpeg", "lzw", "deflate", "none"
            Q=95,  # Calidad JPEG (1-100)
            pyramid=True  # Crear pirámide de resoluciones (recomendado para WSI)
        )
        
        print(f"Guardado exitosamente: {dst_f}")
        
        # Mostrar información del archivo guardado
        file_size_mb = os.path.getsize(dst_f) / (1024 * 1024)
        print(f"  - Tamaño del archivo: {file_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error guardando {base_name}: {str(e)}")

print("\n" + "="*60)
print(f"Proceso completado. Archivos OME-TIFF guardados en: {ome_tiff_dir}")
print("="*60)