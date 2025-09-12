from typing import List
from datetime import datetime
from uuid import UUID
from app.domain.entities.entities import Ticket
from app.domain.datasources.ticket_datasource import ITicketDatasource
from app.infrastructure.models.ticket_model import TicketModel, SessionLocal

class TicketLocalDatasource(ITicketDatasource):
    def agregar(self, ticket: Ticket, propietario_id: UUID) -> None:
        with SessionLocal() as db:
            ticket_db = TicketModel.from_entity(ticket)
            ticket_db.usuario_id = propietario_id
            db.add(ticket_db)
            db.commit()

    def obtener_por_rango_fechas_y_usuario(self, usuario_id: UUID, fecha_inicio: datetime, fecha_fin: datetime) -> List[Ticket]:
        with SessionLocal() as db:
            # --- CORRECCIÓN CLAVE: FILTRO CORRECTO ---
            # Ahora la consulta filtra por la llave foránea 'usuario_id'
            tickets_db = db.query(TicketModel).filter(
                TicketModel.usuario_id == usuario_id,
                TicketModel.fecha >= fecha_inicio,
                TicketModel.fecha <= fecha_fin
            ).all()
            return [t.to_entity() for t in tickets_db]
