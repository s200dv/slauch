# Usa una imagen base de Python
FROM python:3.11-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . /app

# Instala las dependencias de tu proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que Flask estará corriendo
EXPOSE 8080

# Comando para ejecutar la aplicación Flask
CMD ["python", "app.py"]
