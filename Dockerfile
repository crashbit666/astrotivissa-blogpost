# Usa una imagen base oficial de Python
FROM python:3.12-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Crea un entorno virtual
RUN python -m venv venv

# Activa el entorno virtual y instala las dependencias
RUN /bin/bash -c "source venv/bin/activate && pip install --no-cache-dir -r requirements.txt"

# Copia el contenido del directorio actual en el contenedor
COPY . .

# Establece las variables de entorno para usar el entorno virtual
ENV PATH="/app/venv/bin:$PATH"

# Comando por defecto para ejecutar tu aplicación
CMD ["python", "-m", "src.main"]
