from typing import Optional
from src.domain.entities.entities import Usuario
from src.domain.datasources.user_datasource import IUsuarioDatasource
from src.infrastructure.models.ticket_model import UsuarioModel, SessionLocal

class UsuarioSQLDatasource(IUsuarioDatasource):
    def agregar(self, usuario: Usuario) -> None:
        with SessionLocal() as db:
            usuario_db = UsuarioModel.from_entity(usuario)
            db.add(usuario_db)
            db.commit()

    def obtener_por_telegram_id(self, telegram_user_id: int) -> Optional[Usuario]:
        with SessionLocal() as db:
            usuario_db = db.query(UsuarioModel).filter(UsuarioModel.telegram_user_id == telegram_user_id).first()
            return usuario_db.to_entity() if usuario_db else None
        
        
    def actualizar(self, usuario: Usuario) -> Usuario:
        with SessionLocal() as db:
            usuario_db = db.query(UsuarioModel).filter(UsuarioModel.telegram_user_id == usuario.telegram_user_id).first()
            if not usuario_db:
                raise ValueError("No se encontró el usuario para actualizar.")
            usuario_db.nombre_completo = usuario.nombre_completo
            db.commit()
            db.refresh(usuario_db)
            
            return usuario_db.to_entity()