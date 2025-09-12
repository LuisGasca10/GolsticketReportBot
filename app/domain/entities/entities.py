# src/domain/entities.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Usuario:
    id: UUID | None
    telegram_user_id: int
    nombre_completo: str

@dataclass
class Ticket:
    id: UUID | None
    user_id: int # ID de usuario de Telegram
    chat_id: int
    fecha: datetime
    numero_ticket: str
    servicio: str
    usuario_reporta: str
    correo_usuario: str
    empresa: str
    atendido_por: str 