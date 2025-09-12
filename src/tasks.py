import os
import asyncio
import telegram
from celery import Celery
from dotenv import load_dotenv

# El worker es un proceso separado, por lo que necesita cargar
# las variables de entorno por su cuenta.
load_dotenv()

# --- Importamos las piezas de nuestra arquitectura que el worker necesita ---
from src.infrastructure.scraping.ticket_scraper import TicketScraper
from src.infrastructure.datasources.ticket_sqlite_datasource import TicketSQLDatasource
from src.infrastructure.repositories.ticket_repository_impl import TicketRepositoryImpl
from src.infrastructure.datasources.usuario_sqlite_datasource import UsuarioSQLDatasource
from src.infrastructure.repositories.user_repository_impl import UsuarioRepositoryImpl
from src.domain.use_cases.importar_ticket import ImportarTicketUseCase

# --- Configuración de la App de Celery ---
celery_app = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'))

# --- Función auxiliar para enviar mensajes desde el worker ---
async def send_telegram_message(chat_id, message, parse_mode=None):
    """Crea una instancia de bot para enviar un mensaje de notificación."""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("WORKER: No se encontró el TELEGRAM_TOKEN, no se pueden enviar notificaciones.")
        return
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=parse_mode)

@celery_app.task
def procesar_ticket_task(ticket_id: int, user_id: int, chat_id: int):
    """
    Tarea de scraping que ahora notifica al usuario el resultado.
    """
    print(f"WORKER: Recibida tarea para procesar ticket #{ticket_id}")
    
    scraper = None
    try:
        # 1. El worker construye sus propias instancias
        scraper = TicketScraper()
        ticket_datasource = TicketSQLDatasource()
        ticket_repository = TicketRepositoryImpl(datasource=ticket_datasource)
        usuario_datasource = UsuarioSQLDatasource()
        usuario_repository = UsuarioRepositoryImpl(datasource=usuario_datasource)
        
        importar_uc = ImportarTicketUseCase(
            scraper=scraper,
            ticket_repo=ticket_repository,
            usuario_repo=usuario_repository
        )
        
        # 2. Ejecuta el caso de uso
        ticket = importar_uc.ejecutar(ticket_id, user_id, chat_id)
        
        # 3. Notifica el éxito
        mensaje_exito = (
            f"✅ ¡Ticket *#{ticket.numero_ticket}* importado con éxito!\n\n"
            f"**Empresa:** {ticket.empresa}\n"
            f"**Reportado por:** {ticket.usuario_reporta}"
        )
        asyncio.run(send_telegram_message(chat_id, mensaje_exito, parse_mode='Markdown'))
        
    except Exception as e:
        print(f"WORKER: Falló la tarea para el ticket #{ticket_id}. Error: {e}")
        # 4. Notifica el fallo
        mensaje_error = f"❌ No se pudo importar el ticket *#{ticket_id}*. Razón: {e}"
        asyncio.run(send_telegram_message(chat_id, mensaje_error, parse_mode='Markdown'))
    finally:
        # Es crucial cerrar el navegador al final de cada tarea
        if scraper:
            scraper.cerrar_sesion()