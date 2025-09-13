from datetime import datetime
from typing import Tuple
from src.domain.repositories.ticket_repository import ITicketRepository
from src.domain.repositories.user_repository import IUsuarioRepository
from src.domain.reporting.report_generator import IReportGenerator

class GenerarReporteGeneralUseCase:
    def __init__(self, ticket_repo: ITicketRepository, generator: IReportGenerator, usuario_repo: IUsuarioRepository):
        self.ticket_repo = ticket_repo
        self.generator = generator
        self.usuario_repo = usuario_repo

    def ejecutar(self, telegram_user_id: int, comentarios: str) -> Tuple[str, bytes]:
        # 1. Obtenemos el usuario para conseguir su ID de la base de datos (UUID)
        usuario = self.usuario_repo.obtener_por_telegram_id(telegram_user_id)
        if not usuario:
            raise ValueError("Usuario no registrado.")

        # 2. Llama al nuevo método del repositorio para obtener TODOS los tickets del usuario
        tickets = self.ticket_repo.obtener_todos_por_usuario_id(usuario.id)
        
        # 3. Preparamos un nombre de archivo descriptivo
        nombre_archivo = f"Reporte_General_{usuario.nombre_completo.replace(' ', '_')}.xlsx"
        
        # 4. Preparamos los datos para la cabecera del Excel, indicando que es un reporte histórico
        header_data = {
            "fecha_rango": "Histórico Completo", # Usamos un texto en lugar de fechas
            "generado_por": usuario.nombre_completo,
            "comentarios": comentarios
        }

        # 5. Llamamos al generador de Excel para que cree el archivo en memoria
        file_bytes = self.generator.generar(tickets, header_data)
        
        return (nombre_archivo, file_bytes)

