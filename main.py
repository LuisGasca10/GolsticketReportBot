import os
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Añadimos la carpeta 'src' al path para que Python encuentre los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))


# --- Importaciones de la Capa de Infraestructura ---
from src.infrastructure.datasources.ticket_sqlite_datasource import TicketSQLDatasource
from src.infrastructure.repositories.ticket_repository_impl import TicketRepositoryImpl
from src.infrastructure.datasources.usuario_sqlite_datasource import UsuarioSQLDatasource
from src.infrastructure.repositories.user_repository_impl import UsuarioRepositoryImpl
from src.infrastructure.reporting.excel_generator import ExcelReportGenerator
from src.infrastructure.telegram.handlers import BotHandlers

# --- Importaciones de la Capa de Dominio (Casos de Uso) ---
from src.domain.use_cases.tickets.registrar_ticket import RegistrarTicketUseCase
from src.domain.use_cases.reports.generar_reporte_tickets import GenerarReporteTicketsUseCase
from src.domain.use_cases.user.registrar_usuario import RegistrarUsuarioUseCase
from src.domain.use_cases.user.obtener_usuario import ObtenerUsuarioUseCase
from src.domain.use_cases.tickets.obtener_tickets_semanales import ObtenerTicketsSemanalesUseCase
from src.domain.use_cases.tickets.eliminar_ticket import EliminarTicketUseCase
from src.domain.use_cases.reports.generar_reporte_general import GenerarReporteGeneralUseCase
from src.domain.use_cases.user.actualizar_usuario import EditarUsuarioUseCase


from src.config.settings import settings




def main() -> None:
    """
    Punto de entrada principal.
    Construye todas las dependencias y arranca el bot de Telegram.
    """
    
    # 1. Inyección de Dependencias
    # Se crean las instancias de las implementaciones concretas.
    # El bot principal ya NO necesita saber nada sobre el scraper.
    ticket_datasource = TicketSQLDatasource()
    ticket_repository = TicketRepositoryImpl(datasource=ticket_datasource)
    usuario_datasource = UsuarioSQLDatasource()
    usuario_repository = UsuarioRepositoryImpl(datasource=usuario_datasource)
    report_generator = ExcelReportGenerator()

    # 2. Casos de Uso
    # Se crean todas las "recetas" de lógica de negocio que el bot usará directamente.
    registrar_usuario_uc = RegistrarUsuarioUseCase(repository=usuario_repository)
    obtener_usuario_uc = ObtenerUsuarioUseCase(repository=usuario_repository)
    registrar_ticket_uc = RegistrarTicketUseCase(
        ticket_repository=ticket_repository, 
        usuario_repository=usuario_repository
    )
    generar_reporte_uc = GenerarReporteTicketsUseCase(
        repository=ticket_repository, 
        generator=report_generator,
        usuario_repo=usuario_repository
    )
    obtener_tickets_semanales_uc = ObtenerTicketsSemanalesUseCase(
        ticket_repo=ticket_repository,
        usuario_repo=usuario_repository
    )
    eliminar_ticket_uc = EliminarTicketUseCase(repository=ticket_repository)
    
    generar_reporte_general_uc = GenerarReporteGeneralUseCase(ticket_repo=ticket_repository, usuario_repo=usuario_repository, generator=report_generator)
    
    actualizar_usuario_uc = EditarUsuarioUseCase(repository=usuario_repository)
    
    # 3. Handlers de Telegram
    # Se le pasan al bot todas las "recetas" que necesita.
    handlers = BotHandlers(
        registrar_ticket_use_case=registrar_ticket_uc,
        generar_reporte_use_case=generar_reporte_uc,
        registrar_usuario_use_case=registrar_usuario_uc,
        obtener_usuario_use_case=obtener_usuario_uc,
        obtener_tickets_semanales_uc=obtener_tickets_semanales_uc,
        eliminar_ticket_uc=eliminar_ticket_uc,
        generar_reporte_general_uc=generar_reporte_general_uc,
        actualizar_usuario_uc=actualizar_usuario_uc
    )
    
    # 4. Configuración y Ejecución del Bot
    telegram_token = settings.TELEGRAM_TOKEN
    # if not telegram_token: 
    #     raise ValueError("No se encontró el TELEGRAM_TOKEN en las variables de entorno.")
        
    application = Application.builder().token(telegram_token).build()

    # Se registran todos los manejadores de comandos y botones
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("registrar", handlers.registrar_usuario))
    application.add_handler(CommandHandler("importar", handlers.importar_ticket))
    application.add_handler(CommandHandler("reporte", handlers.generar_reporte))
    application.add_handler(CommandHandler("reportegeneral", handlers.generar_reporte_general))
    application.add_handler(CommandHandler("eliminar", handlers.eliminar_ticket_start))
    application.add_handler(handlers.get_conversation_handler())
    application.add_handler(CallbackQueryHandler(handlers.eliminar_ticket_callback))
    application.add_handler(CommandHandler("editarnombre", handlers.editar_nombre))
    

    print("🚀 Bot iniciado. Worker de Celery debería estar corriendo en otro contenedor.")
    application.run_polling()


if __name__ == "__main__":
    main()

