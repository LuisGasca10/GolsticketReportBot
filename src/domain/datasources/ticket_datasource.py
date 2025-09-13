from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from uuid import UUID
from src.domain.entities.entities import Ticket

class ITicketDatasource(ABC):
    @abstractmethod
    def agregar(self, ticket: Ticket, propietario_id: UUID) -> None:
        pass

    @abstractmethod
    def obtener_por_rango_fechas_y_usuario(self, usuario_id: UUID, fecha_inicio: datetime, fecha_fin: datetime) -> List[Ticket]:
        pass
    
    @abstractmethod
    def eliminar_por_id(self, ticket_id: UUID) -> bool:
        """Elimina un ticket por su UUID y devuelve True si tuvo éxito."""
        pass
    
     
    @abstractmethod
    def obtener_todos_por_usuario_id(self, usuario_id: UUID) -> List[Ticket]:
        """Obtiene el historial completo de tickets para un usuario específico."""
        pass