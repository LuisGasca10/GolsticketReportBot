# src/domain/use_cases/registrar_ticket.py
from app.domain.entities.entities import Ticket
from app.domain.repositories.ticket_repository import ITicketRepository

class RegistrarTicketUseCase:
    def __init__(self, repository: ITicketRepository):
        self.repository = repository

    def ejecutar(self, ticket: Ticket):
        self.repository.agregar(ticket)