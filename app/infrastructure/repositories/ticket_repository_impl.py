from typing import List
from datetime import datetime
from app.domain.entities.entities import Ticket
from app.domain.repositories.ticket_repository import ITicketRepository
from app.domain.datasources.ticket_datasource import ITicketDatasource

class TicketRepositoryImpl(ITicketRepository):
    def __init__(self, datasource: ITicketDatasource):
        self.datasource = datasource

    def agregar(self, ticket: Ticket) -> None:
        self.datasource.agregar(ticket)

    def obtener_por_rango_fechas(self, chat_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> List[Ticket]:
        return self.datasource.obtener_por_rango_fechas(chat_id, fecha_inicio, fecha_fin)