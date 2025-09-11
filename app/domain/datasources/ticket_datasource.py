# src/domain/datasources/ticket_datasource.py
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from app.domain.entities.entities import Ticket

class ITicketDatasource(ABC):
    @abstractmethod
    def agregar(self, ticket: Ticket) -> None:
        pass

    @abstractmethod
    def obtener_por_rango_fechas(self, chat_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> List[Ticket]:
        pass