import os
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

# Añadir src al path para que Python encuentre los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
load_dotenv()

# --- Importaciones de Infraestructura ---
from app.infrastructure.datasources.ticket_local_datasource import TicketLocalDatasource
from app.infrastructure.repositories.ticket_repository_impl import TicketRepositoryImpl
from app.infrastructure.datasources.usuario_local_datasource import UsuarioLocalDatasource
from app.infrastructure.repositories.user_repository_impl import UsuarioRepositoryImpl
from app.infrastructure.reporting.excel_generator import ExcelReportGenerator
from app.infrastructure.telegram.handlers import BotHandlers

# --- Importaciones de Dominio ---
from app.domain.use_cases.registrar_ticket import RegistrarTicketUseCase
from app.domain.use_cases.generar_reporte_tickets import GenerarReporteTicketsUseCase
from app.domain.use_cases.registrar_usuario import RegistrarUsuarioUseCase
from app.domain.use_cases.obtener_usuario import ObtenerUsuarioUseCase

def main() -> None:
    # 1. Inyección de Dependencias
    ticket_local_datasource = TicketLocalDatasource()
    ticket_repository = TicketRepositoryImpl(datasource=ticket_local_datasource)
    
    usuario_local_datasource = UsuarioLocalDatasource()
    usuario_repository = UsuarioRepositoryImpl(datasource=usuario_local_datasource)
    
    report_generator = ExcelReportGenerator()

    # 2. Casos de Uso
    registrar_usuario_uc = RegistrarUsuarioUseCase(repository=usuario_repository)
    obtener_usuario_uc = ObtenerUsuarioUseCase(repository=usuario_repository)
    registrar_ticket_uc = RegistrarTicketUseCase(
        ticket_repository=ticket_repository, 
        usuario_repository=usuario_repository
    )
    generar_reporte_uc = GenerarReporteTicketsUseCase(
        repository=ticket_repository, 
        generator=report_generator
    )

    # 3. Handlers de Telegram
    handlers = BotHandlers(
        registrar_ticket_use_case=registrar_ticket_uc,
        generar_reporte_use_case=generar_reporte_uc,
        registrar_usuario_use_case=registrar_usuario_uc,
        obtener_usuario_use_case=obtener_usuario_uc
    )
    
    # 4. Configuración y Ejecución del Bot
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token:
        raise ValueError("No se encontró el TELEGRAM_TOKEN en las variables de entorno.")

    application = Application.builder().token(telegram_token).build()

    # Añadir manejadores
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("registrar", handlers.registrar_usuario))
    application.add_handler(handlers.get_conversation_handler())
    application.add_handler(CommandHandler("reporte", handlers.generar_reporte))

    print("🚀 Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling()

if __name__ == "__main__":
    main()