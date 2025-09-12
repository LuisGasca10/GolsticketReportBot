from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.entities import Ticket

class ITicketScraper(ABC):
    @abstractmethod
    def obtener_datos_ticket(self, ticket_id: int, user_id: int, chat_id: int) -> Optional[Ticket]:
        pass

    @abstractmethod
    def cerrar_sesion(self):
        pass