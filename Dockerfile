# docker build -t map-master .
# cd Documents/gen_ai_course_project/map-master
# docker run -p 5000:7860 --env-file .env map-master
# Luego ir a http://localhost:5000 o http://192.168.1.91:7860
# Crea un mapa mental sobre Daredevil

FROM python:3.9-slim

RUN apt-get update && apt-get install -y nodejs npm
# Crear un nuevo usuario "user" con el ID de usuario 1000
RUN useradd -m -u 1000 user

# Cambiar al usuario "user"
USER user

# Configurar el directorio de trabajo y las variables de entorno
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Actualizar pip e instalar las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip

# Copiar el archivo requirements.txt e instalar dependencias
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar package.json y package-lock.json
COPY --chown=user package*.json ./

# Ajustar permisos para evitar errores de acceso
USER root
RUN chown -R user:user /home/user/app

# Volver al usuario "user" para instalar las dependencias de npm
USER user
RUN npm install

# Copiar el resto del código de la aplicación
COPY --chown=user . $HOME/app

# Crear y establecer permisos para el directorio de markdowns
RUN mkdir -p $HOME/app/markdowns
RUN chmod 777 $HOME/app/markdowns

# Exponer el puerto 7860
EXPOSE 7860

# Comando para ejecutar la aplicación usando Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]

