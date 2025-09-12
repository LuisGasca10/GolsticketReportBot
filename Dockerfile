# -----------------------------------------------------------------------------
# ETAPA 1: IMAGEN BASE Y DEPENDENCIAS DEL SISTEMA
# -----------------------------------------------------------------------------
# Usamos una imagen de Debian (bookworm) con Python 3.11, que es estable
# y nos permite instalar Google Chrome fácilmente.
FROM python:3.11-slim-bookworm

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# -----------------------------------------------------------------------------
# ETAPA 2: INSTALACIÓN DE GOOGLE CHROME Y CHROMEDRIVER PARA SELENIUM
# -----------------------------------------------------------------------------
# Actualizamos los repositorios e instalamos las herramientas necesarias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    # Añadimos el repositorio oficial de Google Chrome
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    # Instalamos Google Chrome
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Descargamos y descomprimimos ChromeDriver
    # Nota: Esta versión debe ser compatible con la de Chrome instalada.
    && wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.78/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    # Limpiamos la caché para mantener la imagen lo más pequeña posible
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# ETAPA 3: INSTALACIÓN DE DEPENDENCIAS DE PYTHON
# -----------------------------------------------------------------------------
# Copiamos primero el archivo de requerimientos para aprovechar la caché de Docker
COPY requirements.txt .
# Instalamos todos los paquetes de Python
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# ETAPA 4: COPIAR EL CÓDIGO DE LA APLICACIÓN Y EJECUTAR
# -----------------------------------------------------------------------------
# Copiamos todo el código fuente de nuestra aplicación al contenedor.
# Como 'tasks.py' ahora está dentro de 'src', se copiará automáticamente aquí.
COPY ./src ./src
COPY main.py .
# --- AÑADIMOS LA PLANTILLA DE EXCEL ---
COPY template_reporte.xlsx .


# El comando por defecto para ejecutar cuando el contenedor inicie.
# Esto será usado por el servicio 'bot'. El servicio 'worker' lo sobreescribirá
# con su propio comando en el docker-compose.yml.
CMD ["python", "main.py"]

