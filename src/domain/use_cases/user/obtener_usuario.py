# src/domain/use_cases/obtener_usuario.py
from typing import Optional
from src.domain.entities.entities import Usuario
from src.domain.repositories.user_repository import IUsuarioRepository

class ObtenerUsuarioUseCase:
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def ejecutar(self, telegram_user_id: int) -> Optional[Usuario]:
        return self.repository.obtener_por_telegram_id(telegram_user_id)