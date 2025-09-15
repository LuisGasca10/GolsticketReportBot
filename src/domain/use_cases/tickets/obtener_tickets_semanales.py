from typing import List
from datetime import datetime, timedelta
import pytz
from src.domain.entities.entities import Ticket
from src.domain.repositories.ticket_repository import ITicketRepository
from src.domain.repositories.user_repository import IUsuarioRepository

class ObtenerTicketsSemanalesUseCase:
    def __init__(self, ticket_repo: ITicketRepository, usuario_repo: IUsuarioRepository):
        self.ticket_repo = ticket_repo
        self.usuario_repo = usuario_repo

    def ejecutar(self, telegram_user_id: int) -> List[Ticket]:
        usuario = self.usuario_repo.obtener_por_telegram_id(telegram_user_id)
        if not usuario:
            raise ValueError("Usuario no registrado.")

        mexico_tz = pytz.timezone('America/Mexico_City')
        today = datetime.now(mexico_tz)

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=5)

        return self.ticket_repo.obtener_por_rango_fechas_y_usuario(usuario.id, start_of_week, end_of_week)
