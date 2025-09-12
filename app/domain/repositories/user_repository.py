from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.entities import Usuario

class IUsuarioRepository(ABC):
    @abstractmethod
    def agregar(self, usuario: Usuario) -> None:
        pass

    @abstractmethod
    def obtener_por_telegram_id(self, telegram_user_id: int) -> Optional[Usuario]:
        pass