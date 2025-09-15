from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Clase que centraliza todas las variables de entorno usando Pydantic.
    Pydantic se encarga de leer el archivo .env, validar los tipos y la presencia
    de las variables requeridas de forma automática.
    """
    # Configuración para que Pydantic lea desde el archivo .env
    # 'extra='ignore'' evita errores si hay variables extra en el .env
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # --- Configuración del Bot de Telegram ---
    # Al no tener un valor por defecto, Pydantic la considera obligatoria.
    # Si no la encuentra en el .env, el programa fallará al iniciar.
    TELEGRAM_TOKEN: str

    # --- Configuración de PostgreSQL ---
    # Estas tienen valores por defecto si no se encuentran en el .env
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str # Obligatoria

    # --- Configuración de Celery y Redis ---
    CELERY_BROKER_URL: str # Obligatoria

    # --- Configuración del Web Scraper ---
    # Usamos 'Field' con un alias para mapear la variable 'USUARIO' del .env
    # al atributo 'SCRAPER_USUARIO' de nuestra clase. Esto hace el código más explícito.
    # El '...' significa que el campo es obligatorio.
    SCRAPER_USUARIO: str = Field(..., alias='USUARIO')
    SCRAPER_PASSWORD: str = Field(..., alias='PASSWORD')
    SCRAPER_BASE_URL: str = Field(..., alias='BASE_URL')


# Creamos una instancia única. Si alguna variable obligatoria falta en el .env,
# la aplicación fallará aquí mismo con un error claro y descriptivo.
settings = Settings()

