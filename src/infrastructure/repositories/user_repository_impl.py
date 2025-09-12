from typing import Optional
from src.domain.entities.entities import Usuario
from src.domain.repositories.user_repository import IUsuarioRepository
from src.domain.datasources.user_datasource import IUsuarioDatasource

class UsuarioRepositoryImpl(IUsuarioRepository):
    def __init__(self, datasource: IUsuarioDatasource):
        self.datasource = datasource

    def agregar(self, usuario: Usuario) -> None:
        self.datasource.agregar(usuario)

    def obtener_por_telegram_id(self, telegram_user_id: int) -> Optional[Usuario]:
        return self.datasource.obtener_por_telegram_id(telegram_user_id)