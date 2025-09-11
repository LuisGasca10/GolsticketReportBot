from typing import List
from datetime import datetime
from app.domain.entities.entities import Ticket
from app.domain.datasources.ticket_datasource import ITicketDatasource
from app.infrastructure.models.ticket_model import TicketModel, SessionLocal


class TicketLocalDatasource(ITicketDatasource):
    def agregar(self, ticket: Ticket) -> None:
        with SessionLocal() as db:
            ticket_db = TicketModel.from_entity(ticket)
            db.add(ticket_db)
            db.commit()

    def obtener_por_rango_fechas(self, user_id: int, fecha_inicio: datetime, fecha_fin: datetime) -> List[Ticket]:
        with SessionLocal() as db:
            tickets_db = db.query(TicketModel).filter(
                TicketModel.user_id == user_id, # <-- Filtro por ID de usuario
                TicketModel.fecha >= fecha_inicio,
                TicketModel.fecha <= fecha_fin
            ).all()
            return [t.to_entity() for t in tickets_db]