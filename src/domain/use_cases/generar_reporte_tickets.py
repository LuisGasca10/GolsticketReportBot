from datetime import datetime, timedelta
from typing import Tuple # Importamos Tuple para definir el tipo de retorno
from src.domain.repositories.ticket_repository import ITicketRepository
from src.domain.repositories.user_repository import IUsuarioRepository
from src.domain.reporting.report_generator import IReportGenerator

class GenerarReporteTicketsUseCase:
    def __init__(self, repository: ITicketRepository, generator: IReportGenerator, usuario_repo: IUsuarioRepository):
        self.repository = repository
        self.generator = generator
        self.usuario_repo = usuario_repo

    # El método ahora devuelve una tupla: (nombre_del_archivo, contenido_en_bytes)
    def ejecutar(self, telegram_user_id: int, comentarios: str) -> Tuple[str, bytes]:
        usuario = self.usuario_repo.obtener_por_telegram_id(telegram_user_id)
        if not usuario:
            raise ValueError("No se puede generar un reporte para un usuario no registrado.")

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=4) # Lunes a Viernes
        
        # La obtención de tickets no cambia
        tickets = self.repository.obtener_por_rango_fechas_y_usuario(usuario.id, start_of_week, end_of_week)
        
        # Generamos el nombre del archivo dinámicamente
        nombre_archivo = f"Reporte_{usuario.nombre_completo.replace(' ', '_')}_{start_of_week.strftime('%Y-%m-%d')}.xlsx"
        
        header_data = {
            "fecha_inicio": start_of_week,
            "fecha_fin": end_of_week,
            "generado_por": usuario.nombre_completo,
            "comentarios": comentarios
        }

        # Obtenemos los bytes del archivo directamente desde el generador
        # Ya no pasamos una ruta de archivo
        file_bytes = self.generator.generar(tickets, header_data)
        
        # Devolvemos el nombre y el contenido
        return (nombre_archivo, file_bytes)

