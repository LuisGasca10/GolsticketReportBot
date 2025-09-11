# src/infrastructure/datasources/usuario_local_datasource.py
from typing import Optional
from app.domain.datasources.user_datasource import IUsuarioDatasource
from app.domain.entities.entities import Usuario

from app.infrastructure.models.ticket_model import UsuarioModel, SessionLocal

class UsuarioLocalDatasource(IUsuarioDatasource):
    def agregar(self, usuario: Usuario) -> None:
        with SessionLocal() as db:
            usuario_db = UsuarioModel.from_entity(usuario)
            db.add(usuario_db)
            db.commit()

    def obtener_por_telegram_id(self, telegram_user_id: int) -> Optional[Usuario]:
        with SessionLocal() as db:
            usuario_db = db.query(UsuarioModel).filter(UsuarioModel.telegram_user_id == telegram_user_id).first()
            return usuario_db.to_entity() if usuario_db else None