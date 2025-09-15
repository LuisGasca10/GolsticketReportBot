import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.domain.entities.entities import Ticket, Usuario
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    nombre_completo = Column(String, nullable=False)
    tickets = relationship("TicketModel", back_populates="propietario")

    def to_entity(self) -> Usuario:
        return Usuario(**{c.name: getattr(self, c.name) for c in self.__table__.columns})

    @staticmethod
    def from_entity(usuario: Usuario) -> "UsuarioModel":
        # uuid.uuid4() will be handled by the database default
        return UsuarioModel(id=usuario.id, telegram_user_id=usuario.telegram_user_id, nombre_completo=usuario.nombre_completo)

class TicketModel(Base):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    propietario = relationship("UsuarioModel", back_populates="tickets")
    
    # Mantenemos el user_id de telegram para referencia, aunque la relación es por usuario_id
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    numero_ticket = Column(String, nullable=False)
    servicio = Column(String, nullable=False)
    usuario_reporta = Column(String, nullable=False)
    correo_usuario = Column(String, nullable=False)
    empresa = Column(String, nullable=False)
    atendido_por = Column(String, nullable=False)

    def to_entity(self) -> Ticket:
        # Excluimos usuario_id y propietario del mapeo directo
        return Ticket(
            id=self.id, user_id=self.user_id, chat_id=self.chat_id, fecha=self.fecha,
            numero_ticket=self.numero_ticket, servicio=self.servicio, usuario_reporta=self.usuario_reporta,
            correo_usuario=self.correo_usuario, empresa=self.empresa, atendido_por=self.atendido_por
        )

    @staticmethod
    def from_entity(ticket: Ticket) -> "TicketModel":
        return TicketModel(
            id=ticket.id, user_id=ticket.user_id, chat_id=ticket.chat_id, fecha=ticket.fecha,
            numero_ticket=ticket.numero_ticket, servicio=ticket.servicio, usuario_reporta=ticket.usuario_reporta,
            correo_usuario=ticket.correo_usuario, empresa=ticket.empresa, atendido_por=ticket.atendido_por
        )

Base.metadata.create_all(bind=engine)