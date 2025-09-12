from typing import Optional
from app.domain.entities.entities import Usuario
from app.domain.repositories.user_repository import IUsuarioRepository
from app.domain.datasources.user_datasource import IUsuarioDatasource

class UsuarioRepositoryImpl(IUsuarioRepository):
    def __init__(self, datasource: IUsuarioDatasource):
        self.datasource = datasource

    def agregar(self, usuario: Usuario) -> None:
        self.datasource.agregar(usuario)

    def obtener_por_telegram_id(self, telegram_user_id: int) -> Optional[Usuario]:
        return self.datasource.obtener_por_telegram_id(telegram_user_id)