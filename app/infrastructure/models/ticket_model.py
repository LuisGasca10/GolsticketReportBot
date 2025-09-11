# src/infrastructure/models/ticket_model.py
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from app.domain.entities.entities import Ticket, Usuario

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- NUEVO MODELO DE USUARIO ---
class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    nombre_completo = Column(String, nullable=False)

    def to_entity(self) -> Usuario:
        return Usuario(**{c.name: getattr(self, c.name) for c in self.__table__.columns})

    @staticmethod
    def from_entity(usuario: Usuario) -> "UsuarioModel":
        return UsuarioModel(**usuario.__dict__)

# --- MODELO DE TICKET MODIFICADO ---
class TicketModel(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True) # Renombrado para claridad
    chat_id = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    numero_ticket = Column(String, nullable=False)
    servicio = Column(String, nullable=False)
    usuario_reporta = Column(String, nullable=False)
    correo_usuario = Column(String, nullable=False)
    empresa = Column(String, nullable=False)
    atendido_por = Column(String, nullable=False) # <-- NUEVO CAMPO

    def to_entity(self) -> Ticket:
        return Ticket(**{c.name: getattr(self, c.name) for c in self.__table__.columns})

    @staticmethod
    def from_entity(ticket: Ticket) -> "TicketModel":
        return TicketModel(**ticket.__dict__)

# Crea ambas tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)