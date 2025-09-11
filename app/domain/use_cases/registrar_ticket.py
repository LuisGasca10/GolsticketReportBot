# src/domain/use_cases/registrar_ticket.py
from app.domain.entities.entities import Ticket
from app.domain.repositories.ticket_repository import ITicketRepository
from app.domain.repositories.user_repository import IUsuarioRepository


class RegistrarTicketUseCase:
    def __init__(self, ticket_repository: ITicketRepository, usuario_repository: IUsuarioRepository):
         self.ticket_repository = ticket_repository
         self.usuario_repository = usuario_repository

    def ejecutar(self, ticket: Ticket):
        usuario = self.usuario_repository.obtener_por_telegram_id(ticket.user_id)
        if not usuario:
            # Esta validación es una segunda capa de seguridad
            raise ValueError("Usuario no registrado. Por favor, usa /registrar primero.")
        ticket.atendido_por = usuario.nombre_completo
        
        self.ticket_repository.agregar(ticket)