from typing import List
from datetime import datetime
from uuid import UUID
from src.domain.entities.entities import Ticket
from src.domain.datasources.ticket_datasource import ITicketDatasource
from src.infrastructure.models.ticket_model import TicketModel, SessionLocal

class TicketSQLDatasource(ITicketDatasource):
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
        
    def eliminar_por_id(self, ticket_id: UUID) -> bool:
        with SessionLocal() as db:
        # Buscamos el ticket por su UUID (que es la llave primaria 'id')
            ticket_a_eliminar = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
            if ticket_a_eliminar:
                db.delete(ticket_a_eliminar)
                db.commit()
                return True # Éxito
            return False # No se encontró el ticket
        
    def obtener_todos_por_usuario_id(self, usuario_id: UUID) -> List[Ticket]:
        with SessionLocal() as db:
            # La consulta ahora solo filtra por el ID del usuario
            tickets_db = db.query(TicketModel).filter(
                TicketModel.usuario_id == usuario_id
            ).order_by(TicketModel.fecha.desc()).all() # Ordenamos por fecha descendente
            return [t.to_entity() for t in tickets_db]
        
