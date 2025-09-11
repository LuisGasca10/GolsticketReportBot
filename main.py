import os
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

# Añadir src al path para que Python encuentre los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))
load_dotenv()

# --- Importaciones de Infraestructura ---
from app.infrastructure.datasources.ticket_local_datasource import TicketLocalDatasource
from app.infrastructure.repositories.ticket_repository_impl import TicketRepositoryImpl
from app.infrastructure.reporting.excel_generator import ExcelReportGenerator
from app.infrastructure.telegram.handlers import BotHandlers

# --- Importaciones de Dominio ---
from app.domain.use_cases.registrar_ticket import RegistrarTicketUseCase
from app.domain.use_cases.generar_reporte_tickets import GenerarReporteTicketsUseCase

def main() -> None:
    # 1. Inyección de Dependencias
    ticket_local_datasource = TicketLocalDatasource()
    ticket_repository = TicketRepositoryImpl(datasource=ticket_local_datasource)
    report_generator = ExcelReportGenerator()

    # 2. Casos de Uso
    registrar_ticket_uc = RegistrarTicketUseCase(repository=ticket_repository)
    generar_reporte_uc = GenerarReporteTicketsUseCase(repository=ticket_repository, generator=report_generator)

    # 3. Handlers de Telegram
    handlers = BotHandlers(
        registrar_ticket_use_case=registrar_ticket_uc,
        generar_reporte_use_case=generar_reporte_uc,
    )
    
    # 4. Configuración y Ejecución del Bot
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        raise ValueError("No se encontró el TELEGRAM_TOKEN en las variables de entorno.")

    application = Application.builder().token(telegram_token).build()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(handlers.get_conversation_handler())
    application.add_handler(CommandHandler("reporte", handlers.generar_reporte))

    print("🚀 Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling()

if __name__ == "__main__":
    main()