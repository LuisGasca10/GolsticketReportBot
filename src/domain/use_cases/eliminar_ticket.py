from uuid import UUID
from src.domain.repositories.ticket_repository import ITicketRepository

class EliminarTicketUseCase:
    def __init__(self, repository: ITicketRepository):
        self.repository = repository

    def ejecutar(self, ticket_id: UUID) -> bool:
        """Devuelve True si la eliminación fue exitosa, False en caso contrario."""
        return self.repository.eliminar_por_id(ticket_id)
