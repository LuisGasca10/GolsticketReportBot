from datetime import datetime
from src.domain.entities.entities import Ticket
import pytz
from src.domain.repositories.ticket_repository import ITicketRepository
from src.domain.repositories.user_repository import IUsuarioRepository

class RegistrarTicketUseCase:
    def __init__(self, ticket_repository: ITicketRepository, usuario_repository: IUsuarioRepository):
        self.ticket_repository = ticket_repository
        self.usuario_repository = usuario_repository

    def ejecutar(self, ticket: Ticket):
        usuario = self.usuario_repository.obtener_por_telegram_id(ticket.user_id)
        if not usuario:
            raise ValueError("Usuario no registrado.")
        
        mexico_tz = pytz.timezone('America/Mexico_City')
        ticket.fecha = datetime.now(mexico_tz)
        
        ticket.atendido_por = usuario.nombre_completo
        
        self.ticket_repository.agregar(ticket, usuario.id)