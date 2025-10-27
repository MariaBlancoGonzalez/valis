# Mi Registro

Breve descripción
------------------
`register.py` realiza el registro (rigid y micro / no-rigid) de Whole Slide Images (WSI) usando la librería `valis`.

- Se obtiene primero un ajuste rígido a baja resolución.
- Opcionalmente se aplica un `MicroRigidRegistrar` para mejorar el ajuste rígido a mayor resolución y después la micro-registración (no-rigid) sobre una fracción de la resolución completa.

Qué hace el script
-------------------
- Carga las imágenes desde la carpeta indicada en la variable `slide_src_dir`.
- Ejecuta el flujo de registro mediante `registration.Valis(...)`.
- Guarda resultados en la carpeta definida por `results_dst_dir` (por defecto en el archivo es `./registered`).
- Dibuja y guarda coincidencias de alta resolución en `hi_rez_matches` dentro del directorio de resultados.

Salida esperada
---------------
- Dentro de `results_dst_dir` verás subcarpetas/archivos relativos al registro rígido y a la micro-registración. Dependiendo de la versión de `valis` pueden aparecer subcarpetas como `processed`, `rigid_registration`, `micro_registration`, y `hi_rez_matches`.

