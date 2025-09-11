# src/domain/use_cases/registrar_usuario.py
from app.domain.entities.entities import Usuario
from app.domain.repositories.user_repository import IUsuarioRepository

class RegistrarUsuarioUseCase:
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def ejecutar(self, telegram_user_id: int, nombre_completo: str):
        usuario_existente = self.repository.obtener_por_telegram_id(telegram_user_id)
        if usuario_existente:
            raise ValueError("Este usuario de Telegram ya está registrado.")
            
        usuario = Usuario(id=None, telegram_user_id=telegram_user_id, nombre_completo=nombre_completo)
        self.repository.agregar(usuario)