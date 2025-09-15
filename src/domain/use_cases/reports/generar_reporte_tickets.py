from datetime import datetime, timedelta
from typing import Tuple
import pytz
from src.domain.repositories.ticket_repository import ITicketRepository
from src.domain.repositories.user_repository import IUsuarioRepository
from src.domain.reporting.report_generator import IReportGenerator

class GenerarReporteTicketsUseCase:
    def __init__(self, repository: ITicketRepository, generator: IReportGenerator, usuario_repo: IUsuarioRepository):
        self.repository = repository
        self.generator = generator
        self.usuario_repo = usuario_repo

    def ejecutar(self, telegram_user_id: int, comentarios: str) -> Tuple[str, bytes]:
        print("\n--- [DEBUG] Iniciando caso de uso: GenerarReporteTickets ---")
        
        usuario = self.usuario_repo.obtener_por_telegram_id(telegram_user_id)
        if not usuario:
            raise ValueError("No se puede generar un reporte para un usuario no registrado.")

        # --- Lógica de cálculo de fechas ---
        mexico_tz = pytz.timezone('America/Mexico_City')
        today = datetime.now(mexico_tz)

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=5) # Lunes a Sábado

        # --- LOG AÑADIDO ---
        # Mostramos en la consola el rango de fechas que se va a usar para la consulta.
        print(f"[DEBUG] Calculando rango de fechas para el reporte:")
        print(f"  -> Fecha de inicio (Lunes): {start_of_week.strftime('%Y-%m-%d')}")
        print(f"  -> Fecha de fin (Sábado):   {end_of_week.strftime('%Y-%m-%d')}")
        
        # --- Lógica de obtención de tickets ---
        tickets = self.repository.obtener_por_rango_fechas_y_usuario(usuario.id, start_of_week, end_of_week)
        
        # --- LOG AÑADIDO ---
        # Mostramos cuántos tickets se encontraron en la base de datos para ese rango.
        print(f"[DEBUG] Tickets encontrados en la base de datos para este rango: {len(tickets)}")
        
        if not tickets:
            print("[DEBUG] La lista de tickets está vacía. El reporte se generará sin datos en la tabla.")

        # --- Lógica de generación de nombre y cabecera (sin cambios) ---
        nombre_archivo = f"Reporte_{usuario.nombre_completo.replace(' ', '_')}_{start_of_week.strftime('%Y-%m-%d')}.xlsx"
        
        header_data = {
            "fecha_inicio": start_of_week,
            "fecha_fin": end_of_week,
            "generado_por": usuario.nombre_completo,
            "comentarios": comentarios
        }

        file_bytes = self.generator.generar(tickets, header_data)
        
        print("--- [DEBUG] Finalizado caso de uso: GenerarReporteTickets ---\n")
        return (nombre_archivo, file_bytes)