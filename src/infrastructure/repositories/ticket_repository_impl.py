from typing import List
from datetime import datetime
from uuid import UUID
from src.domain.entities.entities import Ticket
from src.domain.repositories.ticket_repository import ITicketRepository
from src.domain.datasources.ticket_datasource import ITicketDatasource

class TicketRepositoryImpl(ITicketRepository):
    def __init__(self, datasource: ITicketDatasource):
        self.datasource = datasource

    def agregar(self, ticket: Ticket, propietario_id: UUID) -> None:
        self.datasource.agregar(ticket, propietario_id)

    def obtener_por_rango_fechas_y_usuario(self, usuario_id: UUID, fecha_inicio: datetime, fecha_fin: datetime) -> List[Ticket]:
        return self.datasource.obtener_por_rango_fechas_y_usuario(usuario_id, fecha_inicio, fecha_fin)
    
    def eliminar_por_id(self,ticket_id: UUID):
       return self.datasource.eliminar_por_id(ticket_id)
   
    def obtener_todos_por_usuario_id(self, usuario_id: UUID) -> List[Ticket]:
        return self.datasource.obtener_todos_por_usuario_id(usuario_id)