from datetime import datetime, timedelta
from app.domain.repositories.ticket_repository import ITicketRepository
from app.domain.reporting.report_generator import IReportGenerator

class GenerarReporteTicketsUseCase:
    def __init__(self, repository: ITicketRepository, generator: IReportGenerator):
        self.repository = repository
        self.generator = generator

    def ejecutar(self, user_id: int, generado_por: str, comentarios: str) -> str:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        tickets = self.repository.obtener_por_rango_fechas(user_id, start_of_week, end_of_week)
        
        
        ruta_archivo = f"reporte_tickets_{user_id}.xlsx"
        
        header_data = {
            "fecha_inicio": start_of_week,
            "generado_por": generado_por,
            "comentarios": comentarios
        }

        return self.generator.generar(tickets, ruta_archivo, header_data)