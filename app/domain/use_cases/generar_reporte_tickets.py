from datetime import datetime, timedelta
from app.domain.repositories.user_repository import IUsuarioRepository
from app.domain.repositories.ticket_repository import ITicketRepository
from app.domain.reporting.report_generator import IReportGenerator

class GenerarReporteTicketsUseCase:
    def __init__(self, repository: ITicketRepository, generator: IReportGenerator, usuario_repo: IUsuarioRepository):
        self.repository = repository
        self.generator = generator
        self.usuario_repo = usuario_repo

    def ejecutar(self, telegram_user_id: int, comentarios: str) -> str:
        usuario = self.usuario_repo.obtener_por_telegram_id(telegram_user_id)
        if not usuario:
            raise ValueError("No se puede generar un reporte para un usuario no registrado.")

        today = datetime.now()
        # El lunes es el día 0 del weekday, así que esto calcula el lunes de la semana actual
        start_of_week = today - timedelta(days=today.weekday())
        # --- CORRECCIÓN ---
        # El viernes es 4 días después del lunes
        end_of_week = start_of_week + timedelta(days=4)
        
        tickets = self.repository.obtener_por_rango_fechas_y_usuario(usuario.id, start_of_week, end_of_week)
        
        ruta_archivo = f"reporte_tickets_{telegram_user_id}.xlsx"
        header_data = {
            "fecha_inicio": start_of_week,
            "fecha_fin": end_of_week, # Pasamos la fecha de fin (viernes)
            "generado_por": usuario.nombre_completo,
            "comentarios": comentarios
        }

        return self.generator.generar(tickets, ruta_archivo, header_data)

