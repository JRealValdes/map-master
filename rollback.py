import os
import shutil
from datetime import datetime

# Obtiene el directorio del script actual
script_directory = os.path.dirname(os.path.abspath(__file__))

# Obtiene todos los directorios de respaldo ordenados por fecha
backup_directories = sorted(
    [d for d in os.listdir(script_directory) if d.startswith('backup_')],
    key=lambda x: os.path.getmtime(os.path.join(script_directory, x)),
    reverse=True
)

# Verifica si existen directorios de respaldo
if not backup_directories:
    print("No se encontraron directorios de respaldo. No se puede realizar el rollback.")
    exit()

# Selecciona el último directorio de respaldo
latest_backup_directory = os.path.join(script_directory, backup_directories[0])

# Restaura los archivos originales desde el último directorio de respaldo
backup_files = [f for f in os.listdir(
    latest_backup_directory) if f.endswith('.html')]
for file in backup_files:
    shutil.copy2(os.path.join(latest_backup_directory, file), script_directory)

# Elimina el último directorio de respaldo
shutil.rmtree(latest_backup_directory)

print(
    f"Rollback completado. Los archivos originales han sido restaurados desde '{latest_backup_directory}' y el respaldo ha sido eliminado.")
