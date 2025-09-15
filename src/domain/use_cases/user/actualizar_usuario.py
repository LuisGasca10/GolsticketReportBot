from src.domain.repositories.user_repository import IUsuarioRepository
from src.domain.entities.entities import Usuario

class EditarUsuarioUseCase:
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def ejecutar(self, telegram_user_id: int, nuevo_nombre_completo: str) -> Usuario:
        # 1. Obtenemos el usuario actual de la base de datos
        usuario_actual = self.repository.obtener_por_telegram_id(telegram_user_id)
        if not usuario_actual:
            raise ValueError("No estás registrado. Usa /registrar primero.")
        
        # 2. Modificamos el atributo que queremos cambiar
        usuario_actual.nombre_completo = nuevo_nombre_completo
        
        # 3. Llamamos al repositorio para que guarde los cambios
        usuario_actualizado = self.repository.actualizar(usuario_actual)
        
        return usuario_actualizado
