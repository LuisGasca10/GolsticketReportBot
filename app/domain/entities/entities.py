# src/domain/entities.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Usuario:
    id: int | None
    telegram_user_id: int
    nombre_completo: str

@dataclass
class Ticket:
    id: int | None
    user_id: int # ID de usuario de Telegram
    chat_id: int
    fecha: datetime
    numero_ticket: str
    servicio: str
    usuario_reporta: str
    correo_usuario: str
    empresa: str
    atendido_por: str 